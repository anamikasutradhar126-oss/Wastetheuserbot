# © By Waste shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

from pyrogram import Client, enums, filters 
from pyrogram.types import Message 
from config import LOG_GROUP
from Waste.modules.help import add_command_help
log = []


@Client.on_message(filters.command("tagalert", [".", "/"]) & filters.me)
async def tagalert_command(client: Client, message: Message):
    action = (message.command[1].lower() if len(message.command) > 1 else "status")
    chat_id = message.chat.id
    if action == "on":
        if chat_id not in log:
            log.append(chat_id)
        return await message.edit("**ᴛᴀɢ ᴀʟᴇʀᴛ ᴀᴄᴛɪᴠᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ**")
    if action == "off":
        if chat_id in log:
            log.remove(chat_id)
        return await message.edit("**ᴛᴀɢ ᴀʟᴇʀᴛ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ**")
    return await message.edit("**ᴛᴀɢ ᴀʟᴇʀᴛ:** " + ("ON" if chat_id in log else "OFF"))

if log:
 @Client.on_message(filters.group & filters.mentioned & filters.incoming)
 async def log_tagged_messages(client: Client, message: Message):
    result = f"<b>📨 #TAGS #MESSAGE</b>\n<b> • : </b>{message.from_user.mention}"
    result += f"\n<b> • Group : </b>{message.chat.title}"
    result += f"\n<b> • 👀 </b><a href = '{message.link}'>Lihat Pesan</a>"
    result += f"\n<b> • Message : </b><code>{message.text}</code>"
    await asyncio.sleep(0.5)
    await client.send_message(
        LOG_GROUP,
        result,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
    )


add_command_help(
    "tagalert",
    [
        [
            "tagalert on/off",
            "To activate or deactivate the group tag, which will go to the log group.",
        ],
    ],
)
