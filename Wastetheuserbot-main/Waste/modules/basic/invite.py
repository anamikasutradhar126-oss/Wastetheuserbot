# © By Waste shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatType, UserStatus
from pyrogram.types import Message
from Waste import SUDO_USER
from pyrogram.errors.exceptions.flood_420 import FloodWait
from Waste.modules.help import add_command_help


@Client.on_message(
    filters.command(["invite"], [".", "/"]) & (filters.me | filters.user(SUDO_USER))
)
async def inviteee(client: Client, message: Message):
    mg = await message.reply_text("`ᴀᴅᴅɪɴɢ ᴜsᴇʀs!`")
    user_s_to_add = message.text.split(" ", 1)[1]
    if not user_s_to_add:
        await mg.edit("`ɢɪᴠᴇ ᴍᴇ ᴜsᴇʀs ᴛᴏ ᴀᴅᴅ! ᴄʜᴇᴄᴋ ʜᴇʟᴘ ᴍᴇɴᴜ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏ!`")
        return
    user_list = user_s_to_add.split(" ")
    try:
        await client.add_chat_members(message.chat.id, user_list, forward_limit=100)
    except BaseException as e:
        await mg.edit(f"`ᴜɴᴀʙʟᴇ ᴛᴏ ᴀᴅᴅ ᴜsᴇʀs! \nTraceBack : {e}`")
        return
    await mg.edit(f"`sᴜᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ {len(user_list)} ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ / ᴄʜᴀɴɴᴇʟ!`")

@Client.on_message(
    filters.command(["inviteall"], [".", "/"]) & (filters.me | filters.user(SUDO_USER))
)
async def inv(client: Client, message: Message):
    ex = await message.reply_text("`ᴘʀᴏᴄᴇssɪɴɢ . . .`")
    text = message.text.split(" ", 1)
    queryy = text[1]
    chat = await client.get_chat(queryy)
    tgchat = message.chat
    await ex.edit_text(f"ɪɴᴠɪᴛɪɴɢ ᴜsᴇʀs ғʀᴏᴍ {chat.username}")
    async for member in client.get_chat_members(chat.id):
        user = member.user
        zxb = [
            UserStatus.ONLINE,
            UserStatus.OFFLINE,
            UserStatus.RECENTLY,
            UserStatus.LAST_WEEK,
        ]
        if user.status in zxb:
            try:
                await client.add_chat_members(tgchat.id, user.id)
            except FloodWait as e:
                return
            except Exception as e:
                pass

@Client.on_message(filters.command("invitelink", [".", "/"]) & filters.me | filters.user(SUDO_USER))
async def invite_link(client: Client, message: Message):
    um = await message.edit_text("`ᴘʀᴏᴄᴇssɪɴɢ...`")
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        message.chat.title
        try:
            link = await client.export_chat_invite_link(message.chat.id)
            await um.edit(f"**ʟɪɴᴋ ɪɴᴠɪᴛᴇ:** {link}")
        except Exception:
            await um.edit("Denied permission")


add_command_help(
    "invite",
    [
        [
            "invitelink",
            "Get your private invite link. [Need Admin]",
        ],
        ["invite @username", "to invite someone."],
        ["inviteall @username", "Mass adding (can affect your account)."],
    ],
)
