# © By Waste shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import os
from asyncio import sleep
import os
import sys
from re import sub
from time import time
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from Waste.helper.PyroHelpers import ReplyCheck
from Waste.modules.help import add_command_help

flood = {}
profile_photo = "cache/pfp.jpg"


async def extract_userid(message, text: str):
    def is_int(text: str):
        try:
            int(text)
        except ValueError:
            return False
        return True

    text = text.strip()

    if is_int(text):
        return int(text)

    entities = message.entities
    app = message._client
    if len(entities) < 2:
        return (await app.get_users(text)).id
    entity = entities[1]
    if entity.type == "mention":
        return (await app.get_users(text)).id
    if entity.type == "text_mention":
        return entity.user.id
    return None


async def extract_user_and_reason(message, sender_chat=False):
    args = message.text.strip().split()
    text = message.text
    user = None
    reason = None
    if message.reply_to_message:
        reply = message.reply_to_message
        if not reply.from_user:
            if (
                reply.sender_chat
                and reply.sender_chat != message.chat.id
                and sender_chat
            ):
                id_ = reply.sender_chat.id
            else:
                return None, None
        else:
            id_ = reply.from_user.id

        if len(args) < 2:
            reason = None
        else:
            reason = text.split(None, 1)[1]
        return id_, reason

    if len(args) == 2:
        user = text.split(None, 1)[1]
        return await extract_userid(message, user), None

    if len(args) > 2:
        user, reason = text.split(None, 2)[1:]
        return await extract_userid(message, user), reason

    return user, reason


async def extract_user(message):
    return (await extract_user_and_reason(message))[0]

@Client.on_message(filters.command(["unblock"], [".", "/"]) & filters.me)
async def unblock_user_func(client: Client, message: Message):
    user_id = await extract_user(message)
    tex = await message.reply_text("`Processing . . .`")
    if not user_id:
        return await message.edit(
            "ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀ ID/ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴜsᴇʀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴜɴʙʟᴏᴄᴋ."
        )
    if user_id == client.me.id:
        return await tex.edit("ᴏʜᴋ ᴅᴏɴᴇ ✅.")
    await client.unblock_user(user_id)
    umention = (await client.get_users(user_id)).mention
    await message.edit(f"**sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴʙʟᴏᴄᴋᴇᴅ** {umention}")

@Client.on_message(filters.command(["block"], [".", "/"]) & filters.me)
async def block_user_func(client: Client, message: Message):
    user_id = await extract_user(message)
    tex = await message.reply_text("`ᴘʀᴏᴄᴇssɪɴɢ . . .`")
    if not user_id:
        return await tex.edit_text(
            "ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀ ID/ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴜsᴇʀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʟᴏᴄᴋ."
        )
    if user_id == client.me.id:
        return await tex.edit_text("ᴏʜᴋ ✅.")
    await client.block_user(user_id)
    umention = (await client.get_users(user_id)).mention
    await tex.edit_text(f"**sᴜᴄᴄᴇssғᴜʟʟʏ ʙʟᴏᴄᴋᴇᴅ** {umention}")


@Client.on_message(filters.command(["setname"], [".", "/"]) & filters.me)
async def setname(client: Client, message: Message):
    tex = await message.reply_text("`ᴘʀᴏᴄᴇssɪɴɢ . . .`")
    if len(message.command) == 1:
        return await tex.edit(
            "ᴘʀᴏᴠɪᴅᴇ ᴀ ᴛᴇxᴛ ᴛᴏ sᴇᴛ ᴀs ʏᴏᴜʀ ɴᴀᴍᴇ."
        )
    elif len(message.command) > 1:
        name = message.text.split(None, 1)[1]
        try:
            await client.update_profile(first_name=name)
            await tex.edit(f"**sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ʏᴏᴜʀ ɴᴀᴍᴇ ᴛᴏ** `{name}`")
        except Exception as e:
            await tex.edit(f"**ᴇʀʀᴏʀ:** `{e}`")
    else:
        return await tex.edit(
            "ᴘʀᴏᴠɪᴅᴇ ᴀ ᴛᴇxᴛ ᴛᴏ sᴇᴛ ᴀs ʏᴏᴜʀ ɴᴀᴍᴇ."
        )

@Client.on_message(filters.command(["setbio"], [".", "/"]) & filters.me)
async def set_bio(client: Client, message: Message):
    tex = await message.edit_text("`ᴘʀᴏᴄᴇssɪɴɢ . . .`")
    if len(message.command) == 1:
        return await tex.edit("ᴘʀᴏᴠɪᴅᴇ ᴛᴇxᴛ ᴛᴏ sᴇᴛ ᴀs ʙɪᴏ.")
    elif len(message.command) > 1:
        bio = message.text.split(None, 1)[1]
        try:
            await client.update_profile(bio=bio)
            await tex.edit(f"**sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ʙɪᴏ ᴛᴏ** `{bio}`")
        except Exception as e:
            await tex.edit(f"**ᴇʀʀᴏʀ:** `{e}`")
    else:
        return await tex.edit("ᴘʀᴏᴠɪᴅᴇ ᴛᴇxᴛ ᴛᴏ sᴇᴛ ᴀs ʙɪᴏ.")


@Client.on_message(filters.command(["setpfp"], [".", "/"]) & filters.me)
async def set_pfp(client: Client, message: Message):
    replied = message.reply_to_message
    if (
        replied
        and replied.media
        and (
            replied.photo
            or (replied.document and "image" in replied.document.mime_type)
        )
    ):
        await client.download_media(message=replied, file_name=profile_photo)
        await client.set_profile_photo(profile_photo)
        if os.path.exists(profile_photo):
            os.remove(profile_photo)
        await message.reply_text("**ʏᴏᴜʀ ᴘʀᴏғɪʟᴇ ᴘʜᴏᴛᴏ ᴄʜᴀɴɢᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.**")
    else:
        await message.reply_text(
            "ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴘʜᴏᴛᴏ ᴛᴏ sᴇᴛ ᴀs ᴘʀᴏғɪʟᴇ ᴘʜᴏᴛᴏ"
        )
        await sleep(3)
        await message.delete()


@Client.on_message(filters.command(["vpfp"], [".", "/"]) & filters.me)
async def view_pfp(client: Client, message: Message):
    user_id = await extract_user(message)
    if user_id:
        user = await client.get_users(user_id)
    else:
        user = await client.get_me()
    if not user.photo:
        await message.reply_text("ᴘʀᴏғɪʟᴇ ᴘʜᴏᴛᴏ ɴᴏᴛ ғᴏᴜɴᴅ!")
        return
    await client.download_media(user.photo.big_file_id, file_name=profile_photo)
    await client.send_photo(
        message.chat.id, profile_photo, reply_to_message_id=ReplyCheck(message)
    )
    await message.delete()
    if os.path.exists(profile_photo):
        os.remove(profile_photo)


add_command_help(
    "profile",
    [
        ["block", "to block someone on telegram"],
        ["unblock", "to unblock someone on telegram"],
        ["setname", "set your profile name."],
        ["setbio", "set an bio."],
        [
            "setpfp",
            f"reply with image to set your profile pic.",
        ],
        ["vpfp", "Reply with video to set your video profile."],
    ],
)
