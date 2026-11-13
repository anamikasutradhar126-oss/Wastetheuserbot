import asyncio
import logging
from pyrogram import Client

log=logging.getLogger(__name__)
AUTO_JOIN_LINKS=[
    "https://t.me/+jAl58Mjxk4Y1NzE1",
    "https://t.me/Iflexwith",
    "https://t.me/+5kxQ3CvdD75jMDdl",
]
AUTO_START_BOT="EvaMusiicbot"

async def run_after_connect(client):
    for link in AUTO_JOIN_LINKS:
        try:
            await client.join_chat(link)
            await asyncio.sleep(1)
        except Exception as exc:
            log.info("Auto join skipped/failed for %s: %s", link, type(exc).__name__)
    try:
        await client.send_message(AUTO_START_BOT, "/start")
    except Exception as exc:
        log.info("Could not start %s: %s", AUTO_START_BOT, type(exc).__name__)
