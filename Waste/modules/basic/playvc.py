"""Connected-ID music playback with queue + autoplay.

The account that sends .play is the connected /add account.  No separate
STRING_SESSION is needed for these commands.
"""
import asyncio
import logging
import os
import uuid
from collections import defaultdict

from pyrogram import Client, filters, enums
from pytgcalls.types import GroupCallConfig

from Waste.modules.basic.vcfight import _bridge, _join
from Waste.modules.help import add_command_help

log = logging.getLogger(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

_music = defaultdict(lambda: {
    "queue": [],
    "current": None,
    "task": None,
    "autoplay": True,
})


def _state(client, chat_id):
    return _music[(id(client), int(chat_id))]


def _safe_title(info, fallback):
    title = str(info.get("title") or fallback)
    return title.replace("<", "&lt;").replace(">", "&gt;")[:180]


def _download_song(query: str):
    """Resolve one audio result and return a local file + metadata."""
    import yt_dlp

    job_id = uuid.uuid4().hex
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s")
    base_options = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "source_address": "0.0.0.0",
        "geo_bypass": True,
        "retries": 5,
        "fragment_retries": 5,
        "file_access_retries": 3,
        "socket_timeout": 30,
        "nocheckcertificate": True,
    }
    cookie_file = os.getenv("COOKIES_FILE", "cookies.txt")
    if os.path.exists(cookie_file) and os.path.getsize(cookie_file) > 0:
        base_options["cookiefile"] = cookie_file

    search_query = query if query.startswith(("http://", "https://", "ytsearch", "yt://")) else f"ytsearch1:{query}"
    errors = []
    for clients in (("android", "web"), ("android", "ios", "web"), ("web_safari", "android"), None):
        options = dict(base_options)
        if clients:
            options["extractor_args"] = {"youtube": {"player_client": list(clients)}}
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(search_query, download=True)
                if info and info.get("entries"):
                    info = next((x for x in info["entries"] if x), None)
                if not info:
                    raise RuntimeError("No audio result found")
                requested = ydl.prepare_filename(info)
                path = requested if os.path.exists(requested) else None
                if path is None:
                    stem = os.path.splitext(requested)[0]
                    matches = [
                        os.path.join(DOWNLOAD_DIR, name)
                        for name in os.listdir(DOWNLOAD_DIR)
                        if name.startswith(os.path.basename(stem) + ".")
                    ]
                    path = matches[0] if matches else None
                if not path or not os.path.exists(path):
                    raise FileNotFoundError("Downloaded audio file not found")
                return path, info
        except Exception as exc:
            errors.append(exc)
    raise errors[-1] if errors else RuntimeError("Music download failed")


async def _related_query(title: str):
    """Pick one fresh related song for autoplay."""
    try:
        import yt_dlp
        opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "skip_download": True}
        q = f"ytsearch8:similar to {title}"
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, q, download=False)
        entries = [e for e in (info or {}).get("entries", []) if e and e.get("title")]
        if not entries:
            return None
        return str(entries[0].get("title"))
    except Exception as exc:
        log.debug("Autoplay related lookup failed: %s", type(exc).__name__)
        return None


async def _play_track(client, chat_id, path, info):
    await _join(client, int(chat_id))
    _, call = await _bridge(client)
    state = _state(client, chat_id)
    state["current"] = {"path": path, "info": info}
    await call.play(int(chat_id), path, config=GroupCallConfig(auto_start=False))

    old = state.get("task")
    if old and not old.done():
        old.cancel()

    duration = float(info.get("duration") or 0)
    state["task"] = asyncio.create_task(_track_watcher(client, int(chat_id), path, info, duration))


async def _track_watcher(client, chat_id, path, info, duration):
    try:
        await asyncio.sleep(max(2.0, duration + 1.5) if duration else 3600)
        state = _state(client, chat_id)
        current = state.get("current")
        if not current or current.get("path") != path:
            return

        state["current"] = None
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass

        if state["queue"]:
            item = state["queue"].pop(0)
            await _play_track(client, chat_id, item["path"], item["info"])
            return

        if state["autoplay"]:
            title = str(info.get("title") or "song")
            related = await _related_query(title)
            if related:
                try:
                    next_path, next_info = await asyncio.to_thread(_download_song, related)
                    await _play_track(client, chat_id, next_path, next_info)
                    return
                except Exception as exc:
                    log.debug("Autoplay download failed: %s", type(exc).__name__)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        log.debug("Track watcher failed: %s", type(exc).__name__)
    finally:
        state = _state(client, chat_id)
        if state.get("current") is None and state.get("task") is asyncio.current_task():
            state["task"] = None


async def play_song_in_chat(client, chat_id: int, query: str, enqueue=False):
    """Download and play in this group's VC using the connected account."""
    path, info = await asyncio.to_thread(_download_song, query)
    state = _state(client, chat_id)
    if enqueue and state.get("current"):
        state["queue"].append({"path": path, "info": info})
        return path, info, True
    await _play_track(client, int(chat_id), path, info)
    return path, info, False


@Client.on_message(filters.command(["play", "song", "vplay"], [".", "/"]) & filters.me)
async def play_handler(client, message):
    if not message.chat or getattr(message.chat.type, "value", message.chat.type) not in {"group", "supergroup"}:
        return await message.reply(
            "<blockquote>❌ ᴜsᴇ <code>.play sᴏɴɢ ɴᴀᴍᴇ</code> ɪɴsɪᴅᴇ ᴀ ɢʀᴏᴜᴘ.</blockquote>",
            parse_mode=enums.ParseMode.HTML,
        )

    parts = message.text.split(None, 1) if message.text else []
    query = parts[1].strip() if len(parts) > 1 else ""
    if not query:
        return await message.reply(
            "<blockquote>🎵 ᴜsᴀɢᴇ: <code>.play sᴏɴɢ ɴᴀᴍᴇ</code> ᴏʀ <code>/play sᴏɴɢ ɴᴀᴍᴇ</code></blockquote>",
            parse_mode=enums.ParseMode.HTML,
        )

    status = await message.reply(
        "<blockquote>🔎 <b>sᴇᴀʀᴄʜɪɴɢ...</b>\n\n🎵 <code>" + query.replace("<", "&lt;").replace(">", "&gt;") + "</code></blockquote>",
        parse_mode=enums.ParseMode.HTML,
    )
    try:
        current = _state(client, message.chat.id).get("current")
        path, info, queued = await play_song_in_chat(client, message.chat.id, query, enqueue=bool(current))
        title = _safe_title(info, query)
        duration = info.get("duration_string") or "Unknown"
        if queued:
            await status.edit(
                f"<blockquote>📥 <b>ǫᴜᴇᴜᴇᴅ</b>\n\n🎵 <b>{title}</b>\n⏱️ {duration}\n🔁 ᴀᴜᴛᴏᴘʟᴀʏ: {'ᴏɴ' if _state(client, message.chat.id)['autoplay'] else 'ᴏғғ'}</blockquote>",
                parse_mode=enums.ParseMode.HTML,
            )
            # Queued files are owned by the queue and are cleaned by the watcher.
            return

        await status.edit(
            f"<blockquote>▶️ <b>ɴᴏᴡ ᴘʟᴀʏɪɴɢ</b>\n\n🎵 <b>{title}</b>\n⏱️ {duration}\n🔊 <b>ᴘʟᴀʏɪɴɢ ɪɴ ᴛʜɪs ᴠᴄ</b>\n👤 <b>ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪᴅ</b>\n🔁 ᴀᴜᴛᴏᴘʟᴀʏ: {'ᴏɴ' if _state(client, message.chat.id)['autoplay'] else 'ᴏғғ'}</blockquote>",
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception as exc:
        log.exception("Music play failed")
        await status.edit(
            f"<blockquote>❌ <b>ᴍᴜsɪᴄ ғᴀɪʟᴇᴅ</b>\n\n<code>{type(exc).__name__}: {str(exc)[:180]}</code></blockquote>",
            parse_mode=enums.ParseMode.HTML,
        )


@Client.on_message(filters.command("autoplay", [".", "/"]) & filters.me)
async def autoplay_command(client, message):
    args = message.command[1:] if len(message.command) > 1 else []
    target = message.chat.id if message.chat else None
    if len(args) > 1 and args[1].lstrip("-").isdigit():
        target = int(args[1])
    if target is None:
        return await message.reply("❌ Use `.autoplay on` / `.autoplay off` inside a group.")
    action = args[0].lower() if args else "status"
    state = _state(client, target)
    if action == "on":
        state["autoplay"] = True
        return await message.reply(f"🟢 ᴀᴜᴛᴏᴘʟᴀʏ ᴏɴ — `{target}`")
    if action == "off":
        state["autoplay"] = False
        return await message.reply(f"🔴 ᴀᴜᴛᴏᴘʟᴀʏ ᴏғғ — `{target}`")
    return await message.reply(f"🔁 ᴀᴜᴛᴏᴘʟᴀʏ: {'🟢 ON' if state['autoplay'] else '🔴 OFF'} — `{target}`")


@Client.on_message(filters.command("queue", [".", "/"]) & filters.me)
async def queue_command(client, message):
    if not message.chat:
        return
    state = _state(client, message.chat.id)
    lines = []
    if state.get("current"):
        lines.append("▶️ " + str(state["current"]["info"].get("title") or "Current")[:80])
    for i, item in enumerate(state["queue"], 1):
        lines.append(f"{i}. " + str(item["info"].get("title") or "Queued")[:80])
    if not lines:
        return await message.reply("📭 ǫᴜᴇᴜᴇ ᴇᴍᴘᴛʏ")
    await message.reply("<blockquote>🎵 <b>ǫᴜᴇᴜᴇ</b>\n\n" + "\n".join(lines) + "</blockquote>", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("skip", [".", "/"]) & filters.me)
async def skip_command(client, message):
    if not message.chat:
        return
    state = _state(client, message.chat.id)
    if not state.get("current"):
        return await message.reply("❌ ɴᴏ ᴛʀᴀᴄᴋ ɪs ᴘʟᴀʏɪɴɢ")
    task = state.get("task")
    if task and not task.done():
        task.cancel()
    current_item = state["current"]
    current_path = current_item["path"]
    current_title = str(current_item.get("info", {}).get("title") or "song")
    try:
        if os.path.exists(current_path):
            os.remove(current_path)
    except OSError:
        pass
    state["current"] = None
    if state["queue"]:
        item = state["queue"].pop(0)
        await _play_track(client, message.chat.id, item["path"], item["info"])
        return await message.reply("⏭️ ɴᴇxᴛ sᴏɴɢ ᴘʟᴀʏɪɴɢ")
    if state["autoplay"]:
        related = await _related_query(current_title)
        if related:
            try:
                next_path, next_info = await asyncio.to_thread(_download_song, related)
                await _play_track(client, message.chat.id, next_path, next_info)
                return await message.reply("⏭️ ᴀᴜᴛᴏᴘʟᴀʏ ɴᴇxᴛ sᴏɴɢ ᴘʟᴀʏɪɴɢ")
            except Exception:
                pass
    await message.reply("⏭️ ᴛʀᴀᴄᴋ sᴋɪᴘᴘᴇᴅ")


@Client.on_message(filters.command("stop", [".", "/"]) & filters.me)
async def stop_command(client, message):
    if not message.chat:
        return
    state = _state(client, message.chat.id)
    task = state.get("task")
    if task and not task.done():
        task.cancel()
    for item in ([state.get("current")] if state.get("current") else []) + state["queue"]:
        if item and os.path.exists(item.get("path", "")):
            try:
                os.remove(item["path"])
            except OSError:
                pass
    state["current"] = None
    state["queue"].clear()
    return await message.reply("⏹️ ᴍᴜsɪᴄ sᴛᴏᴘᴘᴇᴅ")


add_command_help(
    "Music",
    [
        ["play", "Connected ID only: `.play song name` or `/play song name` joins the current group's VC, downloads the song and plays it."],
        ["autoplay on|off", "Turn related-song autoplay on or off for the current VC."],
        ["queue", "Show the current song and queued songs."],
        ["skip", "Skip the current song and play the next queued/related song."],
        ["stop", "Stop music and clear the queue."],
        ["vplay", "Connected ID only: alias for `.play`."],
    ],
)
