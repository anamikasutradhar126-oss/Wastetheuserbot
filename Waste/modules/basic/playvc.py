import asyncio
import logging
import os
import uuid

from pyrogram import Client, filters
from pytgcalls.types import GroupCallConfig

from Waste.modules.basic.vcfight import _bridge
from Waste.modules.help import add_command_help

log = logging.getLogger(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _download_song(query: str):
    """Resolve one YouTube result and return a real local audio path."""
    import yt_dlp

    job_id = uuid.uuid4().hex
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s")
    base = {
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "source_address": "0.0.0.0",
        "geo_bypass": True,
        "retries": 5,
        "fragment_retries": 5,
        "continuedl": True,
        "overwrites": True,
        "socket_timeout": 20,
    }

    attempts = [
        {
            **base,
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "extractor_args": {"youtube": {"player_client": ["android_vr", "android", "web"]}},
        },
        {
            **base,
            "format": "bestaudio/best",
            "extractor_args": {"youtube": {"player_client": ["web_creator", "web_safari", "android"]}},
        },
    ]

    last_error = None
    for options in attempts:
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(query, download=True)
                if info and info.get("entries"):
                    info = next((x for x in info["entries"] if x), None)
                if not info:
                    raise RuntimeError("No YouTube result found")
                requested = ydl.prepare_filename(info)
                if os.path.exists(requested):
                    return requested, info

                # yt-dlp may change the extension after post-processing.
                stem = os.path.splitext(requested)[0]
                matches = [
                    os.path.join(DOWNLOAD_DIR, name)
                    for name in os.listdir(DOWNLOAD_DIR)
                    if name.startswith(os.path.basename(stem) + ".")
                ]
                if matches:
                    return matches[0], info
                raise FileNotFoundError("Downloaded audio file not found")
        except Exception as exc:
            last_error = exc
            continue

    raise last_error or RuntimeError("Music download failed")


async def play_song_in_chat(client, chat_id: int, query: str):
    """Download and play the requested song in the VC using the connected ID."""
    path, info = await asyncio.to_thread(_download_song, query)
    state, call = await _bridge(client)
    if chat_id not in state.joined:
        try:
            from Waste.modules.basic.vcfight import _join
            await _join(client, chat_id)
        except Exception:
            if os.path.exists(path):
                os.remove(path)
            raise RuntimeError("Connected ID is not in this VC. Use `.join <chatid>` or `.allvc join` first.")
    state.current = chat_id
    try:
        await call.play(chat_id, path, config=GroupCallConfig(auto_start=False))
    except Exception:
        if os.path.exists(path):
            os.remove(path)
        raise
    return path, info


# The Telegram control bot in Waste.modules.bot.start owns the group-wide
# /play/.play dispatcher. Keeping only play_song_in_chat here prevents multiple
# connected userbot sessions from all playing the same request simultaneously.


async def _cleanup_later(path: str, delay: int):
    await asyncio.sleep(delay)
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


add_command_help("Music", [
    ["play <song name>", "Download the requested song and play it in the current group's VC using the connected ID."],
    ["vplay <song name>", "Alias of play."],
])
