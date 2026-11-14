import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
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


class Data:
    donate_button = [InlineKeyboardButton("⛈️ ᴅσηᴧᴛє ⛈️", callback_data="donate")]
    generate_single_button = [InlineKeyboardButton("⛈️ ʙᴀsɪᴄ ɢᴜɪᴅᴇ ⛈️", callback_data="guide")]
    home_buttons = [generate_single_button, [InlineKeyboardButton("🏠 ʀᴇᴛᴜʀɴ ʜᴏᴍᴇ 🏠", callback_data="home")]]
    back_buttons = [donate_button, [InlineKeyboardButton("🏠 ʀᴇᴛᴜʀɴ ʜᴏᴍᴇ 🏠", callback_data="home")]]
    guide_buttons = [[InlineKeyboardButton("🏠 ʀᴇᴛᴜʀɴ ʜᴏᴍᴇ 🏠", callback_data="home")]]
    buttons = [
        generate_single_button,
        [InlineKeyboardButton("🕸️ ᴡᴀsᴛᴇ", url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("📚 ʜᴇʟᴘ", callback_data="force_menu"), InlineKeyboardButton("ᴀʙᴏᴜᴛ 🎶", callback_data="about")],
        [InlineKeyboardButton("⚡ ᴜᴘᴅᴀᴛᴇ's", url=f"https://t.me/{SUPPORT_USERNAME}"), InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ ⛈️", url=f"https://t.me/{SUPPORT_USERNAME}")],
        [InlineKeyboardButton("🌿 ʙᴏᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ 🌿", url=f"https://t.me/{OWNER_USERNAME}")],
    ]
    START = """**┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼ ⏤͟͟͞͞‌‌‌‌★**
**┆◍ ʜᴇʏ, ɪ ᴀᴍ : [ᴡᴀsᴛᴇ ꭙ 𝐔sᴇʀвσᴛ](https://t.me/Wasteuserrbot)**
**┆● ɴɪᴄᴇ ᴛᴏ ᴍᴇᴇᴛ ʏᴏᴜ !**
**└────────────────────────•**
**❖ ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ ɪᴅ-ᴜsᴇʀ-ʙᴏᴛ**
**❖ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ ғᴏʀ ғᴜɴ.**
**❖ ɪ ᴄᴀɴ ʙᴏᴏsᴛ ʏᴏᴜʀ ɪᴅ**
**•─────────────────────────•**
**❖ ʙʏ : [ᴡᴀsᴛᴇ ꭙ ᴏᴡɴᴇʀ](https://t.me/day1Nomore) 🚩**"""
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
        [InlineKeyboardButton("🛡️  JOIN SUPPORT  ➜", url=f"https://t.me/{FORCE_SUPPORT}")],
        [InlineKeyboardButton("📢  JOIN UPDATES  ➜", url=f"https://t.me/{FORCE_UPDATES}")],
        [InlineKeyboardButton("💚  ✅ CHECK AGAIN  💚", callback_data="start_force_check")],
    ])


FORCE_CAPTION = """<blockquote><b>👑 WASTE X UBOT — ACCESS REQUIRED 👑</b>

🔐 <b>Welcome to WASTE X UBOT</b>

To unlock the bot, join both official channels below.

🛡️ <b>Support</b> — @wasteBotz
📢 <b>Updates</b> — @wasteuserbotUpdates

✨ After joining both channels, press <b>CHECK AGAIN</b>.

⚡ <i>Powerful • Fast • Secure</i></blockquote>"""


async def _send_force_screen(client: Client, message: Message):
    """Always return a visible response when /start cannot pass verification."""
    try:
        return await client.send_photo(
            message.chat.id,
            ALIVE_PIC,
            caption=FORCE_CAPTION,
            reply_markup=_force_markup(),
            parse_mode="html",
        )
    except Exception:
        return await client.send_message(
            message.chat.id,
            FORCE_CAPTION,
            reply_markup=_force_markup(),
            parse_mode="html",
        )


async def _send_start_or_force(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return await _send_force_screen(client, message)
    try:
        joined = await _force_joined(client, user_id)
    except Exception:
        joined = False
    if not joined:
        return await _send_force_screen(client, message)
    try:
        return await client.send_photo(
            message.chat.id,
            ALIVE_PIC,
            caption=Data.START,
            reply_markup=InlineKeyboardMarkup(Data.buttons),
        )
    except Exception:
        return await client.send_message(
            message.chat.id,
            Data.START,
            reply_markup=InlineKeyboardMarkup(Data.buttons),
        )


@app.on_message(filters.command("start", prefixes=["/", "."]) & filters.private)
async def start_handler(client: Client, message: Message):
    try:
        await _send_start_or_force(client, message)
    except Exception as exc:
        log.exception("/start failed for user %s", getattr(message.from_user, "id", "unknown"))
        try:
            await message.reply_text(
                "⚠️ WASTE X UBOT could not open the menu right now.\n\n"
                "Please try /start again. If the problem continues, make sure the bot is an admin in both Force Join channels.",
            )
        except Exception:
            pass


@app.on_message(filters.command("force", [".", "/"]) & filters.private)
async def force_handler(client: Client, message: Message):
    # /force is the Force Commands entry point after the normal /start
    # force-join gate has been satisfied. If the user has not joined yet,
    # show the same join screen used by /start.
    if not await _force_joined(client, message.from_user.id):
        return await client.send_photo(message.chat.id, ALIVE_PIC, caption=FORCE_CAPTION, reply_markup=_force_markup(), parse_mode="html")
    try:
        from Waste.modules.help.help import FORCE_TEXT, _force_keyboard
        return await client.send_photo(message.chat.id, ALIVE_PIC, caption=FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="html")
    except Exception:
        return await client.send_photo(message.chat.id, ALIVE_PIC, caption=BOT_FORCE_TEXT, reply_markup=_bot_force_keyboard(), parse_mode="html")


BOT_FORCE_TEXT = """<blockquote><b>❖ ＷＡＳＴＥ Ｘ ＵＢＯＴ - FORCE COMMANDS ❖</b>

Tap a category below to open its commands and usage.

<b>Music/Song, VcFight and AutoTextPromo have separate command menus.</b></blockquote>"""

BOT_FORCE_CATEGORIES = [
    ("🎵 MUSIC / SONG", "music"), ("⚔️ VCFIGHT", "vcfight"),
    ("📢 AUTOTEXTPROMO", "autotextpromo"), ("🤖 AICHAT", "aichat"),
    ("🎨 AUTOPIC", "autopic"), ("🛠️ ADMIN", "admin"),
    ("😴 AFK", "afk"), ("🎬 ANIMATION", "animation"),
    ("📣 PROMOTION", "promotion"), ("🔧 TOOLS", "tools"),
]

BOT_FORCE_COMMANDS = {
    "music": "<blockquote><b>🎵 MUSIC / SONG</b>\n\n<code>.play song name</code>\n<code>/play song name</code>\n\nThe connected ID is used as the VC assistant/player.</blockquote>",
    "vcfight": "<blockquote><b>⚔️ VCFIGHT</b>\n\n<code>.join &lt;group_id&gt;</code>\n<code>.allvc join</code> / <code>.allvc leave</code>\n<code>.fight</code> / <code>.fightstop</code>\n<code>.vcleave</code>\n<code>.vcstatus</code>\n<code>.recordings</code>\n<code>.addrc</code> / <code>.removerc</code> / <code>.myrc</code> / <code>.rcinfo</code>\n\nUse either <code>.</code> or <code>/</code>.</blockquote>",
    "autotextpromo": "<blockquote><b>📢 AUTOTEXTPROMO</b>\n\n<code>.autotextpromo on</code>\n<code>.autotextpromo off</code>\n<code>/autotextpromo on</code>\n<code>/autotextpromo off</code></blockquote>",
    "aichat": "<blockquote><b>🤖 AICHAT</b>\n\nUse the existing AI chat commands from the connected userbot. Both <code>.</code> and <code>/</code> prefixes are supported where registered.</blockquote>",
    "autopic": "<blockquote><b>🎨 AUTOPIC</b>\n\nUse <code>.autopic</code> / <code>/autopic</code> and the existing Autopic settings.</blockquote>",
    "admin": "<blockquote><b>🛠️ ADMIN</b>\n\nExisting administrator commands remain available through the connected userbot.</blockquote>",
    "afk": "<blockquote><b>😴 AFK</b>\n\n<code>.afk</code> / <code>/afk</code> and the existing AFK settings.</blockquote>",
    "animation": "<blockquote><b>🎬 ANIMATION</b>\n\nExisting animation commands are available from the connected userbot.</blockquote>",
    "promotion": "<blockquote><b>📣 PROMOTION</b>\n\n<code>.promotion &lt;text&gt;</code>\n<code>.autotextpromo on/off</code></blockquote>",
    "tools": "<blockquote><b>🔧 TOOLS</b>\n\nAll existing tool commands remain available from the connected userbot.</blockquote>",
}

def _bot_force_keyboard():
    rows = []
    for i in range(0, len(BOT_FORCE_CATEGORIES), 2):
        row = [InlineKeyboardButton(BOT_FORCE_CATEGORIES[i][0], callback_data=f"botforce:{BOT_FORCE_CATEGORIES[i][1]}")]
        if i + 1 < len(BOT_FORCE_CATEGORIES):
            row.append(InlineKeyboardButton(BOT_FORCE_CATEGORIES[i+1][0], callback_data=f"botforce:{BOT_FORCE_CATEGORIES[i+1][1]}"))
        rows.append(row)
    return InlineKeyboardMarkup(rows)

@app.on_message(filters.command("help", [".", "/"]) & filters.private)
async def help_command(client: Client, message: Message):
    if not await _force_joined(client, message.from_user.id):
        return await client.send_photo(message.chat.id, ALIVE_PIC, caption=FORCE_CAPTION, reply_markup=_force_markup(), parse_mode="html")
    arg = " ".join(message.command[1:]).strip().lower() if len(message.command) > 1 else ""
    if arg:
        aliases = {"song": "music", "play": "music", "vcfight": "vcfight", "autotext": "autotextpromo"}
        key = aliases.get(arg, arg)
        if key in BOT_FORCE_COMMANDS:
            return await message.reply_photo(ALIVE_PIC, caption=BOT_FORCE_COMMANDS[key], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="botforce:menu")]]), parse_mode="html")
    return await client.send_photo(message.chat.id, ALIVE_PIC, caption=BOT_FORCE_TEXT, reply_markup=_bot_force_keyboard(), parse_mode="html")

@app.on_callback_query(filters.regex(r"^botforce:"))
async def bot_force_callback(client: Client, query: CallbackQuery):
    await query.answer()
    key = query.data.split(":", 1)[1]
    if key == "menu":
        return await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=BOT_FORCE_TEXT, parse_mode="html"), reply_markup=_bot_force_keyboard())
    text = BOT_FORCE_COMMANDS.get(key, BOT_FORCE_TEXT)
    await query.message.edit_caption(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="botforce:menu")]]), parse_mode="html")


@app.on_callback_query(filters.regex(r"^start_force_check$"))
async def start_force_check(client: Client, query: CallbackQuery):
    if not await _force_joined(client, query.from_user.id):
        await query.answer("Please join both channels first.", show_alert=True)
        return
    await query.answer("Joined successfully ✓")
    await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.START), reply_markup=InlineKeyboardMarkup(Data.buttons))

@app.on_message(filters.command("about", [".", "/"]) & filters.private)
async def about_command(client: Client, message: Message):
    await message.reply_text(Data.ABOUT, reply_markup=InlineKeyboardMarkup(Data.home_buttons))

@app.on_callback_query(filters.regex(r"^(home|help|about|donate|guide)$"))
async def callback_handler(client: Client, query: CallbackQuery):
    await query.answer()
    data = query.data
    if data == "home":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.START), reply_markup=InlineKeyboardMarkup(Data.buttons))
    elif data == "help":
        try:
            from Waste.modules.help.help import FORCE_TEXT, _force_keyboard
            await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=FORCE_TEXT, parse_mode="html"), reply_markup=_force_keyboard())
        except Exception:
            await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.HELP, parse_mode="html"), reply_markup=InlineKeyboardMarkup(Data.home_buttons))
    elif data == "about":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.ABOUT), reply_markup=InlineKeyboardMarkup(Data.home_buttons))
    elif data == "donate":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.DONATE), reply_markup=InlineKeyboardMarkup(Data.guide_buttons))
    elif data == "guide":
        await query.message.edit_media(InputMediaPhoto(ALIVE_PIC, caption=Data.GUIDE), reply_markup=InlineKeyboardMarkup(Data.back_buttons))

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

