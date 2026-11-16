import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from pyrogram import Client, filters, enums
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeExpired, PhoneCodeInvalid
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, InputMediaVideo
from pymongo import MongoClient

from config import OWNER_ID, ALIVE_PIC, MONGO_URL
from Waste import app, API_ID, API_HASH

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
FORCE_SUPPORT = "wasteBotz"
FORCE_UPDATES = "wasteuserbotUpdates"
START_VIDEO_URL = "https://www.image2url.com/r2/default/videos/1794758121681-9a91954b-c9c6-4323-9fd0-9bf9e42ed0fa.mp4"
PREMIUM_MAIN = "5989952280823076303"
PREMIUM_START = "5989975649740134220"
PREMIUM_HELP = "5992130701120507687"

def _ce(emoji_id, fallback="✦"):
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


class Data:
    donate_button = [InlineKeyboardButton("⛈️ ᴅσηᴧᴛє ⛈️", callback_data="donate")]
    generate_single_button = [InlineKeyboardButton("⛈️ ʙᴀsɪᴄ ɢᴜɪᴅᴇ ⛈️", callback_data="guide")]
    home_buttons = [generate_single_button, [InlineKeyboardButton("🏠 ʀᴇᴛᴜʀɴ ʜᴏᴍᴇ 🏠", callback_data="home")]]
    back_buttons = [donate_button, [InlineKeyboardButton("🏠 ʀᴇᴛᴜʀɴ ʜᴏᴍᴇ 🏠", callback_data="home")]]
    guide_buttons = [[InlineKeyboardButton("🏠 ʀᴇᴛᴜʀɴ ʜᴏᴍᴇ 🏠", callback_data="home")]]
    buttons = [
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ BASIC GUIDE", callback_data="guide")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ WASTE", url=f"https://t.me/{OWNER_USERNAME}"), InlineKeyboardButton("ᴅᴇᴘʟᴏʏ ABOUT", callback_data="about")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ HELP", callback_data="force_menu"), InlineKeyboardButton("ᴅᴇᴘʟᴏʏ MUSIC", callback_data="botforce:music")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ UPDATE'S", url=f"https://t.me/{FORCE_UPDATES}"), InlineKeyboardButton("ᴅᴇᴘʟᴏʏ SUPPORT", url=f"https://t.me/{FORCE_SUPPORT}")],
    ]
    START = f"""<blockquote>{_ce(PREMIUM_START)} <b>ＷＡＳＴＥ Ｘ 𝐔𝐒𝐄𝐑𝐁𝐎𝐓</b>

{_ce(PREMIUM_MAIN)} <b>┃ Hey, I am : <a href="https://t.me/Wasteuserrbot">WASTE X UBOT</a></b>
{_ce(PREMIUM_MAIN)} <b>┃ Nice to meet you! 💜</b>

{_ce(PREMIUM_HELP)} <b>✦ I am a Powerful Id-User-Bot</b>
{_ce(PREMIUM_HELP)} <b>✦ You can use me for fun.</b>
{_ce(PREMIUM_HELP)} <b>✦ I can boost your ID.</b>

{_ce(PREMIUM_HELP)} <b>✦ By : <a href="https://t.me/day1Nomore">WASTE OWNER</a> 👑</b></blockquote>"""
    HELP = """<blockquote>❁ <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ - ＨＥＬＰ ＭＥＮＵ</b> ❁

📚 <b>Available:</b>

/start — Start the bot
/help — Open help menu
/about — About the bot and owner
/add — Auto-host your account
/clone — Clone via string session
/remove — Logout from bot

<b>Userbot:</b> <code>.help</code> / <code>/help</code></blockquote>"""
    GUIDE = """**❖ ʜᴇʏ ᴅᴇᴀʀ, ᴛʜɪs ɪs ᴀ ǫᴜɪᴄᴋ ɢᴜɪᴅᴇ ᴛᴏ ʜᴏsᴛɪɴɢ ᴡᴀsᴛᴇ Uꜱᴇʀʙᴏᴛ**

**1)** sᴇɴᴅ /add
**2)** sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪɴ ɪɴᴛᴇʀɴᴀᴛɪᴏɴᴀʟ ғᴏʀᴍᴀᴛ
**3)** sᴇɴᴅ ᴛʜᴇ ᴏᴛᴘ ᴡɪᴛʜ sᴘᴀᴄᴇs, ᴛʜᴇɴ 2ғᴀ ɪғ ᴇɴᴀʙʟᴇᴅ

**ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴡɪʟʟ ʙᴇ ʜᴏsᴛᴇᴅ ᴀғᴛᴇʀ ʟᴏɢɪɴ.**"""
    ABOUT = """**ᴀʙᴏᴜᴛ ᴛʜɪꜱ ʙᴏᴛ** 🌙

**ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴛᴏ ʜᴏsᴛ ᴀ ᴜsᴇʀʙᴏᴛ ᴡɪᴛʜ ᴍᴜʟᴛɪᴘʟᴇ ᴘʟᴜɢɪɴs.**

**ᴘᴏᴡᴇʀᴇᴅ ʙʏ : [ᴡᴀsᴛᴇ ꭙ ʙᴏᴛs](https://t.me/wasteBotz)**
**ᴅᴇᴠᴇʟᴏᴘᴇʀ : [ᴡᴀsᴛᴇ](https://t.me/day1Nomore)**"""
    DONATE = """**❖ ᴅᴏɴᴀᴛᴇ / sᴜᴘᴘᴏʀᴛ**

**• ᴜᴘɪ ɪᴅ »** `JOYZZ@FAM`
**• ᴄᴏɴᴛᴀᴄᴛ »** [ᴏᴡɴᴇʀ](https://t.me/day1Nomore)"""


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


async def _force_joined(client: Client, user_id: int) -> bool:
    for channel in (f"@{FORCE_SUPPORT}", f"@{FORCE_UPDATES}"):
        try:
            member = await client.get_chat_member(channel, user_id)
            status = getattr(member.status, "value", member.status)
            if status in {"left", "kicked", "banned"}:
                return False
        except Exception:
            # Force-join must fail closed: if membership cannot be verified,
            # do not bypass the gate.
            return False
    return True


def _force_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ SUPPORT ➜", url=f"https://t.me/{FORCE_SUPPORT}")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ UPDATES ➜", url=f"https://t.me/{FORCE_UPDATES}")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ CHECK AGAIN", callback_data="start_force_check")],
    ])


FORCE_CAPTION = f"""<blockquote>{_ce(PREMIUM_MAIN)} <b>WASTE X USERBOT</b>

{_ce(PREMIUM_MAIN)} <b>ᴜꜱᴇʀ : 𝐉 𝐏 𝐄 𝐗 𝐎 🚩</b>
{_ce(PREMIUM_MAIN)} <b>ꜱᴛᴀᴛᴜꜱ : ❌ ɪɴᴀᴄᴛɪᴠᴇ</b>

{_ce(PREMIUM_MAIN)} <i>ᴡᴇʟᴄᴏᴍᴇ! ᴅᴇᴘʟᴏʏ ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ᴜꜱᴇʀʙᴏᴛ ɪɴꜱᴛᴀɴᴛʟʏ ᴡɪᴛʜ ꜱᴇᴄᴜʀᴇ ᴏᴛᴘ ʟᴏɢɪɴ.</i></blockquote>"""


async def _send_start_or_force(client: Client, message: Message):
    if not await _force_joined(client, message.from_user.id):
        try:
            return await client.send_video(message.chat.id, START_VIDEO_URL, caption=FORCE_CAPTION, reply_markup=_force_markup(), parse_mode=enums.ParseMode.HTML, supports_streaming=True)
        except Exception:
            return await client.send_photo(message.chat.id, ALIVE_PIC, caption=FORCE_CAPTION, reply_markup=_force_markup(), parse_mode=enums.ParseMode.HTML)
    try:
        return await client.send_video(message.chat.id, START_VIDEO_URL, caption=Data.START, reply_markup=InlineKeyboardMarkup(Data.buttons), parse_mode=enums.ParseMode.HTML, supports_streaming=True)
    except Exception:
        return await client.send_photo(message.chat.id, ALIVE_PIC, caption=Data.START, reply_markup=InlineKeyboardMarkup(Data.buttons), parse_mode=enums.ParseMode.HTML)


@app.on_message(filters.command("start", [".", "/"]) & filters.private)
async def start_handler(client: Client, message: Message):
    await _send_start_or_force(client, message)


BOT_FORCE_TEXT = f"""<blockquote>{_ce(PREMIUM_HELP)} <b>ＷＡＳＴＥ Ｘ 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 — ᴅᴇᴘʟᴏʏ FORCE COMMANDS</b>\n\n{_ce(PREMIUM_HELP)} Choose a command/module below to open its details.\n{_ce(PREMIUM_HELP)} Tap any command to view its usage.\n{_ce(PREMIUM_HELP)} Music, VcFight and Recordings have their own command pages.\n{_ce(PREMIUM_HELP)} Use <code>.help &lt;command&gt;</code> from a connected ID for direct details.</blockquote>"""


def _bot_force_keys():
    try:
        from Waste.modules.help.help import HELP_COMMANDS
        return list(HELP_COMMANDS)
    except Exception:
        return ["Autopic", "admin", "afk", "animation", "aichat", "autoreact", "mmar", "omar", "promotion", "vctalk", "vctools", "weather"]


def _bot_force_keyboard(page=0):
    keys = _bot_force_keys()
    per_page = 12
    total = 6
    page = max(0, min(int(page), total - 1))
    rows = [
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ MUSIC / SONG", callback_data="botforce:music"), InlineKeyboardButton("ᴅᴇᴘʟᴏʏ VCFIGHT", callback_data="botforce:vcfight")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ RECORDINGS", callback_data="botforce:recordings"), InlineKeyboardButton("ᴅᴇᴘʟᴏʏ AUTOTEXTPROMO", callback_data="botforce:autotextpromo")],
    ]
    chunk = keys[page * per_page:(page + 1) * per_page]
    for i in range(0, len(chunk), 2):
        row = [InlineKeyboardButton(f"✦ {chunk[i]}", callback_data=f"botforce:cmd:{chunk[i]}")]
        if i + 1 < len(chunk):
            row.append(InlineKeyboardButton(f"✦ {chunk[i+1]}", callback_data=f"botforce:cmd:{chunk[i+1]}"))
        rows.append(row)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ PREV", callback_data=f"botforce:page:{page-1}"))
    nav.append(InlineKeyboardButton(f"PAGE {page+1}/{total}", callback_data="botforce:noop"))
    if page < total - 1:
        nav.append(InlineKeyboardButton("ᴅᴇᴘʟᴏʏ NEXT ➜", callback_data=f"botforce:page:{page+1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton("🏠 MAIN MENU", callback_data="home")])
    return InlineKeyboardMarkup(rows)


def _bot_force_media_kwargs():
    return dict(caption=BOT_FORCE_TEXT, parse_mode=enums.ParseMode.HTML, supports_streaming=True)


@app.on_message(filters.command("force", [".", "/"]) & filters.private)
async def force_handler(client: Client, message: Message):
    if not await _force_joined(client, message.from_user.id):
        try:
            return await client.send_video(message.chat.id, START_VIDEO_URL, caption=FORCE_CAPTION, reply_markup=_force_markup(), parse_mode=enums.ParseMode.HTML, supports_streaming=True)
        except Exception:
            return await client.send_photo(message.chat.id, ALIVE_PIC, caption=FORCE_CAPTION, reply_markup=_force_markup(), parse_mode=enums.ParseMode.HTML)
    try:
        return await client.send_video(message.chat.id, START_VIDEO_URL, reply_markup=_bot_force_keyboard(0), **_bot_force_media_kwargs())
    except Exception:
        return await client.send_photo(message.chat.id, ALIVE_PIC, caption=BOT_FORCE_TEXT, reply_markup=_bot_force_keyboard(0), parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex(r"^botforce:"))
async def bot_force_callback(client: Client, query: CallbackQuery):
    await query.answer()
    data = query.data.split(":", 1)[1]
    if data == "noop":
        return
    if data == "menu":
        try:
            return await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=BOT_FORCE_TEXT, parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=_bot_force_keyboard(0))
        except Exception:
            return await query.message.edit_text(BOT_FORCE_TEXT, reply_markup=_bot_force_keyboard(0), parse_mode=enums.ParseMode.HTML)
    if data.startswith("page:"):
        page = int(data.split(":", 1)[1])
        try:
            return await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=BOT_FORCE_TEXT, parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=_bot_force_keyboard(page))
        except Exception:
            return await query.message.edit_text(BOT_FORCE_TEXT, reply_markup=_bot_force_keyboard(page), parse_mode=enums.ParseMode.HTML)
    if data in {"music", "vcfight", "recordings", "autotextpromo"}:
        from Waste.modules.help.help import _find_help_key, _module_text
        key = {"music": "Music", "vcfight": "VcFight", "recordings": "VcFight", "autotextpromo": "AutoTextPromo"}[data]
        text = _module_text(_find_help_key(key) or key)
    elif data.startswith("cmd:"):
        from Waste.modules.help.help import _find_help_key, _module_text
        raw = data.split(":", 1)[1]
        key = _find_help_key(raw) or raw
        text = _module_text(key)
    else:
        return
    await query.message.edit_caption(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="botforce:menu")]]), parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex(r"^start_force_check$"))
async def start_force_check(client: Client, query: CallbackQuery):
    if not await _force_joined(client, query.from_user.id):
        await query.answer("Please join both channels first.", show_alert=True)
        return
    await query.answer("Joined successfully ✓")
    await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=Data.START, parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=InlineKeyboardMarkup(Data.buttons))

@app.on_message(filters.command("about", [".", "/"]) & filters.private)
async def about_command(client: Client, message: Message):
    await message.reply_text(Data.ABOUT, reply_markup=InlineKeyboardMarkup(Data.home_buttons))

@app.on_callback_query(filters.regex(r"^(home|help|force_menu|about|donate|guide)$"))
async def callback_handler(client: Client, query: CallbackQuery):
    await query.answer()
    data = query.data
    if data == "home":
        try:
            await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=Data.START, parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=InlineKeyboardMarkup(Data.buttons))
        except Exception:
            await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.START, parse_mode=enums.ParseMode.HTML), reply_markup=InlineKeyboardMarkup(Data.buttons))
    elif data in {"help", "force_menu"}:
        try:
            await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=BOT_FORCE_TEXT, parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=_bot_force_keyboard(0))
        except Exception:
            await query.message.edit_text(BOT_FORCE_TEXT, reply_markup=_bot_force_keyboard(0), parse_mode=enums.ParseMode.HTML)
    elif data == "about":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.ABOUT, parse_mode=enums.ParseMode.HTML), reply_markup=InlineKeyboardMarkup(Data.home_buttons))
    elif data == "donate":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.DONATE, parse_mode=enums.ParseMode.HTML), reply_markup=InlineKeyboardMarkup(Data.guide_buttons))
    elif data == "guide":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.GUIDE, parse_mode=enums.ParseMode.HTML), reply_markup=InlineKeyboardMarkup(Data.back_buttons))

@app.on_message(filters.command(["play", "vplay"], [".", "/"]) & filters.group)
async def group_play_command(client: Client, message: Message):
    parts = message.text.split(None, 1) if message.text else []
    query = parts[1].strip() if len(parts) > 1 else ""
    if not query:
        return await message.reply_text("🎵 Usage: /play song name")
    if not active_sessions:
        return await message.reply_text("❌ No connected ID is online right now.")

    hosted = None
    # The bot is only the control interface. Prefer the connected account
    # belonging to the person who issued the command, then fall back to an
    # account that is a member of the group.
    requester_id = message.from_user.id if message.from_user else None
    if requester_id is not None:
        for candidate in list(active_sessions):
            if getattr(candidate, "_waste_owner_uid", None) == requester_id:
                hosted = candidate
                break
    if hosted is None:
        for candidate in list(active_sessions):
            try:
                member = await candidate.get_chat_member(message.chat.id, "me")
                status = getattr(member.status, "value", member.status)
                if status not in {"left", "kicked", "banned"}:
                    hosted = candidate
                    break
            except Exception:
                continue
    hosted = hosted or active_sessions[0]

    status = await message.reply_text("🔎 Searching YouTube...")
    path = None
    try:
        from Waste.modules.basic.playvc import play_song_in_chat
        path, info = await play_song_in_chat(hosted, message.chat.id, query)
        title = info.get("title") or query
        duration = info.get("duration_string") or "Unknown"
        await status.edit_text(f"▶️ Now Playing\n\n🎵 {title}\n⏱️ {duration}\n🔊 Playing in this group's Voice Chat")
        seconds = info.get("duration") or 0
        if seconds:
            await asyncio.sleep(min(float(seconds) + 10, 60 * 60 * 4))
        else:
            await asyncio.sleep(60 * 60 * 4)
    except Exception as exc:
        await status.edit_text(f"❌ Music failed: `{type(exc).__name__}`\n\n`{str(exc)[:500]}`")
    finally:
        if path:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass


@app.on_message(filters.command("subscription", [".", "/"]) & filters.private & filters.user(OWNER_ID))
async def subscription_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /subscription <user_id> [username]")
    uid, username = _parse_target(message.command[1:])
    if uid is None:
        return await message.reply_text("❌ User ID required. Example: /subscription 123456789 username")
    expires = datetime.now(timezone.utc) + timedelta(days=30)
    subscriptions_col.update_one({"_id": uid}, {"$set": {"user_id": uid, "username": username or "", "expires_at": expires, "activated_at": datetime.now(timezone.utc)}}, upsert=True)
    # Restart premium background features immediately if this account is online.
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
        await client.send_message(uid, "✅ **Subscription Activated**\n\nYour Promotion subscription is active for **30 days**.")
    except Exception as exc:
        log.warning("Could not notify subscriber %s: %s", uid, exc)
    await message.reply_text(f"✅ Subscription activated for `{uid}` for 30 days.\nExpires: `{expires.isoformat()}`")

@app.on_message(filters.command("disubscription", [".", "/"]) & filters.private & filters.user(OWNER_ID))
async def disubscription_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /disubscription <user_id> [username]")
    uid, username = _parse_target(message.command[1:])
    if uid is None:
        return await message.reply_text("❌ User ID required.")
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
        await client.send_message(uid, "⚠️ **Subscription Deactivated**\n\nYour Promotion subscription has ended. Contact @day1Nomore to reactivate it.")
    except Exception as exc:
        log.warning("Could not notify unsubscribed user %s: %s", uid, exc)
    await message.reply_text("✅ Subscription removed." if result.deleted_count else "ℹ️ No active subscription found.")

@app.on_message(filters.command("clone", [".", "/"]) & filters.private)
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
        await msg.reply(f"❖ ɴᴏᴡ ʏᴏᴜ ᴀʀᴇ ʀᴇᴀᴅʏ ᴛᴏ ғɪɢʜᴛ\n\n❍ ᴀᴄᴄᴏᴜɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ\n\n❖ {user.first_name}")
    except Exception as e:
        await msg.reply(f"**ERROR:** `{e}`")

@app.on_message(filters.command("add", [".", "/"]) & filters.private)
async def add_session_command(client: Client, message: Message):
    uid = message.from_user.id
    if _session_doc(uid):
        return await message.reply("⚠️ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ. ᴜsᴇ /remove ғɪʀsᴛ.")
    # A previous expired/failed login must never leave a stale wizard behind.
    old = user_sessions.pop(uid, None)
    if old and old.get("client"):
        try:
            await old["client"].disconnect()
        except Exception:
            pass
    await message.reply("📲 ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪɴ ɪɴᴛᴇʀɴᴀᴛɪᴏɴᴀʟ ғᴏʀᴍᴀᴛ (e.g. +918200000009):")
    user_sessions[uid] = {"step": "awaiting_phone"}

@app.on_message(filters.command("remove", [".", "/"]) & filters.private)
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
    await msg.reply("✅ ʏᴏᴜʀ sᴇssɪᴏɴ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ." if result.deleted_count else "❌ ɴᴏ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ ғᴏᴜɴᴅ.")

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
            await msg.reply("📨 OTP sᴇɴᴛ! sᴇɴᴅ ɪᴛ ʟɪᴋᴇ: `1 2 3 4 5`")
        except Exception as e:
            await msg.reply(f"❌ OTP error: `{e}`\nPlease use /add again.")
            try: await temp.disconnect()
            except Exception: pass
            user_sessions.pop(uid, None)
    elif step == "awaiting_otp":
        temp = session["client"]
        try:
            await temp.sign_in(phone_number=session["phone"], phone_code_hash=session["phone_code_hash"], phone_code=msg.text.strip().replace(" ", ""))
        except SessionPasswordNeeded:
            session["step"] = "awaiting_2fa"
            return await msg.reply("🔐 sᴇɴᴅ ʏᴏᴜʀ 2FA ᴘᴀssᴡᴏʀᴅ.")
        except (PhoneCodeExpired, PhoneCodeInvalid) as e:
            await msg.reply(f"❌ OTP login failed: `{e}`\nPlease use /add again and enter the newest OTP.")
            try: await temp.disconnect()
            except Exception: pass
            user_sessions.pop(uid, None)
            return
        except Exception as e:
            await msg.reply(f"❌ Login failed: `{e}`\nPlease use /add again.")
            try: await temp.disconnect()
            except Exception: pass
            user_sessions.pop(uid, None)
            return
        await finalize_login(temp, msg, uid)
    elif step == "awaiting_2fa":
        temp = session["client"]
        try:
            await temp.check_password(msg.text.strip())
            await finalize_login(temp, msg, uid)
        except Exception as e:
            await msg.reply(f"❌ Incorrect 2FA password: `{e}`\nPlease use /add again.")
            try: await temp.disconnect()
            except Exception: pass
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
        asyncio_task = __import__("asyncio").create_task(run_after_connect(hosted))
    except Exception as exc:
        log.warning("Post-connect setup failed for %s: %s", uid, exc)
    if notify:
        try:
            await app.send_message(uid, "✅ **Userbot Connected**\n\nYour account is now online with the Waste X Userbot features.")
        except Exception as exc:
            log.warning("Notification failed for %s: %s", uid, exc)
    return hosted

async def finalize_login(client: Client, msg: Message, uid: int):
    try:
        string = await client.export_session_string()
        user = await client.get_me()
        sessions_col.update_one({"_id": uid}, {"$set": {"session": string, "name": user.first_name, "user_id": user.id, "username": user.username}}, upsert=True)
        await start_hosted_session(uid, string, notify=False)
        await msg.reply(f"✅ ʟᴏɢɢᴇᴅ ɪɴ ᴀs **{user.first_name}**.\n\nᴀᴜᴛᴏ-ʜᴏsᴛ ɴᴏᴡ ᴏɴ.\n\nUss account me `.help` se commands dekho.")
    except Exception as e:
        await msg.reply(f"❌ ғɪɴᴀʟ sᴛᴇᴘ ғᴀɪʟᴇᴅ: `{e}`")
    finally:
        try: await client.disconnect()
        except Exception: pass
        user_sessions.pop(uid, None)

async def restore_saved_sessions():
    for doc in sessions_col.find({"session": {"$exists": True}}):
        uid = int(doc["_id"])
        try:
            await start_hosted_session(uid, doc["session"], notify=True)
            log.info("Restored hosted session for %s", uid)
        except Exception as exc:
            log.warning("Could not restore session for %s: %s", uid, exc)

