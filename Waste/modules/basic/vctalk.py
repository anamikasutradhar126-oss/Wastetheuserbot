import asyncio
import logging
import os
import uuid
from typing import Optional

from gtts import gTTS
from pyrogram import Client, filters
from pyrogram.types import Message

from Waste.modules.basic.vcfight import _bridge, _states
from Waste.modules.basic.aichat import _ask_groq
from Waste.modules.bot.start import settings_col
from Waste.modules.help import add_command_help

log = logging.getLogger(__name__)
TALK_DIR = "vctalk_audio"
os.makedirs(TALK_DIR, exist_ok=True)


def _talk_map(client):
    value = getattr(client, "_vctalk_targets", None)
    if not isinstance(value, set):
        value = set()
        setattr(client, "_vctalk_targets", value)
    return value


def _global_enabled(client) -> bool:
    return bool(getattr(client, "_vctalk_global", False))


def _target_enabled(client, chat_id: int) -> bool:
    return _global_enabled(client) or int(chat_id) in _talk_map(client)


def _load_settings(client):
    uid = getattr(client, "_waste_owner_uid", None)
    if not uid:
        return
    try:
        doc = settings_col.find_one({"_id": int(uid)}) or {}
        setattr(client, "_vctalk_global", bool(doc.get("vctalk_global", False)))
        _talk_map(client).update(int(x) for x in doc.get("vctalk_targets", []))
    except Exception as exc:
        log.debug("VC Talk settings load failed: %s", type(exc).__name__)


def _save_settings(client):
    uid = getattr(client, "_waste_owner_uid", None)
    if not uid:
        return
    settings_col.update_one(
        {"_id": int(uid)},
        {"$set": {
            "vctalk_global": _global_enabled(client),
            "vctalk_targets": sorted(_talk_map(client)),
        }},
        upsert=True,
    )


async def _ensure_settings(client):
    if not hasattr(client, "_vctalk_loaded"):
        _load_settings(client)
        setattr(client, "_vctalk_loaded", True)


async def _speak(client, chat_id: int, text: str):
    state, call = await _bridge(client)
    # The connected ID must already be in this VC. .allvc/.join are responsible
    # for joining; VC Talk only speaks in the connected account's joined calls.
    if chat_id not in state.joined:
        return False

    answer = await _ask_groq(text)
    if not answer or answer.startswith(("⚠️", "⏳")):
        return False

    path = os.path.join(TALK_DIR, f"{uuid.uuid4().hex}.mp3")
    try:
        await asyncio.to_thread(gTTS(text=answer[:1200], lang="en", slow=False).save, path)
        await call.play(chat_id, path)
        asyncio.create_task(_cleanup(path, 300))
        return True
    except Exception as exc:
        log.warning("VC Talk playback failed: %s", type(exc).__name__)
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass
        return False


async def _cleanup(path: str, delay: int):
    await asyncio.sleep(delay)
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


@Client.on_message(filters.command("vctalk", [".", "/"]) & filters.me)
async def vctalk_command(client, message: Message):
    await _ensure_settings(client)
    args = [x.strip() for x in message.command[1:]]
    action = args[0].lower() if args else "status"
    target: Optional[int] = None
    if len(args) > 1:
        try:
            target = int(args[1])
        except ValueError:
            return await message.reply("❌ Invalid chat ID.")

    if action == "on":
        if target is None:
            client._vctalk_global = True
            _save_settings(client)
            return await message.reply(
                "🎙️ **VC Talk: ON**\nAI voice replies are enabled for every VC this connected ID joins."
            )
        _talk_map(client).add(target)
        _save_settings(client)
        return await message.reply(f"🎙️ **VC Talk: ON**\nEnabled only for VC `{target}`.")

    if action == "off":
        if target is None:
            client._vctalk_global = False
            _talk_map(client).clear()
            _save_settings(client)
            return await message.reply("🔴 **VC Talk: OFF**\nAI voice conversation disabled.")
        _talk_map(client).discard(target)
        _save_settings(client)
        return await message.reply(f"🔴 **VC Talk: OFF**\nDisabled only for VC `{target}`.")

    if action == "status":
        targets = sorted(_talk_map(client))
        state = "ON (ALL VCs)" if _global_enabled(client) else ("ON (SELECTED VCs)" if targets else "OFF")
        extra = "\nTargets: " + ", ".join(map(str, targets)) if targets else ""
        return await message.reply(f"🎙️ **VC Talk:** {state}{extra}")

    return await message.reply(
        "Usage: `.vctalk on` / `.vctalk off` / `.vctalk status`\n"
        "Per VC: `.vctalk on <chatid>` / `.vctalk off <chatid>`"
    )


@Client.on_message(
    filters.incoming & filters.group & filters.text & ~filters.me & ~filters.bot
)
async def vctalk_text_listener(client, message: Message):
    await _ensure_settings(client)
    chat_id = int(message.chat.id)
    if not _target_enabled(client, chat_id):
        return

    state = _states.get(id(client))
    if not state or chat_id not in state.joined:
        return

    text = (message.text or "").strip()
    if not text or text.startswith((".", "/", "!")):
        return

    # Each connected userbot session handles its own joined VC. This prevents
    # the control bot from speaking in the call and keeps the connected ID as
    # the actual voice participant.
    await _speak(client, chat_id, text)


add_command_help(
    "VcTalk",
    [
        ["vctalk on", "Enable AI voice replies in every VC joined by the connected ID."],
        ["vctalk off", "Disable AI voice replies globally."],
        ["vctalk on <chatid>", "Enable AI voice replies only for one VC/group."],
        ["vctalk off <chatid>", "Disable AI voice replies for one VC/group."],
        ["vctalk status", "Show VC Talk status and selected VC IDs."],
    ],
)
