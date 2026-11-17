"""AI Voice Chat for the connected /add userbot account.

Commands:
    .vctalk on              -> enable for every VC currently joined by this ID
    .vctalk off             -> disable all VC Talk sessions
    .vctalk on <chat_id>    -> enable only in that VC (joins it if needed)
    .vctalk off <chat_id>   -> disable only that VC
    .vctalk status          -> show status

The connected account from /add is used; no extra STRING_SESSION is required.
"""
import asyncio
import io
import logging
import os
import uuid
import wave
from pathlib import Path

import aiohttp
from pyrogram import Client, filters
from pytgcalls.types import GroupCallConfig

from config import GROQ_API_KEY, GROQ_MODEL
from Waste.modules.help import add_command_help
from Waste.modules.basic.vcfight import _bridge, _states, _key, _join

log = logging.getLogger(__name__)
TALK_DIR = Path("vctalk_cache")
TALK_DIR.mkdir(exist_ok=True)

TTS_VOICE = os.getenv("TTS_VOICE", "hi-IN-SwaraNeural")
TTS_RATE = os.getenv("TTS_RATE", "-12%")
TTS_PITCH = os.getenv("TTS_PITCH", "+5Hz")

try:
    from pytgcalls import filters as call_filters
    from pytgcalls.types import Direction, Device, StreamFrames, RecordStream
    from pytgcalls.types.raw import AudioParameters
    _VC_API_OK = True
except Exception as exc:  # pragma: no cover - depends on installed py-tgcalls build
    _VC_API_OK = False
    call_filters = None
    Direction = Device = StreamFrames = RecordStream = AudioParameters = None
    log.warning("VC Talk disabled: incoming PyTgCalls stream API unavailable: %s", exc)

_talk_global = {}
_talk_enabled = {}          # (client key, chat_id) -> bool
_talk_buffers = {}          # (client key, chat_id) -> bytearray
_talk_tasks = {}
_talk_locks = {}
_talk_recording = set()
_talk_busy = set()
_talk_watchers = {}


def _owner_key(client):
    return getattr(client, "_waste_owner_uid", None) or id(client)


def _key2(client, chat_id):
    return (_owner_key(client), int(chat_id))


def _enabled(client, chat_id):
    key = _key2(client, chat_id)
    return bool(_talk_enabled.get(key, False) or _talk_global.get(_owner_key(client), False))


def _pcm_to_wav(pcm: bytes) -> bytes:
    out = io.BytesIO()
    with wave.open(out, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(48000)
        wf.writeframes(pcm)
    return out.getvalue()


async def _transcribe(wav_bytes: bytes):
    if not GROQ_API_KEY:
        return ""
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    form = aiohttp.FormData()
    form.add_field("file", wav_bytes, filename="vc.wav", content_type="audio/wav")
    form.add_field("model", "whisper-large-v3-turbo")
    form.add_field("response_format", "json")
    timeout = aiohttp.ClientTimeout(total=45)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, headers=headers, data=form) as resp:
            data = await resp.json(content_type=None)
            if resp.status != 200:
                log.warning("VC transcription failed: %s", data)
                return ""
            return str(data.get("text", "")).strip()


async def _ask(text: str):
    if not GROQ_API_KEY:
        return ""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": (
                "You are a friendly natural Telegram voice-chat participant. "
                "Reply in the same language and tone as the speaker. If they use Hinglish, "
                "reply in Roman Hinglish. Keep the spoken reply short, natural and conversational; "
                "usually one sentence, at most two. Do not use lists or fancy Unicode."
            )},
            {"role": "user", "content": text[:1500]},
        ],
        "temperature": 0.75,
        "max_tokens": 160,
    }
    timeout = aiohttp.ClientTimeout(total=45)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json(content_type=None)
            if resp.status != 200:
                log.warning("VC AI failed: %s", data)
                return ""
            return str(data.get("choices", [{}])[0].get("message", {}).get("content", "")).strip()


async def _tts(text: str):
    try:
        import edge_tts
        path = TALK_DIR / f"reply_{uuid.uuid4().hex}.mp3"
        communicate = edge_tts.Communicate(
            text[:700], TTS_VOICE,
            rate=TTS_RATE,
            pitch=TTS_PITCH,
        )
        await communicate.save(str(path))
        return str(path)
    except Exception as exc:
        log.warning("VC TTS failed: %s", exc)
        return None


def _register_stream_callback(user_client, call):
    if getattr(call, "_waste_vctalk_registered", False) or not _VC_API_OK:
        return
    decorator = call.on_update(
        call_filters.stream_frame(Direction.INCOMING, Device.MICROPHONE)
    )

    async def _bound_incoming_audio(call_instance, update):
        await _incoming_audio(user_client, update)

    decorator(_bound_incoming_audio)
    setattr(call, "_waste_vctalk_registered", True)


async def _start_recording(client, chat_id):
    if not _VC_API_OK:
        raise RuntimeError("Installed PyTgCalls build has no incoming stream-frame callback API")
    _, call = await _bridge(client)
    _register_stream_callback(client, call)
    key = _key2(client, chat_id)
    if key in _talk_recording:
        return
    params = AudioParameters(bitrate=48000, channels=2)
    await call.record(int(chat_id), RecordStream(True, params))
    _talk_recording.add(key)
    _talk_buffers.setdefault(key, bytearray())


async def _stop_recording(client, chat_id):
    key = _key2(client, chat_id)
    _talk_recording.discard(key)
    _talk_buffers.pop(key, None)
    try:
        _, call = await _bridge(client)
        stop = getattr(call, "stop", None)
        if stop:
            await stop(int(chat_id))
    except Exception:
        pass


async def _reply_pipeline(client, chat_id, pcm):
    key = _key2(client, chat_id)
    path = None
    try:
        text = await _transcribe(_pcm_to_wav(pcm))
        if not text or len(text.strip()) < 2:
            return
        # Ignore obvious command fragments and empty/noise transcripts.
        if text.strip().startswith((".", "/", "!")):
            return
        answer = await _ask(text)
        if not answer:
            return
        path = await _tts(answer)
        if not path or not _enabled(client, chat_id):
            return
        _talk_busy.add(key)
        _, call = await _bridge(client)
        await call.play(int(chat_id), path, config=GroupCallConfig(auto_start=False))
        # Give the recorder time to ignore the bot's own TTS audio.
        await asyncio.sleep(max(1.0, min(8.0, len(answer) / 8.0)))
    except Exception as exc:
        log.warning("VC Talk pipeline failed: %s", type(exc).__name__)
    finally:
        _talk_busy.discard(key)
        if path:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass


async def _incoming_audio(client, update: StreamFrames):
    chat_id = int(getattr(update, "chat_id", 0) or 0)
    if not chat_id or not _enabled(client, chat_id):
        return
    key = _key2(client, chat_id)
    if key in _talk_busy:
        return
    buf = _talk_buffers.setdefault(key, bytearray())
    for frame_data in getattr(update, "frames", []) or []:
        frame = getattr(frame_data, "frame", b"")
        if frame:
            buf.extend(frame)
    # About three seconds of 48 kHz stereo PCM16.
    if len(buf) < 48000 * 2 * 2 * 3:
        return
    pcm = bytes(buf)
    del buf[:]
    lock = _talk_locks.setdefault(key, asyncio.Lock())
    if lock.locked():
        return

    async def run():
        async with lock:
            await _reply_pipeline(client, chat_id, pcm)

    task = asyncio.create_task(run())
    _talk_tasks[key] = task


async def _start_for_joined(client, chat_id):
    try:
        await _start_recording(client, int(chat_id))
        return None
    except Exception as exc:
        return f"{type(exc).__name__}: {str(exc)[:120]}"


async def _watch_global(client):
    """Keep global VC Talk attached to every VC the connected ID is already in."""
    owner = _owner_key(client)
    await asyncio.sleep(3)
    while _talk_global.get(owner, False):
        try:
            state = _states.get(_key(client))
            joined = list(state.joined) if state else []
            for chat_id in joined:
                if not _enabled(client, chat_id):
                    continue
                if _key2(client, chat_id) not in _talk_recording:
                    err = await _start_for_joined(client, chat_id)
                    if err:
                        log.debug("VC Talk auto-start %s: %s", chat_id, err)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.debug("VC Talk watcher failed: %s", type(exc).__name__)
        await asyncio.sleep(15)


def _ensure_global_watcher(client):
    owner = _owner_key(client)
    task = _talk_watchers.get(owner)
    if task and not task.done():
        return
    _talk_watchers[owner] = asyncio.create_task(_watch_global(client))


async def start_background_for_client(client):
    """Called after /add session restore; resumes a saved global VC Talk setting."""
    try:
        from Waste.modules.bot.start import settings_col
        uid = getattr(client, "_waste_owner_uid", None)
        if not uid:
            return
        doc = settings_col.find_one({"_id": int(uid)}) or {}
        if doc.get("vctalk_global"):
            _talk_global[_owner_key(client)] = True
            _ensure_global_watcher(client)
    except Exception as exc:
        log.debug("VC Talk background restore skipped: %s", type(exc).__name__)


async def _save_global_setting(client, enabled):
    try:
        from Waste.modules.bot.start import settings_col
        uid = getattr(client, "_waste_owner_uid", None)
        if uid:
            settings_col.update_one({"_id": int(uid)}, {"$set": {"vctalk_global": bool(enabled)}}, upsert=True)
    except Exception:
        pass


if _VC_API_OK:
    @Client.on_message(filters.command("vctalk", [".", "/"]) & filters.me)
    async def vctalk_command(client, message):
        args = message.command[1:] if len(message.command) > 1 else []
        action = args[0].lower() if args else "status"
        target = None
        if len(args) > 1 and args[1].lstrip("-").isdigit():
            target = int(args[1])

        if action == "on":
            if target is None:
                _talk_global[_owner_key(client)] = True
                await _save_global_setting(client, True)
                _ensure_global_watcher(client)
                state = _states.get(_key(client))
                joined = list(state.joined) if state else []
                started = 0
                for cid in joined:
                    if await _start_for_joined(client, cid) is None:
                        started += 1
                if not joined:
                    return await message.reply("🟢 **VC Talk ON**\nAb connected ID jis VC mein joined hai, un sab mein AI voice talk active rahega. Naya joined VC bhi automatically cover hoga.")
                return await message.reply(f"🟢 **VC Talk ON**\nActive VCs: `{started}`\nTargeted use: `.vctalk on <chat_id>`")

            try:
                await _join(client, target)
            except Exception as exc:
                return await message.reply(f"❌ Connected ID could not join this VC: `{type(exc).__name__}`")
            _talk_enabled[_key2(client, target)] = True
            err = await _start_for_joined(client, target)
            if err:
                _talk_enabled.pop(_key2(client, target), None)
                return await message.reply(f"❌ VC Talk could not start: `{err}`")
            return await message.reply(f"🟢 **VC Talk ON**\nOnly VC `{target}` is enabled.")

        if action == "off":
            if target is None:
                _talk_global[_owner_key(client)] = False
                await _save_global_setting(client, False)
                state = _states.get(_key(client))
                joined = list(state.joined) if state else []
                for cid in joined:
                    _talk_enabled.pop(_key2(client, cid), None)
                    await _stop_recording(client, cid)
                task = _talk_watchers.pop(_owner_key(client), None)
                if task and not task.done():
                    task.cancel()
                return await message.reply("🔴 **VC Talk OFF**\nAI voice talk disabled for all VCs.")

            _talk_enabled.pop(_key2(client, target), None)
            await _stop_recording(client, target)
            return await message.reply(f"🔴 **VC Talk OFF**\nOnly VC `{target}` disabled.")

        state = _states.get(_key(client))
        joined = list(state.joined) if state else []
        active = [str(cid) for cid in joined if _enabled(client, cid)]
        return await message.reply(
            f"🎙 **VC Talk:** {'🟢 ON' if (_talk_global.get(_owner_key(client), False) or active) else '🔴 OFF'}\n"
            f"Active VCs: {', '.join(active) if active else 'none'}\n"
            f"Use `.vctalk on`, `.vctalk off`, or `.vctalk on <chat_id>`."
        )
else:
    @Client.on_message(filters.command("vctalk", [".", "/"]) & filters.me)
    async def vctalk_unavailable(client, message):
        await message.reply("❌ VC Talk needs a PyTgCalls build with incoming stream-frame support. Music/VC join remains available.")


add_command_help("VcTalk", [
    ["vctalk on", "Enable AI voice conversation in every VC currently joined by the connected ID; newly joined VCs are picked up automatically."],
    ["vctalk off", "Disable AI voice conversation in all VCs."],
    ["vctalk on <chat_id>", "Enable AI voice conversation only in the specified VC; the connected ID joins it if necessary."],
    ["vctalk off <chat_id>", "Disable AI voice conversation only in the specified VC."],
    ["vctalk status", "Show active VC Talk sessions."],
])
