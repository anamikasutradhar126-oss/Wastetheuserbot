"""AI Voice Chat for the connected /add userbot account.

The connected account from /add is used; no extra STRING_SESSION is required.
VC speech is transcribed with Groq, answered through a fast provider fallback
(Groq -> Gemini -> OpenRouter -> Claude), and spoken with automatic
Hindi/Bengali/English voice selection. TTS fallbacks include Edge, Sarvam and
Gemini where configured.
"""
import asyncio
import base64
import io
import json
import logging
import os
import re
import uuid
import wave
from pathlib import Path

import aiohttp
from pyrogram import Client, filters
from pytgcalls import filters as tgcall_filters
from pytgcalls.types import Device, Direction, GroupCallConfig

from config import GROQ_API_KEY, GROQ_MODEL
from Waste.modules.help import add_command_help
from Waste.modules.basic.vcfight import _bridge, _states, _key, _join

log = logging.getLogger(__name__)
TALK_DIR = Path("vctalk_cache")
TALK_DIR.mkdir(exist_ok=True)

TTS_VOICE = os.getenv("TTS_VOICE", "hi-IN-SwaraNeural")
TTS_RATE = os.getenv("TTS_RATE", "-8%")
TTS_PITCH = os.getenv("TTS_PITCH", "+2Hz")
TTS_VOICE_EN = os.getenv("TTS_VOICE_EN", "en-IN-NeerjaNeural")
TTS_VOICE_BN = os.getenv("TTS_VOICE_BN", "bn-IN-TanishaaNeural")
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "auto").strip().lower() or "auto"

_GEM_KEYS = [k.strip() for k in re.split(r"[,\s]+", os.getenv("GEMINI_API_KEY", "")) if k.strip()]
_OR_KEYS = [k.strip() for k in re.split(r"[,\s]+", os.getenv("OPENROUTER_API_KEY", "")) if k.strip()]
_CL_KEYS = [k.strip() for k in re.split(r"[,\s]+", os.getenv("ANTHROPIC_API_KEY", "") or os.getenv("CLAUDE_API_KEY", "")) if k.strip()]
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
GEM_TTS = os.getenv("GEM_TTS", "1") != "0"
GEM_TTS_MODEL = os.getenv("GEM_TTS_MODEL", "gemini-2.5-flash-preview-tts")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_MODEL = os.getenv("SARVAM_MODEL", "bulbul:v4-flash")
SARVAM_SPEAKER = os.getenv("SARVAM_SPEAKER", "ritu_hi_social_lively")

try:
    # Keep imports limited to the recording primitives actually needed by
    # VcTalk.  Some py-tgcalls builds do not expose the optional filter/
    # Direction/Device names even though the generic on_update API works.
    from pytgcalls.types import RecordStream
    try:
        from pytgcalls.types.raw import AudioParameters
    except Exception:
        AudioParameters = None
    _VC_API_OK = RecordStream is not None
except Exception as exc:
    _VC_API_OK = False
    RecordStream = AudioParameters = None
    log.warning("VC Talk disabled: PyTgCalls recording API unavailable: %s", exc)

_talk_global = {}
_talk_enabled = {}
_talk_buffers = {}
_talk_tasks = {}
_talk_locks = {}
_talk_recording = set()
_talk_busy = set()
_talk_watchers = {}
_talk_vad = {}
VAD_RMS = float(os.getenv("VCTALK_VAD_RMS", "450"))
VAD_SILENCE = float(os.getenv("VCTALK_VAD_SILENCE", "0.55"))
VAD_MAX = float(os.getenv("VCTALK_VAD_MAX", "8.0"))
VAD_MIN_VOICE = float(os.getenv("VCTALK_VAD_MIN_VOICE", "0.25"))


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


def _language(text: str) -> str:
    """Return hi/bn/en using the reply text, with a small Hinglish hint."""
    t = text or ""
    if re.search(r"[\u0980-\u09ff]", t):
        return "bn"
    if re.search(r"[\u0900-\u097f]", t):
        return "hi"
    words = set(re.findall(r"[a-zA-Z]+", t.lower()))
    hindi = {"hai", "hain", "ho", "hoga", "kya", "kyun", "kaise", "kaisa", "tum", "aap", "mujhe", "mera", "meri", "yeh", "yah", "woh", "kahan", "kab", "nahi", "nahin", "acha", "accha", "batao", "bolo", "kar", "raha", "rahi", "sakta", "sakti", "chalo", "theek", "thik"}
    if len(words & hindi) >= 2:
        return "hi"
    return "en"


def _system_prompt(lang: str) -> str:
    if lang == "bn":
        return ("You are a natural, friendly Telegram voice-chat participant. Reply in Bengali, "
                "using natural spoken Bengali. Keep it short, conversational and easy to speak, "
                "usually one sentence and at most two. Do not use markdown, lists or emojis.")
    if lang == "hi":
        return ("You are a natural, friendly Telegram voice-chat participant. Reply in Hindi or "
                "natural Hinglish matching the speaker. If the speaker uses Roman Hinglish, use "
                "Roman Hinglish; if they use Devanagari Hindi, use Devanagari. Keep it short, "
                "conversational and easy to speak, usually one sentence and at most two. "
                "Do not use markdown, lists or emojis.")
    return ("You are a natural, friendly Telegram voice-chat participant. Reply in English "
            "because the speaker is using English. Keep it short, conversational and easy to "
            "speak, usually one sentence and at most two. Do not use markdown, lists or emojis.")


async def _post_json(url, headers, payload, timeout=20):
    tout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=tout) as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json(content_type=None)
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status}: {str(data)[:180]}")
            return data


async def _transcribe(wav_bytes: bytes):
    if not GROQ_API_KEY:
        return ""
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    form = aiohttp.FormData()
    form.add_field("file", wav_bytes, filename="vc.wav", content_type="audio/wav")
    form.add_field("model", "whisper-large-v3-turbo")
    form.add_field("response_format", "verbose_json")
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, data=form) as resp:
            data = await resp.json(content_type=None)
            if resp.status != 200:
                log.warning("VC transcription failed: %s", str(data)[:220])
                return ""
            text = str(data.get("text", "")).strip()
            # Reject obvious noise/hallucination when verbose_json supplies segments.
            segs = data.get("segments") or []
            if segs:
                good = [s for s in segs if s.get("no_speech_prob", 0) <= 0.5 and s.get("avg_logprob", 0) >= -0.9]
                if not good:
                    return ""
                text = " ".join(str(s.get("text", "")).strip() for s in good).strip()
            return text


async def _ask_groq(text, lang):
    data = await _post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        {"model": GROQ_MODEL, "messages": [{"role": "system", "content": _system_prompt(lang)}, {"role": "user", "content": text[:1500]}], "temperature": 0.65, "max_tokens": 160}, 18)
    return str(data.get("choices", [{}])[0].get("message", {}).get("content", "")).strip()


async def _ask_gemini(text, lang):
    if not _GEM_KEYS:
        raise RuntimeError("Gemini key missing")
    last = None
    for key in _GEM_KEYS:
        try:
            data = await _post_json(
                "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                {"model": GEMINI_MODEL, "messages": [{"role": "system", "content": _system_prompt(lang)}, {"role": "user", "content": text[:1500]}], "temperature": 0.65, "max_tokens": 160}, 20)
            ans = str(data.get("choices", [{}])[0].get("message", {}).get("content", "")).strip()
            if ans:
                return ans
        except Exception as exc:
            last = exc
    raise last or RuntimeError("Gemini failed")


async def _ask_openrouter(text, lang):
    if not _OR_KEYS:
        raise RuntimeError("OpenRouter key missing")
    models = [OPENROUTER_MODEL, "meta-llama/llama-3.3-70b-instruct:free", "google/gemma-3-27b-it:free", "deepseek/deepseek-chat-v3.1:free"]
    last = None
    for key in _OR_KEYS:
        for model in dict.fromkeys(x for x in models if x):
            try:
                data = await _post_json(
                    "https://openrouter.ai/api/v1/chat/completions",
                    {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "HTTP-Referer": "https://t.me", "X-Title": "WASTE X UBOT VC Talk"},
                    {"model": model, "messages": [{"role": "system", "content": _system_prompt(lang)}, {"role": "user", "content": text[:1500]}], "temperature": 0.65, "max_tokens": 160}, 20)
                ans = str(data.get("choices", [{}])[0].get("message", {}).get("content", "")).strip()
                ans = re.sub(r"<think>.*?(</think>|$)", "", ans, flags=re.S).strip()
                if ans:
                    return ans
            except Exception as exc:
                last = exc
    raise last or RuntimeError("OpenRouter failed")


async def _ask_claude(text, lang):
    if not _CL_KEYS:
        raise RuntimeError("Claude key missing")
    last = None
    for key in _CL_KEYS:
        try:
            data = await _post_json(
                "https://api.anthropic.com/v1/messages",
                {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                {"model": CLAUDE_MODEL, "max_tokens": 160, "system": _system_prompt(lang), "messages": [{"role": "user", "content": text[:1500]}]}, 22)
            ans = "".join(str(x.get("text", "")) for x in (data.get("content") or []) if isinstance(x, dict) and x.get("type") == "text").strip()
            if ans:
                return ans
        except Exception as exc:
            last = exc
    raise last or RuntimeError("Claude failed")


async def _ask(text: str):
    lang = _language(text)
    providers = [
        ("groq", _ask_groq),
        ("gemini", _ask_gemini),
        ("openrouter", _ask_openrouter),
        ("claude", _ask_claude),
    ]
    last = None
    for name, fn in providers:
        try:
            if name == "groq" and not GROQ_API_KEY:
                continue
            answer = await fn(text, lang)
            if answer:
                return answer, lang
        except Exception as exc:
            last = exc
            log.info("VC AI %s unavailable: %s", name, str(exc)[:120])
    if last:
        log.warning("VC AI all providers failed: %s", str(last)[:160])
    return "", lang


def _edge_voice(lang):
    return {"hi": TTS_VOICE, "bn": TTS_VOICE_BN, "en": TTS_VOICE_EN}.get(lang, TTS_VOICE)


async def _edge_tts(text, lang):
    import edge_tts
    path = TALK_DIR / f"reply_{uuid.uuid4().hex}.mp3"
    await edge_tts.Communicate(text[:700], _edge_voice(lang), rate=TTS_RATE, pitch=TTS_PITCH).save(str(path))
    return str(path)


async def _sarvam_tts(text, lang):
    if not SARVAM_API_KEY or lang not in ("hi", "bn"):
        return None
    # Sarvam is used as an Indian-language accelerator/fallback. If the configured
    # speaker/model does not accept the language, Edge remains the final fallback.
    language_code = "hi-IN" if lang == "hi" else "bn-IN"
    payload = {"text": text[:700], "language_code": language_code, "model": SARVAM_MODEL, "speaker": SARVAM_SPEAKER, "pace": 1.05, "temperature": 0.7, "speech_sample_rate": 24000}
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post("https://api.sarvam.ai/text-to-speech", headers={"api-subscription-key": SARVAM_API_KEY, "Content-Type": "application/json"}, json=payload) as resp:
            data = await resp.json(content_type=None)
            if resp.status != 200:
                raise RuntimeError(f"Sarvam HTTP {resp.status}: {str(data)[:120]}")
            raw = base64.b64decode("".join(data.get("audios") or []))
            if len(raw) < 2000:
                raise RuntimeError("Sarvam returned no audio")
    wav = TALK_DIR / f"sarvam_{uuid.uuid4().hex}.wav"
    mp3 = TALK_DIR / f"sarvam_{uuid.uuid4().hex}.mp3"
    wav.write_bytes(raw)
    proc = await asyncio.create_subprocess_exec("ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "64k", str(mp3), stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
    await asyncio.wait_for(proc.wait(), 20)
    try:
        wav.unlink()
    except Exception:
        pass
    if proc.returncode != 0 or not mp3.exists():
        raise RuntimeError("Sarvam audio conversion failed")
    return str(mp3)


async def _gemini_tts(text, lang):
    if not _GEM_KEYS or not GEM_TTS:
        return None
    # Gemini's audio generation is multilingual; the prompt explicitly names the language.
    lang_name = {"hi": "Hindi/Hinglish", "bn": "Bengali", "en": "English"}.get(lang, "English")
    prompt = f"Speak this naturally in {lang_name}, as a friendly Telegram voice-chat reply: {text[:500]}"
    for key in _GEM_KEYS:
        try:
            payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseModalities": ["AUDIO"]}}
            timeout = aiohttp.ClientTimeout(total=25)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(f"https://generativelanguage.googleapis.com/v1beta/models/{GEM_TTS_MODEL}:generateContent", headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=payload) as resp:
                    data = await resp.json(content_type=None)
                    if resp.status != 200:
                        continue
            for part in ((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []:
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    raw = base64.b64decode(inline["data"])
                    if len(raw) > 4000:
                        rate = 24000
                        m = re.search(r"rate=(\d+)", str(inline.get("mimeType") or inline.get("mime_type") or ""))
                        if m:
                            rate = int(m.group(1))
                        wav = TALK_DIR / f"gem_{uuid.uuid4().hex}.pcm"
                        mp3 = TALK_DIR / f"gem_{uuid.uuid4().hex}.mp3"
                        wav.write_bytes(raw)
                        proc = await asyncio.create_subprocess_exec("ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", str(wav), "-ar", "24000", "-c:a", "libmp3lame", "-b:a", "64k", str(mp3), stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                        await asyncio.wait_for(proc.wait(), 20)
                        try: wav.unlink()
                        except Exception: pass
                        if proc.returncode == 0 and mp3.exists():
                            return str(mp3)
        except Exception as exc:
            log.info("Gemini TTS unavailable: %s", str(exc)[:100])
    return None


async def _tts(text: str, lang: str):
    # Fast path: Edge is local HTTP streaming and supports all three target languages.
    # Other engines remain available as fallbacks when configured.
    providers = []
    if TTS_PROVIDER in ("auto", "edge"):
        providers.append(("edge", _edge_tts))
    if TTS_PROVIDER in ("auto", "sarvam") and SARVAM_API_KEY:
        providers.append(("sarvam", _sarvam_tts))
    if TTS_PROVIDER in ("auto", "gemini") and GEM_TTS and _GEM_KEYS:
        providers.append(("gemini", _gemini_tts))
    for name, fn in providers:
        try:
            path = await fn(text, lang)
            if path and os.path.exists(path) and os.path.getsize(path) > 500:
                return path
        except Exception as exc:
            log.info("VC TTS %s unavailable: %s", name, str(exc)[:120])
    return None


def _register_stream_callback(user_client, call):
    # Use the generic PyTgCalls update stream, like the working VC listener
    # implementation.  This avoids depending on the optional stream_frame
    # filter API, which is missing in some py-tgcalls 2.x builds.
    if getattr(call, "_waste_vctalk_registered", False):
        return True
    on_update = getattr(call, "on_update", None)
    if not callable(on_update):
        return False

    # Only consume incoming microphone frames from the VC.  This is the
    # supported PyTgCalls stream-frame path and avoids accidentally feeding
    # the connected account's own outgoing audio back into VcTalk.
    try:
        stream_filter = tgcall_filters.stream_frame(
            Direction.INCOMING,
            Device.MICROPHONE,
        )
    except Exception:
        stream_filter = None

    if stream_filter is not None:
        @on_update(stream_filter)
        async def _bound_update(call_instance, update):
            await _incoming_audio(user_client, update)
    else:
        @on_update()
        async def _bound_update_fallback(call_instance, update):
            if type(update).__name__ != "StreamFrames":
                return
            direction = str(getattr(update, "direction", "")).upper()
            if "OUTGOING" in direction:
                return
            await _incoming_audio(user_client, update)

    setattr(call, "_waste_vctalk_registered", True)
    return True


async def _start_recording(client, chat_id):
    # VcTalk must listen on the connected ID's active VC. If the connected
    # ID has not joined this VC yet, join it first using the existing VC
    # join path instead of creating a separate bot-side call.
    state = _states.get(_key(client))
    if not state or int(chat_id) not in state.joined:
        await _join(client, int(chat_id))
    _, call = await _bridge(client)
    if not _register_stream_callback(client, call):
        raise RuntimeError("Installed PyTgCalls build has no VC update callback API")
    key = _key2(client, chat_id)
    if key in _talk_recording:
        return
    if RecordStream is None:
        raise RuntimeError("Installed PyTgCalls build has no RecordStream API")
    params = AudioParameters(bitrate=48000, channels=2) if AudioParameters else None
    try:
        import inspect
        sig = inspect.signature(RecordStream.__init__).parameters
        kwargs = {}
        if "audio" in sig:
            kwargs["audio"] = True
        if params is not None and "audio_parameters" in sig:
            kwargs["audio_parameters"] = params
        stream = RecordStream(**kwargs) if kwargs else RecordStream(True, params) if params is not None else RecordStream(True)
    except Exception:
        stream = RecordStream(True, params) if params is not None else RecordStream(True)
    await call.record(int(chat_id), stream)
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
        if not text or len(text.strip()) < 2 or text.strip().startswith((".", "/", "!")):
            return
        answer, lang = await _ask(text)
        if not answer:
            return
        answer = re.sub(r"[*_`#>~|]+", "", answer).strip()[:700]
        path = await _tts(answer, lang)
        if not path or not _enabled(client, chat_id):
            return
        _talk_busy.add(key)
        _, call = await _bridge(client)
        await call.play(int(chat_id), path, config=GroupCallConfig(auto_start=False))
        await asyncio.sleep(max(0.5, min(6.0, len(answer) / 10.0)))
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


def _rms(pcm: bytes) -> float:
    if not pcm:
        return 0.0
    import array, math
    a = array.array("h")
    a.frombytes(pcm[: min(len(pcm), 19200)])
    if not a:
        return 0.0
    return math.sqrt(sum(x * x for x in a) / len(a))


async def _incoming_audio(client, update):
    chat_id = int(getattr(update, "chat_id", 0) or 0)
    if not chat_id or not _enabled(client, chat_id):
        return
    key = _key2(client, chat_id)
    if key in _talk_busy:
        return
    fmt_rate, fmt_channels = 48000, 2
    now = asyncio.get_running_loop().time()
    states = _talk_vad.setdefault(key, {})
    for frame_data in getattr(update, "frames", []) or []:
        frame = getattr(frame_data, "frame", b"")
        if not frame:
            continue
        ssrc = int(getattr(frame_data, "ssrc", 0) or 0)
        st = states.setdefault(ssrc, {"pcm": bytearray(), "pre": bytearray(), "voice": 0.0, "last": 0.0, "t0": 0.0})
        seconds = len(frame) / float(fmt_rate * 2 * fmt_channels)
        loud = _rms(frame)
        voice = loud >= VAD_RMS
        if voice and not st["pcm"]:
            st["pcm"] += st["pre"]
            st["pre"].clear()
            st["t0"] = now
        if voice:
            st["voice"] += seconds
            st["last"] = now
        if voice or st["pcm"]:
            st["pcm"] += frame
        else:
            st["pre"] += frame
            max_pre = int(fmt_rate * 2 * fmt_channels * 0.6)
            if len(st["pre"]) > max_pre:
                del st["pre"][:len(st["pre"]) - max_pre]
        elapsed = now - st["t0"] if st["t0"] else 0.0
        if st["pcm"] and st["last"] and (now - st["last"] >= VAD_SILENCE or elapsed >= VAD_MAX):
            pcm = bytes(st["pcm"])
            voice_len = st["voice"]
            st["pcm"].clear(); st["pre"].clear()
            st["voice"] = st["last"] = st["t0"] = 0.0
            if voice_len < VAD_MIN_VOICE:
                continue
            lock = _talk_locks.setdefault(key, asyncio.Lock())
            if lock.locked():
                continue
            async def run(pcm_data=pcm):
                async with lock:
                    await _reply_pipeline(client, chat_id, pcm_data)
            task = asyncio.create_task(run())
            _talk_tasks[key] = task


async def _start_for_joined(client, chat_id):
    try:
        await _start_recording(client, int(chat_id))
        return None
    except Exception as exc:
        return f"{type(exc).__name__}: {str(exc)[:120]}"


async def _watch_global(client):
    owner = _owner_key(client)
    await asyncio.sleep(3)
    while _talk_global.get(owner, False):
        try:
            state = _states.get(_key(client))
            chats = list(state.joined) if state else []
            for cid in chats:
                await _start_for_joined(client, int(cid))
        except Exception as exc:
            log.debug("VC Talk watcher failed: %s", type(exc).__name__)
        await asyncio.sleep(5)


async def start_background_for_client(client):
    owner = _owner_key(client)
    task = _talk_watchers.get(owner)
    if not task or task.done():
        _talk_watchers[owner] = asyncio.create_task(_watch_global(client))


@Client.on_message(filters.command("vctalk", [".", "/"]) & (filters.incoming | filters.me))
async def vctalk_command(client, message):
    args = message.command[1:] if len(message.command) > 1 else []
    action = args[0].lower() if args else "status"
    target = None
    if len(args) > 1:
        try:
            target = int(args[1])
        except Exception:
            target = None

    if action == "on":
        if target is None:
            _talk_global[_owner_key(client)] = True
            await start_background_for_client(client)
            state = _states.get(_key(client))
            joined = list(state.joined) if state else []
            started = 0
            for cid in joined:
                if await _start_for_joined(client, int(cid)) is None:
                    started += 1
            return await message.reply(f"🟢 VC Talk ON\nActive VCs: `{started}`")
        _talk_enabled[_key2(client, target)] = True
        err = await _start_for_joined(client, target)
        return await message.reply("🟢 VC Talk ON" if not err else f"❌ VC Talk start failed: `{err}`")

    if action == "off":
        if target is None:
            _talk_global[_owner_key(client)] = False
            for key in list(_talk_enabled):
                if key[0] == _owner_key(client):
                    _talk_enabled.pop(key, None)
            for cid in list(_talk_recording):
                if cid[0] == _owner_key(client):
                    await _stop_recording(client, cid[1])
            return await message.reply("🔴 VC Talk OFF")
        _talk_enabled.pop(_key2(client, target), None)
        await _stop_recording(client, target)
        return await message.reply("🔴 VC Talk OFF")

    if action == "status":
        owner = _owner_key(client)
        active = [str(k[1]) for k, v in _talk_enabled.items() if k[0] == owner and v]
        return await message.reply("🎙 VC Talk: " + ("ON" if _talk_global.get(owner) or active else "OFF") + (f"\nVCs: {', '.join(active[:10])}" if active else ""))

    await message.reply("Use `.vctalk on`, `.vctalk off`, or `.vctalk on <chat_id>`.")


add_command_help("VcTalk", [
    ["vctalk on", "Enable AI voice conversation in every VC currently joined by the connected ID; newly joined VCs are picked up automatically."],
    ["vctalk off", "Disable AI voice conversation in all VCs."],
    ["vctalk on <chat_id>", "Enable AI voice conversation only in the specified VC; the connected ID joins it if necessary."],
    ["vctalk off <chat_id>", "Disable AI voice conversation only in the specified VC."],
    ["vctalk status", "Show active VC Talk sessions."],
])
