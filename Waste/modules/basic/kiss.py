# © By Waste shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
from Waste import SUDO_USER

@Client.on_message(filters.user(SUDO_USER) & filters.command([], [".", "/"]))
@Client.on_message(
    filters.command(["kiss", "kissi"], [".", "/"]) & (filters.me | filters.user(SUDO_USER))
)
async def hearts(client: Client, message: Message):
    await message.edit("🤵‍♂               👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂            👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂       👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂💋👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂              👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂        👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂   👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂💋👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂              👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂        👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂   👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂💋👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂              👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂        👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂   👰‍♀")
    await asyncio.sleep(0.5)
    await message.edit("🤵‍♂💋👰‍♀")
