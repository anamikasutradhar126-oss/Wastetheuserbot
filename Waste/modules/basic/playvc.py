import asyncio
import logging
import os
import uuid

from pyrogram import Client, filters
from pytgcalls.types import GroupCallConfig

from Waste.modules.basic.vcfight import _bridge, _states
from Waste.modules.help import add_command_help

log = logging.getLogger(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _download_song(query: str):
    """Resolve and download one audio track for PyTgCalls."""
    import yt_dlp

    job_id = uuid.uuid4().hex
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s")
    options = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "source_address": "0.0.0.0",
        "geo_bypass": True,
        "retries": 3,
        "fragment_retries": 3,
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
    }
    if os.path.exists("cookies.txt") and os.path.getsize("cookies.txt") > 0:
        options["cookiefile"] = "cookies.txt"

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(query, download=True)
    except Exception as first_error:
        # YouTube can reject one player client/format. Retry with a different
        # client set before surfacing the failure to the user.
        fallback = dict(options)
        fallback["format"] = "bestaudio/best"
        fallback["extractor_args"] = {"youtube": {"player_client": ["web_safari", "android"]}}
        try:
            with yt_dlp.YoutubeDL(fallback) as ydl:
                info = ydl.extract_info(query, download=True)
        except Exception:
            raise first_error
        if info and info.get("entries"):
            info = info["entries"][0]
        if not info:
            raise RuntimeError("No result found")
        requested = ydl.prepare_filename(info)
        path = requested
        if not os.path.exists(path):
            base = os.path.splitext(requested)[0]
            matches = [
                os.path.join(DOWNLOAD_DIR, name)
                for name in os.listdir(DOWNLOAD_DIR)
                if name.startswith(os.path.basename(base) + ".")
            ]
            if matches:
                path = matches[0]
        if not os.path.exists(path):
            raise FileNotFoundError("Downloaded audio file not found")
        return path, info


async def play_song_in_chat(client, chat_id: int, query: str):
    """Download a YouTube result and play it in the supplied group's VC using this connected account."""
    path, info = await asyncio.to_thread(_download_song, query)
    state, call = await _bridge(client)
    state.current = chat_id
    await call.play(chat_id, path, config=GroupCallConfig(auto_start=False))
    return path, info


@Client.on_message(filters.command(["play", "vplay"], [".", "/"]) & filters.me)
async def play_handler(client, message):
    if not message.chat or getattr(message.chat.type, "value", message.chat.type) not in {"group", "supergroup"}:
        return await message.reply(
            "<blockquote>❌ Use <code>.play song name</code> inside a group.</blockquote>",
            parse_mode="html",
        )

    parts = message.text.split(None, 1) if message.text else []
    query = parts[1].strip() if len(parts) > 1 else ""
    if not query:
        return await message.reply(
            "<blockquote>🎵 Usage: <code>.play song name</code> or <code>/play song name</code></blockquote>",
            parse_mode="html",
        )

    status = await message.reply(
        "<blockquote>🔎 <b>Searching...</b>\n\n🎵 <code>" + query.replace("<", "&lt;").replace(">", "&gt;") + "</code></blockquote>",
        parse_mode="html",
    )
    path = None
    try:
        path, info = await play_song_in_chat(client, message.chat.id, query)
        title = info.get("title") or query
        duration = info.get("duration_string") or "Unknown"

        await status.edit(
            "<blockquote>▶️ <b>Now Playing</b>\n\n"
            f"🎵 <b>{title}</b>\n"
            f"⏱️ {duration}\n"
            "🔊 <b>Playing in this group's Voice Chat</b>\n"
            "👤 <b>Connected ID</b></blockquote>",
            parse_mode="html",
        )

        # Keep the downloaded file alive while PyTgCalls is consuming it.
        duration_seconds = info.get("duration") or 0
        if duration_seconds:
            await asyncio.sleep(min(float(duration_seconds) + 10, 60 * 60 * 4))
        else:
            await asyncio.sleep(60 * 60 * 4)
    except Exception as exc:
        log.exception("Music play failed")
        try:
            await status.edit(
                f"<blockquote>❌ <b>Music failed</b>\n\n<code>{type(exc).__name__}</code></blockquote>",
                parse_mode="html",
            )
        except Exception:
            pass
    finally:
        if path:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass


add_command_help(
    "Music",
    [
        ["play", "Search and play a song in the connected account's actual group Voice Chat."],
        ["vplay", "Play audio in the connected account's actual group Voice Chat."],
    ],
)
