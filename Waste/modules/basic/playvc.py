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
    """Resolve and download one audio track for PyTgCalls.

    YouTube sometimes requires authentication for audio extraction. The downloader
    accepts either a local cookies.txt or YOUTUBE_COOKIES_FILE/YOUTUBE_COOKIES_B64.
    """
    import base64
    import tempfile
    import yt_dlp

    job_id = uuid.uuid4().hex
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s")
    base_options = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "source_address": "0.0.0.0",
        "geo_bypass": True,
        "retries": 5,
        "fragment_retries": 5,
        "socket_timeout": 30,
        "concurrent_fragment_downloads": 3,
    }

    cookie_path = ""
    for candidate in ("cookies.txt", os.getenv("YOUTUBE_COOKIES_FILE", "")):
        if candidate and os.path.exists(candidate) and os.path.getsize(candidate) > 0:
            cookie_path = candidate
            break

    temp_cookie = None
    if not cookie_path:
        encoded = os.getenv("YOUTUBE_COOKIES_B64", "").strip()
        if encoded:
            try:
                fd, temp_cookie = tempfile.mkstemp(prefix="ytcookies_", suffix=".txt")
                with os.fdopen(fd, "wb") as fh:
                    fh.write(base64.b64decode(encoded))
                cookie_path = temp_cookie
            except Exception:
                temp_cookie = None
    if cookie_path:
        base_options["cookiefile"] = cookie_path

    attempts = [
        ["android_vr"],
        ["ios"],
        ["web_safari"],
        ["web_embedded"],
        ["tv_embedded"],
    ]
    last_exc = None
    try:
        for player_client in attempts:
            options = dict(base_options)
            options["extractor_args"] = {"youtube": {"player_client": player_client}}
            try:
                with yt_dlp.YoutubeDL(options) as ydl:
                    info = ydl.extract_info(query, download=True)
                    if info and info.get("entries"):
                        info = next((entry for entry in info["entries"] if entry), None)
                    if not info:
                        raise RuntimeError("No YouTube result found")
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
                if os.path.exists(path):
                    return path, info
                last_exc = FileNotFoundError("Downloaded audio file not found")
            except Exception as exc:
                last_exc = exc
                continue
    finally:
        if temp_cookie:
            try:
                os.remove(temp_cookie)
            except OSError:
                pass

    if last_exc and "Sign in to confirm" in str(last_exc):
        raise RuntimeError("YouTube requires authentication for this video. Add a valid cookies.txt file or set YOUTUBE_COOKIES_FILE/YOUTUBE_COOKIES_B64.") from last_exc
    raise last_exc or RuntimeError("YouTube download failed")


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
                f"<blockquote>❌ <b>Music failed</b>\n\n<code>{type(exc).__name__}</code>\n\n"
                "If YouTube asks for sign-in, add a valid cookies.txt file to the project and try again.</blockquote>",
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
        ["play", "Connected ID only: `.play song name` or `/play song name` searches and plays the song in the current group Voice Chat."],
        ["vplay", "Connected ID only: play audio in the connected account's actual group Voice Chat."],
    ],
)
