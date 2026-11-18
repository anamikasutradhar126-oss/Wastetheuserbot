import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from html import escape

from pyrogram import Client, filters, enums
from pyrogram.errors import SessionPasswordNeeded
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    InputMediaVideo,
)
from pymongo import MongoClient

from config import OWNER_ID, ALIVE_VIDEO, MONGO_URL
from Waste import app, API_ID, API_HASH, CMD_HELP
from Waste.modules.bot.premium import (
    PE_HOST,
    PE_COMMAND,
    PE_PAGE,
    PE_MAIN,
    PE_NEXT,
    pe,
    line,
    serendipity,
)

log = logging.getLogger(__name__)
user_sessions = {}
active_sessions = []

mongo_client = MongoClient(MONGO_URL)
db = mongo_client["SessionDB"]
sessions_col = db["UserSessions"]
subscriptions_col = db["Subscriptions"]
settings_col = db["UserSettings"]
recordings_col = db["UserRecordings"]

OWNER_USERNAME = "day1Nomore"
SUPPORT_USERNAME = "wasteBotz"
UPDATES_USERNAME = "wasteuserbotUpdates"


def html_link(text: str, url: str) -> str:
    return f'<a href="{escape(url, quote=True)}">{escape(text)}</a>'


def start_caption(user=None) -> str:
    name = escape((getattr(user, "first_name", "") or "").strip())
    if name:
        user_line = f"{name}"
    else:
        user_line = ""
    return "\n".join([
        line("<b>ＷＡＳＴＥ Ｘ 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐇𝐎ＳＴ</b>", PE_HOST),
        line(f"<b>ᴜꜱᴇʀ : {user_line}</b>"),
        line("<b>ꜱᴛᴀᴛᴜꜱ : ɪɴᴀᴄᴛɪᴠᴇ</b>"),
        line("<b>ᴡᴇʟᴄᴏᴍᴇ! ᴅᴇᴘʟᴏʏ ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ᴜꜱᴇʀʙᴏᴛ ɪɴꜱᴛᴀɴᴛʟʏ ᴡɪᴛʜ ꜱᴇᴄᴜʀᴇ ᴏᴛᴘ ʟᴏɢɪɴ.</b>"),
    ])


def button(label: str, callback_data: str = None, url: str = None):
    return InlineKeyboardButton(label, callback_data=callback_data, url=url)


class Data:
    donate_button = [button("ＤＯＮＡＴＥ", callback_data="donate")]
    generate_single_button = [button("ＢＡＳＩＣ ＧＵＩＤＥ", callback_data="guide")]
    home_buttons = [
        [button("ＷＡＳＴＥ ↗", url=f"https://t.me/{OWNER_USERNAME}"), button("ＡＢＯＵＴ", callback_data="about")],
        [button("ＨＥＬＰ", callback_data="help"), button("ＭＵＳＩＣ", callback_data="music")],
        [button("ＵＰＤＡＴＥＳ ↗", url=f"https://t.me/{UPDATES_USERNAME}"), button("ＳＵＰＰＯＲＴ ↗", url=f"https://t.me/{SUPPORT_USERNAME}")],
    ]
    back_buttons = [
        [button("ＭＡＩＮ ＭＥＮＵ", callback_data="home")],
    ]
    guide_buttons = [
        [button("/add", callback_data="start_add")],
        [button("ＭＡＩＮ ＭＥＮＵ", callback_data="home")],
    ]
    HELP = "\n".join([
        line("<b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ʜᴇʟᴘ</b>"),
        line("<b>ᴜsᴇ /add ᴛᴏ ʟᴏɢɪɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ.</b>"),
        line("<b>ᴜsᴇ /help ᴛᴏ ᴏᴘᴇɴ ᴛʜᴇ ғᴜʟʟ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇɴᴜ.</b>"),
    ])
    GUIDE = "\n".join([
        line("<b>ＢＡＳＩＣ ＧＵＩＤＥ</b>"),
        line("<b>ᴜsᴇ /add ᴛᴏ ʟᴏɢɪɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ.</b>"),
        line("<b>ᴀғᴛᴇʀ ᴄᴏɴɴᴇᴄᴛɪɴɢ, ᴜsᴇ /help ᴛᴏ ᴏᴘᴇɴ ᴛʜᴇ ғᴜʟʟ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇɴᴜ.</b>"),
        line("<b>ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ . ᴏʀ / ᴡʜᴇʀᴇ sᴜᴘᴘᴏʀᴛᴇᴅ.</b>"),
    ])
    ABOUT = "\n".join([
        line("<b>ＷＡＳＴＥ Ｘ ＵＢＯＴ</b>"),
        line("<b>ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴛᴏ ʜᴏsᴛ ᴀ ᴜsᴇʀʙᴏᴛ ᴡɪᴛʜ ᴍᴜʟᴛɪᴘʟᴇ ᴘʟᴜɢɪɴs.</b>"),
        line(f"<b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ : {html_link('ＷＡＳＴＥ', 'https://t.me/wasteBotz')}</b>"),
        line(f"<b>ᴜᴘᴅᴀᴛᴇs : {html_link('ＷＡＳＴＥ ＵＰＤＡＴＥＳ', 'https://t.me/wasteuserbotUpdates')}</b>"),
    ])
    DONATE = "\n".join([
        line("<b>ＤＯＮＡＴＥ / ＳＵＰＰＯＲＴ</b>"),
        line("<b>ᴜᴘɪ ɪᴅ » JOYZZ@FAM</b>"),
        line(f"<b>ᴄᴏɴᴛᴀᴄᴛ » {html_link('ᴏᴡɴᴇʀ', 'https://t.me/day1Nomore')}</b>"),
    ])


def _session_doc(uid):
    return sessions_col.find_one({"_id": uid})


def _is_owner(message):
    return bool(message.from_user and message.from_user.id == OWNER_ID)


def _parse_target(parts):
    user_id = None
    username = None
    for part in parts:
        p = part.strip().lstrip("@")
        if p.lstrip("-").isdigit() and user_id is None:
            user_id = int(p)
        elif p and username is None:
            username = p
    return user_id, username


def _sub_active(uid):
    doc = subscriptions_col.find_one({"_id": int(uid)})
    if not doc:
        return False, None
    expires = doc.get("expires_at")
    if isinstance(expires, datetime):
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires > datetime.now(timezone.utc):
            return True, expires
        subscriptions_col.delete_one({"_id": int(uid)})
    return False, None


async def send_start(client, chat_id, user):
    return await client.send_video(
        chat_id,
        ALIVE_VIDEO,
        caption=start_caption(user),
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(Data.home_buttons),
    )


async def edit_start(message, user, markup=None):
    return await message.edit_media(
        InputMediaVideo(
            ALIVE_VIDEO,
            caption=start_caption(user),
            parse_mode=enums.ParseMode.HTML,
        ),
        reply_markup=markup or InlineKeyboardMarkup(Data.home_buttons),
    )


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await send_start(client, message.chat.id, message.from_user)


@app.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    await message.reply_text(Data.HELP, reply_markup=InlineKeyboardMarkup(Data.back_buttons), parse_mode=enums.ParseMode.HTML)


@app.on_message(filters.command("about") & filters.private)
async def about_command(client: Client, message: Message):
    await message.reply_text(Data.ABOUT, reply_markup=InlineKeyboardMarkup(Data.back_buttons), parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex(r"^(home|help|about|donate|guide|music|start_add)$"))
async def callback_handler(client: Client, query: CallbackQuery):
    await query.answer()
    data = query.data
    if data == "home":
        await edit_start(query.message, query.from_user, InlineKeyboardMarkup(Data.home_buttons))
    elif data == "help":
        await query.message.edit_media(InputMediaVideo(ALIVE_VIDEO, caption=Data.HELP, parse_mode=enums.ParseMode.HTML), reply_markup=InlineKeyboardMarkup(Data.back_buttons))
    elif data == "about":
        await query.message.edit_media(InputMediaVideo(ALIVE_VIDEO, caption=Data.ABOUT, parse_mode=enums.ParseMode.HTML), reply_markup=InlineKeyboardMarkup(Data.back_buttons))
    elif data == "donate":
        await query.message.edit_media(InputMediaVideo(ALIVE_VIDEO, caption=Data.DONATE, parse_mode=enums.ParseMode.HTML), reply_markup=InlineKeyboardMarkup(Data.back_buttons))
    elif data == "guide":
        await query.message.edit_media(InputMediaVideo(ALIVE_VIDEO, caption=Data.GUIDE, parse_mode=enums.ParseMode.HTML), reply_markup=InlineKeyboardMarkup(Data.guide_buttons))
    elif data == "music":
        await query.message.edit_media(InputMediaVideo(ALIVE_VIDEO, caption=music_caption(), parse_mode=enums.ParseMode.HTML), reply_markup=InlineKeyboardMarkup(Data.back_buttons))
    elif data == "start_add":
        uid = query.from_user.id
        if _session_doc(uid):
            return await query.message.reply_text(
                line("<b>ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ. ᴜsᴇ /remove ғɪʀsᴛ.</b>"),
                parse_mode=enums.ParseMode.HTML,
            )
        user_sessions[uid] = {"step": "awaiting_phone"}
        await query.message.reply_text(
            line("<b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪɴ ɪɴᴛᴇʀɴᴀᴛɪᴏɴᴀʟ ғᴏʀᴍᴀᴛ.</b>"),
            parse_mode=enums.ParseMode.HTML,
        )


def music_caption():
    return "\n".join([
        line("<b>ＭＵＳＩＣ</b>"),
        line("<b>ᴜsᴇ /play song name ᴏʀ .play song name ᴏɴ ʏᴏᴜʀ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ.</b>"),
        line("<b>ᴍᴜsɪᴄ ᴘʟᴀʏs ɪɴ ᴛʜᴇ ᴀᴄᴛɪᴠᴇ ɢʀᴏᴜᴘ ᴠᴄ.</b>"),
    ])


@app.on_message(filters.command("subscription") & filters.private & filters.user(OWNER_ID))
async def subscription_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /subscription <user_id> [username]")
    uid, username = _parse_target(message.command[1:])
    if uid is None:
        return await message.reply_text("User ID required. Example: /subscription 123456789 username")
    expires = datetime.now(timezone.utc) + timedelta(days=30)
    subscriptions_col.update_one({"_id": uid}, {"$set": {"user_id": uid, "username": username or "", "expires_at": expires, "activated_at": datetime.now(timezone.utc)}}, upsert=True)
    for hosted in list(active_sessions):
        if getattr(hosted, "_waste_owner_uid", None) == uid:
            try:
                from Waste.modules.basic.vcfight import _sub_cache, start_background_for_client
                _sub_cache.pop(id(hosted), None)
                await start_background_for_client(hosted)
            except Exception as exc:
                log.warning("Could not refresh VC premium state for %s: %s", uid, exc)
            try:
                from Waste.modules.basic.promotion import start_autotextpromo_if_enabled
                await start_autotextpromo_if_enabled(hosted)
            except Exception as exc:
                log.warning("Could not refresh promotion state for %s: %s", uid, exc)
    try:
        await client.send_message(uid, "Subscription Activated\n\nYour Promotion subscription is active for 30 days.")
    except Exception as exc:
        log.warning("Could not notify subscriber %s: %s", uid, exc)
    await message.reply_text(f"Subscription activated for `{uid}` for 30 days.\nExpires: `{expires.isoformat()}`")


@app.on_message(filters.command("disubscription") & filters.private & filters.user(OWNER_ID))
async def disubscription_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /disubscription <user_id> [username]")
    uid, username = _parse_target(message.command[1:])
    if uid is None:
        return await message.reply_text("User ID required.")
    result = subscriptions_col.delete_one({"_id": uid})
    settings_col.update_one({"_id": uid}, {"$set": {"allvc_auto": False, "autotextpromo": False}}, upsert=True)
    for hosted in list(active_sessions):
        if getattr(hosted, "_waste_owner_uid", None) == uid:
            try:
                from Waste.modules.basic.vcfight import disable_auto_allvc, _sub_cache
                _sub_cache.pop(id(hosted), None)
                await disable_auto_allvc(hosted)
            except Exception as exc:
                log.warning("Could not disable VC premium mode for %s: %s", uid, exc)
            try:
                from Waste.modules.basic.promotion import stop_autotextpromo
                await stop_autotextpromo(hosted)
            except Exception as exc:
                log.warning("Could not disable promotion mode for %s: %s", uid, exc)
    try:
        await client.send_message(uid, "Subscription Deactivated\n\nYour Promotion subscription has ended.")
    except Exception as exc:
        log.warning("Could not notify unsubscribed user %s: %s", uid, exc)
    await message.reply_text("Subscription removed." if result.deleted_count else "No active subscription found.")


@app.on_message(filters.command("clone") & filters.private)
async def clone(bot: Client, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply("Usage: /clone <session_string>")
    try:
        client = Client(name=f"Clone_{msg.from_user.id}", api_id=API_ID, api_hash=API_HASH, session_string=msg.command[1], plugins=dict(root="Waste/modules"), device_model="Waste", app_version="1.0")
        await client.start()
        user = await client.get_me()
        setattr(client, "_waste_owner_uid", msg.from_user.id)
        settings = settings_col.find_one({"_id": msg.from_user.id}) or {}
        setattr(client, "_auto_allvc_enabled", bool(settings.get("allvc_auto", False)))
        setattr(client, "_autotextpromo_enabled", bool(settings.get("autotextpromo", False)))
        active_sessions.append(client)
        try:
            from Waste.modules.basic.vcfight import start_background_for_client
            await start_background_for_client(client)
            from Waste.modules.basic.promotion import start_autotextpromo_if_enabled
            await start_autotextpromo_if_enabled(client)
        except Exception as exc:
            log.warning("Clone background start failed: %s", exc)
        await msg.reply(f"ʏᴏᴜ ᴀʀᴇ ʀᴇᴀᴅʏ ᴛᴏ ғɪɢʜᴛ\n\nᴀᴄᴄᴏᴜɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ\n\n{user.first_name}")
    except Exception as e:
        await msg.reply(f"ERROR: `{e}`")


@app.on_message(filters.command("add") & filters.private)
async def add_session_command(client: Client, message: Message):
    uid = message.from_user.id
    if _session_doc(uid):
        return await message.reply(
            line("<b>ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ. ᴜsᴇ /remove ғɪʀsᴛ.</b>"),
            parse_mode=enums.ParseMode.HTML,
        )
    await message.reply(
        line("<b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪɴ ɪɴᴛᴇʀɴᴀᴛɪᴏɴᴀʟ ғᴏʀᴍᴀᴛ.</b>"),
        parse_mode=enums.ParseMode.HTML,
    )
    user_sessions[uid] = {"step": "awaiting_phone"}


@app.on_message(filters.command("remove") & filters.private)
async def remove_session(client: Client, msg: Message):
    uid = msg.from_user.id
    for hosted in list(active_sessions):
        if getattr(hosted, "_waste_owner_uid", None) == uid or hosted.name == f"AutoClone_{uid}":
            try:
                await hosted.stop()
            except Exception:
                pass
            active_sessions.remove(hosted)
    result = sessions_col.delete_one({"_id": uid})
    await msg.reply(
        line("<b>ʏᴏᴜʀ sᴇssɪᴏɴ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.</b>" if result.deleted_count else "<b>ɴᴏ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ ғᴏᴜɴᴅ.</b>"),
        parse_mode=enums.ParseMode.HTML,
    )


@app.on_message()
async def session_handler(client: Client, msg: Message):
    if not msg.from_user or not msg.text:
        return
    uid = msg.from_user.id
    session = user_sessions.get(uid)
    if not session:
        return
    step = session.get("step")
    if step == "awaiting_phone":
        phone = msg.text.strip()
        temp = Client(name=f"gen_{uid}", api_id=API_ID, api_hash=API_HASH, in_memory=True, device_model="Waste", app_version="1.0")
        session.update({"phone": phone, "client": temp})
        try:
            await temp.connect()
            sent = await temp.send_code(phone)
            session["phone_code_hash"] = sent.phone_code_hash
            session["step"] = "awaiting_otp"
            await msg.reply(
                line("<b>ᴏᴛᴘ sᴇɴᴛ! sᴇɴᴅ ɪᴛ ʟɪᴋᴇ: `1 2 3 4 5`</b>"),
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception as e:
            await msg.reply(
                line(f"<b>ᴏᴛᴘ ᴇʀʀᴏʀ: <code>{escape(str(e))}</code></b>"),
                parse_mode=enums.ParseMode.HTML,
            )
            try:
                await temp.disconnect()
            except Exception:
                pass
            user_sessions.pop(uid, None)
    elif step == "awaiting_otp":
        temp = session["client"]
        try:
            await temp.sign_in(phone_number=session["phone"], phone_code_hash=session["phone_code_hash"], phone_code=msg.text.strip().replace(" ", ""))
        except SessionPasswordNeeded:
            session["step"] = "awaiting_2fa"
            return await msg.reply(
                line("<b>sᴇɴᴅ ʏᴏᴜʀ 2ғᴀ ᴘᴀssᴡᴏʀᴅ.</b>"),
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception as e:
            await msg.reply(
                line(f"<b>ʟᴏɢɪɴ ғᴀɪʟᴇᴅ: <code>{escape(str(e))}</code></b>"),
                parse_mode=enums.ParseMode.HTML,
            )
            try:
                await temp.disconnect()
            except Exception:
                pass
            user_sessions.pop(uid, None)
            return
        await finalize_login(temp, msg, uid)
    elif step == "awaiting_2fa":
        temp = session["client"]
        try:
            await temp.check_password(msg.text.strip())
            await finalize_login(temp, msg, uid)
        except Exception as e:
            await msg.reply(
                line(f"<b>2ғᴀ ғᴀɪʟᴇᴅ: <code>{escape(str(e))}</code></b>"),
                parse_mode=enums.ParseMode.HTML,
            )
            try:
                await temp.disconnect()
            except Exception:
                pass
            user_sessions.pop(uid, None)


async def start_hosted_session(uid, string, notify=False):
    for c in active_sessions:
        if getattr(c, "_waste_owner_uid", None) == uid:
            return c
    hosted = Client(name=f"AutoClone_{uid}", api_id=API_ID, api_hash=API_HASH, session_string=string, plugins=dict(root="Waste/modules"), device_model="Waste", app_version="1.0")
    setattr(hosted, "_waste_owner_uid", uid)
    await hosted.start()
    try:
        settings = settings_col.find_one({"_id": uid}) or {}
        setattr(hosted, "_auto_allvc_enabled", bool(settings.get("allvc_auto", False)))
        setattr(hosted, "_autotextpromo_enabled", bool(settings.get("autotextpromo", False)))
        if "welcome_enabled" not in settings:
            settings_col.update_one({"_id": uid}, {"$set": {"welcome_enabled": True}}, upsert=True)
    except Exception:
        setattr(hosted, "_auto_allvc_enabled", False)
        setattr(hosted, "_autotextpromo_enabled", False)
    active_sessions.append(hosted)
    try:
        from Waste.modules.basic.vcfight import start_background_for_client
        await start_background_for_client(hosted)
    except Exception as exc:
        log.warning("VC background start failed for %s: %s", uid, exc)
    try:
        from Waste.modules.basic.promotion import start_autotextpromo_if_enabled
        await start_autotextpromo_if_enabled(hosted)
    except Exception as exc:
        log.warning("Promotion background start failed for %s: %s", uid, exc)
    try:
        from Waste.modules.basic.auto_setup import run_after_connect
        asyncio.create_task(run_after_connect(hosted))
    except Exception as exc:
        log.warning("Post-connect setup failed for %s: %s", uid, exc)
    if notify:
        try:
            await app.send_message(uid, line("<b>ᴜsᴇʀʙᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ</b>\n\n<b>ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ɪs ɴᴏᴡ ᴏɴʟɪɴᴇ ᴡɪᴛʜ ᴡᴀsᴛᴇ x ᴜsᴇʀʙᴏᴛ.</b>"), parse_mode=enums.ParseMode.HTML)
        except Exception as exc:
            log.warning("Notification failed for %s: %s", uid, exc)
    return hosted


async def finalize_login(client: Client, msg: Message, uid: int):
    try:
        string = await client.export_session_string()
        user = await client.get_me()
        sessions_col.update_one({"_id": uid}, {"$set": {"session": string, "name": user.first_name, "user_id": user.id, "username": user.username}}, upsert=True)
        await start_hosted_session(uid, string, notify=False)
        await msg.reply(
            line(f"<b>ʟᴏɢɢᴇᴅ ɪɴ ᴀs {escape(user.first_name or '')}.</b>") + "\n" +
            line("<b>ᴀᴜᴛᴏ-ʜᴏsᴛ ɴᴏᴡ ᴏɴ.</b>"),
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception as e:
        await msg.reply(line(f"<b>ғɪɴᴀʟ sᴛᴇᴘ ғᴀɪʟᴇᴅ: <code>{escape(str(e))}</code></b>"), parse_mode=enums.ParseMode.HTML)
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
        user_sessions.pop(uid, None)


async def restore_saved_sessions():
    for doc in sessions_col.find({"session": {"$exists": True}}):
        uid = int(doc["_id"])
        try:
            await start_hosted_session(uid, doc["session"], notify=True)
            log.info("Restored hosted session for %s", uid)
        except Exception as exc:
            log.warning("Could not restore session for %s: %s", uid, exc)
