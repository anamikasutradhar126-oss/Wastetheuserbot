"""Voice-chat AI talk mode.

This module is intentionally optional: the rest of the userbot still starts if a
PyTgCalls build does not expose incoming stream-frame callbacks.  When supported,
.vctalk on starts listening on the VC already joined by the connected account,
transcribes short speech chunks with Groq, generates a reply, synthesizes it with
edge-tts, and plays the reply back into that same VC.
"""
import asyncio
import io
import os
import wave
import uuid
import logging
from pathlib import Path

import aiohttp
from pyrogram import Client, filters
from pytgcalls.types import GroupCallConfig

from config import GROQ_API_KEY, GROQ_MODEL
from Waste.modules.help import add_command_help
from Waste.modules.basic.vcfight import _bridge, _states, _key, _subscription_active

log = logging.getLogger(__name__)
TALK_DIR = Path("vctalk_cache")
TALK_DIR.mkdir(exist_ok=True)

try:
    from pytgcalls import filters as call_filters
    from pytgcalls.types import Direction, Device, StreamFrames, RecordStream
    from pytgcalls.types.raw import AudioParameters
    _VC_API_OK = True
except Exception as exc:  # pragma: no cover - depends on installed PyTgCalls build
    _VC_API_OK = False
    call_filters = None
    Direction = Device = StreamFrames = RecordStream = AudioParameters = None
    log.warning("VC Talk disabled: incoming PyTgCalls stream API unavailable: %s", exc)

_talk_enabled = {}
_talk_buffers = {}
_talk_tasks = {}
_talk_locks = {}


def _owner_key(client):
    return getattr(client, "_waste_owner_uid", None) or id(client)


def _enabled(client, chat_id):
    return bool(_talk_enabled.get((_owner_key(client), int(chat_id)), False))


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
            {"role": "system", "content": "You are a concise friendly voice-chat assistant. Reply naturally in the same language as the speaker. Keep replies short enough for voice."},
            {"role": "user", "content": text[:1500]},
        ],
        "temperature": 0.7,
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
        communicate = edge_tts.Communicate(text[:700], "en-US-AriaNeural")
        await communicate.save(str(path))
        return str(path)
    except Exception as exc:
        log.warning("VC TTS failed: %s", exc)
        return None


async def _reply_pipeline(client, chat_id, pcm):
    path = None
    try:
        text = await _transcribe(_pcm_to_wav(pcm))
        if not text or len(text.strip()) < 2:
            return
        answer = await _ask(text)
        if not answer:
            return
        path = await _tts(answer)
        if not path:
            return
        state, call = await _bridge(client)
        if not _enabled(client, chat_id):
            return
        await call.play(chat_id, path, config=GroupCallConfig(auto_start=False))
        await asyncio.sleep(1)
    except Exception as exc:
        log.warning("VC Talk pipeline failed: %s", type(exc).__name__)
    finally:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


def _register_stream_callback(client, call):
    """Register the stream-frame callback on the PyTgCalls instance.

    py-tgcalls 2.x expects stream_frame filters to be passed to
    PyTgCalls.on_update(), not to Pyrogram Client.on_message().
    """
    if getattr(call, "_waste_vctalk_registered", False):
        return
    if not _VC_API_OK:
        return
    try:
        decorator = call.on_update(
            call_filters.stream_frame(Direction.INCOMING, Device.MICROPHONE)
        )
        decorator(_incoming_audio)
        setattr(call, "_waste_vctalk_registered", True)
    except Exception as exc:
        log.warning("Could not register VC Talk stream callback: %s", exc)
        raise


async def _start_recording(client, chat_id):
    if not _VC_API_OK:
        raise RuntimeError("Installed PyTgCalls version has no incoming stream callback API")
    state, call = await _bridge(client)
    # RecordStream enables incoming audio frames for the callback API.  The
    # callback below only buffers short chunks; it does not store recordings.
    params = AudioParameters(bitrate=48000, channels=2)
    try:
        await call.record(chat_id, RecordStream(True, params), GroupCallConfig(auto_start=False))
    except TypeError:
        await call.record(chat_id, RecordStream(True, params))


async def _stop_recording(client, chat_id):
    try:
        _, call = await _bridge(client)
        stop = getattr(call, "stop", None)
        if stop:
            await stop(chat_id)
    except Exception:
        pass


if _VC_API_OK:
    @Client.on_message(filters.command("vctalk", [".", "/"]) & filters.me)
    async def vctalk_command(client, message):
        action = (message.command[1].lower() if len(message.command) > 1 else "status")
        chat_id = message.chat.id if message.chat else None
        if not chat_id:
            return await message.reply("❌ Use `.vctalk on` inside the group whose VC you want to use.")
        state, _ = await _bridge(client)
        if action == "on":
            if chat_id not in state.joined:
                return await message.reply("❌ Connected ID is not in this VC. Use `.join <group_id>` first.")
            _talk_enabled[(_owner_key(client), int(chat_id))] = True
            _talk_buffers.setdefault((_owner_key(client), int(chat_id)), bytearray())
            try:
                await _start_recording(client, chat_id)
            except Exception as exc:
                _talk_enabled.pop((_owner_key(client), int(chat_id)), None)
                return await message.reply(f"❌ VC Talk could not start: `{type(exc).__name__}`")
            return await message.reply("🟢 **VC Talk ON**\nConnected ID will listen and answer in this VC.")
        if action == "off":
            _talk_enabled.pop((_owner_key(client), int(chat_id)), None)
            _talk_buffers.pop((_owner_key(client), int(chat_id)), None)
            await _stop_recording(client, chat_id)
            return await message.reply("🔴 **VC Talk OFF**")
        return await message.reply(f"🎙️ **VC Talk:** {'🟢 ON' if _enabled(client, chat_id) else '🔴 OFF'}")

    async def _incoming_audio(client, update: StreamFrames):
        # PyTgCalls dispatches stream updates to this callback.  Keep a small
        # rolling chunk so normal conversation can be transcribed without
        # retaining a long recording.
        chat_id = int(update.chat_id)
        if not _enabled(client, chat_id):
            return
        key = (_owner_key(client), chat_id)
        buf = _talk_buffers.setdefault(key, bytearray())
        for frame_data in getattr(update, "frames", []) or []:
            frame = getattr(frame_data, "frame", b"")
            if frame:
                buf.extend(frame)
        # ~3 seconds of stereo 48kHz PCM16 is enough for a short utterance.
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
        asyncio.create_task(run())
else:
    @Client.on_message(filters.command("vctalk", [".", "/"]) & filters.me)
    async def vctalk_unavailable(client, message):
        await message.reply("❌ VC Talk needs a PyTgCalls build with incoming stream-frame support. Music/VC join remains available.")


add_command_help("VcTalk", [
    ["vctalk on", "Enable AI voice conversation in the current VC. The connected ID listens and answers there."],
    ["vctalk off", "Disable AI voice conversation in the current VC."],
    ["vctalk status", "Show VC Talk status for the current group."],
])
