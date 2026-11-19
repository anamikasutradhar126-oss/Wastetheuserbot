import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from html import escape

from pyrogram import Client, filters, enums
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeExpired, PhoneCodeInvalid
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaVideo
from pymongo import MongoClient

from config import OWNER_ID, MONGO_URL
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

def _session_doc(uid):
    return sessions_col.find_one({"_id": uid})

OWNER_USERNAME = "day1Nomore"
SUPPORT_USERNAME = "wasteBotz"
FORCE_SUPPORT = "wasteBotz"
FORCE_UPDATES = "wasteuserbotUpdates"
START_VIDEO_URL = "https://www.image2url.com/r2/default/videos/1795028137883-50dbfe05-30ea-4fdd-bee6-9918b92c79db.mp4"

# Premium custom-emoji IDs requested for the WASTE X UBOT UI.
PE_USER = 5471952986970267163
PE_COMMAND = 5445284980978621387
PE_SUPPORT = 5471952986970267163
PE_VERIFIED = 5226512880362332956

def _pe(eid, fallback="✦"):
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'

# Start-menu buttons are defined here so /start never depends on the legacy
# Data object, which does not contain the old buttons in this build.
START_BUTTONS = [
    [InlineKeyboardButton("𝙗𝙖𝙨𝙞𝙘 𝙜𝙪𝙞𝙙𝙚", callback_data="guide")],
    [InlineKeyboardButton("𝙬𝙖𝙨𝙩𝙚", url="https://t.me/wasteBotz"), InlineKeyboardButton("𝙖𝙗𝙤𝙪𝙩", callback_data="about")],
    [InlineKeyboardButton("𝙝𝙚𝙡𝙥", callback_data="help"), InlineKeyboardButton("𝙢𝙪𝙨𝙞𝙘", callback_data="botforce:cmd:Music")],
    [InlineKeyboardButton("𝙪𝙥𝙙𝙖𝙩𝙚𝙨", url="https://t.me/wasteuserbotUpdates"), InlineKeyboardButton("𝙨𝙪𝙥𝙥𝙤𝙧𝙩", url="https://t.me/wasteBotz")],
]

HOME_BUTTONS = START_BUTTONS

ABOUT_TEXT = "<blockquote>" + _pe(PE_USER) + " <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ</b>\n" + _pe(PE_USER) + " <b>𝙥𝙤𝙬𝙚𝙧𝙛𝙪𝙡 𝙩𝙚𝙡𝙚𝙜𝙧𝙖𝙢 𝙪𝙨𝙚𝙧𝙗𝙤𝙩 𝙬𝙞𝙩𝙝 𝙢𝙪𝙨𝙞𝙘, 𝙫𝙘𝙛𝙞𝙜𝙝𝙩, 𝙪𝙩𝙞𝙡𝙞𝙩𝙞𝙚𝙨 𝙖𝙣𝙙 𝙖𝙪𝙩𝙤𝙢𝙖𝙩𝙞𝙤𝙣.</b></blockquote>"
DONATE_TEXT = ABOUT_TEXT
GUIDE_TEXT = "<blockquote><tg-emoji emoji-id=\"5471952986970267163\">✦</tg-emoji> <b>ＢＡＳＩＣ ＧＵＩＤＥ</b>\n\n<tg-emoji emoji-id=\"5471952986970267163\">✦</tg-emoji> <b>ᴜsᴇ <code>/add</code> ᴛᴏ ʟᴏɢɪɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ.</b>\n<tg-emoji emoji-id=\"5471952986970267163\">✦</tg-emoji> <b>ᴀғᴛᴇʀ ᴄᴏɴɴᴇᴄᴛɪɴɢ, ᴜsᴇ <code>/help</code> ᴛᴏ ᴏᴘᴇɴ ᴛʜᴇ ғᴜʟʟ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇɴᴜ.</b>\n<tg-emoji emoji-id=\"5471952986970267163\">✦</tg-emoji> <b>ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ . ᴏʀ / ᴡʜᴇʀᴇ sᴜᴘᴘᴏʀᴛᴇᴅ.</b></blockquote>"

def _started_name(message: Message) -> str:
    user = getattr(message, "from_user", None)
    if not user:
        return "User"
    name = getattr(user, "first_name", None) or getattr(user, "username", None) or "User"
    return escape(str(name))

def _is_userbot_active(uid: int) -> bool:
    return any(getattr(c, "_waste_owner_uid", None) == uid for c in active_sessions)

def _start_caption(message: Message) -> str:
    uid = getattr(getattr(message, "from_user", None), "id", 0)
    name = _started_name(message)
    status = "ᴀᴄᴛɪᴠᴇ" if _is_userbot_active(uid) else "ɪɴᴀᴄᴛɪᴠᴇ"
    return f"""<blockquote>{_pe(PE_USER)} <b>ＷＡＳＴＥ Ｘ 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐇𝐎𝐒𝐓</b>
{_pe(PE_USER)} <b>ᴜꜱᴇʀ : {name}</b>
{_pe(PE_USER)} <b>ꜱᴛᴀᴛᴜꜱ : {status}</b>
{_pe(PE_USER)} <b>ᴡᴇʟᴄᴏᴍᴇ! ᴅᴇᴘʟᴏʏ ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ᴜꜱᴇʀʙᴏᴛ ɪɴꜱᴛᴀɴᴛʟʏ ᴡɪᴛʜ ꜱᴇᴄᴜʀᴇ ᴏᴛᴘ ʟᴏɢɪɴ.</b></blockquote>"""


def _force_caption(message: Message) -> str:
    uid = getattr(getattr(message, "from_user", None), "id", 0)
    name = _started_name(message)
    status = "ᴀᴄᴛɪᴠᴇ" if _is_userbot_active(uid) else "ɪɴᴀᴄᴛɪᴠᴇ"
    return f"""<blockquote>{_pe(PE_USER)} <b>ＷＡＳＴＥ Ｘ 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐇𝐎𝐒ᴛ</b>
{_pe(PE_USER)} <b>ᴜꜱᴇʀ : {name}</b>
{_pe(PE_USER)} <b>ꜱᴛᴀᴛᴜꜱ : {status}</b>
{_pe(PE_USER)} <b>ᴡᴇʟᴄᴏᴍᴇ! ᴅᴇᴘʟᴏʏ ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ᴜꜱᴇʀʙᴏᴛ ɪɴꜱᴛᴀɴᴛʟʏ ᴡɪᴛʜ ꜱᴇᴄᴜʀᴇ ᴏᴛᴘ ʟᴏɢɪɴ.</b>
{_pe(PE_SUPPORT)} <b>ᴊᴏɪɴ ʙᴏᴛʜ ᴏғғɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴜɴʟᴏᴄᴋ ᴀᴄᴄᴇss.</b>
{_pe(PE_VERIFIED)} <b>ᴀғᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴛᴀᴘ ᴠᴇʀɪғɪᴇᴅ ᴛᴏ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ.</b></blockquote>"""


async def _force_joined(client: Client, user_id: int) -> bool:
    """Return True only when the user is a member of both required channels."""
    for chat in ("@wasteBotz", "@wasteuserbotUpdates"):
        try:
            member = await client.get_chat_member(chat, user_id)
            status = getattr(member, "status", None)
            value = getattr(status, "value", status)
            if value in {"left", "kicked", "banned"}:
                return False
        except Exception as exc:
            log.warning("Force-join check failed for %s: %s", chat, type(exc).__name__)
            return False
    return True


def _force_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("𝙨𝙪𝙥𝙥𝙤𝙧𝙩", url="https://t.me/wasteBotz")],
        [InlineKeyboardButton("𝙪𝙥𝙙𝙖𝙩𝙚𝙨", url="https://t.me/wasteuserbotUpdates")],
        [InlineKeyboardButton("𝙫𝙚𝙧𝙞𝙛𝙞𝙚𝙙", callback_data="start_force_check")],
    ])


async def _send_start_or_force(client: Client, message: Message):
    if not await _force_joined(client, message.from_user.id):
        try:
            return await client.send_video(message.chat.id, START_VIDEO_URL, caption=_force_caption(message), reply_markup=_force_markup(), parse_mode=enums.ParseMode.HTML, supports_streaming=True)
        except Exception:
            return await client.send_message(message.chat.id, _force_caption(message), reply_markup=_force_markup(), parse_mode=enums.ParseMode.HTML)
    try:
        return await client.send_video(message.chat.id, START_VIDEO_URL, caption=_start_caption(message), reply_markup=InlineKeyboardMarkup(START_BUTTONS), parse_mode=enums.ParseMode.HTML, supports_streaming=True)
    except Exception:
        return await client.send_message(message.chat.id, _start_caption(message), reply_markup=InlineKeyboardMarkup(START_BUTTONS), parse_mode=enums.ParseMode.HTML)


@app.on_message(filters.command("start", [".", "/"]) & filters.private)
async def start_handler(client: Client, message: Message):
    await _send_start_or_force(client, message)


BOT_FORCE_TEXT = """<blockquote><tg-emoji emoji-id="5471952986970267163">✦</tg-emoji> <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ꜰᴏʀᴄᴇ ᴄᴏᴍᴍᴀɴᴅs</b></blockquote>"""

FORCE_COMMANDS = [
    "Autopic", "admin", "afk", "animation", "anime_cf", "antipm", "autoscroll", "banall", "birthday", "broadcast", "carbon", "clone",
    "create", "destruct", "dictionary", "dmspam", "emoji", "flirt", "globals", "google", "info", "invite", "joinleave", "locks",
    "memify", "mention", "metrics", "paste", "pats", "ping", "profile", "purge", "quotly", "raid", "replyraid", "restart",
    "sangmata", "screenshot", "spam", "start", "stats", "sticker", "stickers", "sudos", "tag", "tagalert", "tagall", "text",
    "tiny", "translate", "truth-dare", "update", "upload", "vctools", "vulgar", "waifu", "weather", "VcFight", "promotion", "aichat",
    "Music", "AutoTextPromo"
]

def _bot_force_page_text(page):
    total = 6
    chunks = [FORCE_COMMANDS[i:i+11] for i in range(0, 55, 11)] + [FORCE_COMMANDS[55:]]
    chunk = chunks[max(0, min(int(page), total - 1))]
    # Only the requested header and command list are shown.
    lines = ['<blockquote><tg-emoji emoji-id="5471952986970267163">✦</tg-emoji> <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ꜰᴏʀᴄᴇ ᴄᴏᴍᴍᴀɴᴅs</b>', '']
    for name in chunk:
        lines.append(f'<tg-emoji emoji-id="5445284980978621387">✦</tg-emoji> <b>{_ser_name(name)}</b>')
    lines.append(f'<tg-emoji emoji-id="5226512880362332956">✦</tg-emoji> <b>ᴘᴀɢᴇ {int(page)+1}/6</b>')
    lines.append('</blockquote>')
    return '\n'.join(lines)

def _ser_name(name):
    # Mathematical Sans Bold Italic style requested for command labels.
    mapping = str.maketrans({
        'a':'𝙖','b':'𝙗','c':'𝙘','d':'𝙙','e':'𝙚','f':'𝙛','g':'𝙜','h':'𝙝','i':'𝙞','j':'𝙟','k':'𝙠','l':'𝙡','m':'𝙢',
        'n':'𝙣','o':'𝙤','p':'𝙥','q':'𝙦','r':'𝙧','s':'𝙨','t':'𝙩','u':'𝙪','v':'𝙫','w':'𝙬','x':'𝙭','y':'𝙮','z':'𝙯',
        'A':'𝙰','B':'𝙱','C':'𝙲','D':'𝙳','E':'𝙴','F':'𝙵','G':'𝙶','H':'𝙷','I':'𝙸','J':'𝙹','K':'𝙺','L':'𝙻','M':'𝙼',
        'N':'𝙽','O':'𝙾','P':'𝙿','Q':'𝚀','R':'𝚁','S':'𝚂','T':'𝚃','U':'𝚄','V':'𝚅','W':'𝚆','X':'𝚇','Y':'𝚈','Z':'𝚉'
    })
    return str(name).lower().translate(mapping)

def _bot_force_keyboard(page=0):
    page = max(0, min(int(page), 5))
    chunk = [FORCE_COMMANDS[i:i+11] for i in range(0, 55, 11)] + [FORCE_COMMANDS[55:]]
    rows = []
    items = chunk[page]
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(_ser_name(items[i]), callback_data=f"botforce:cmd:{items[i]}")]
        if i + 1 < len(items):
            row.append(InlineKeyboardButton(_ser_name(items[i+1]), callback_data=f"botforce:cmd:{items[i+1]}"))
        rows.append(row)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("𝙥𝙧𝙚𝙫", callback_data=f"botforce:page:{page-1}"))
    nav.append(InlineKeyboardButton(f"ᴘᴀɢᴇ {page+1}/6", callback_data="botforce:noop"))
    if page < 5:
        nav.append(InlineKeyboardButton("𝙣𝙚𝙭𝙩", callback_data=f"botforce:page:{page+1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton("𝙢𝙖𝙞𝙣 𝙢𝙚𝙣𝙪", callback_data="home")])
    return InlineKeyboardMarkup(rows)


def _bot_force_media_kwargs():
    return dict(caption=BOT_FORCE_TEXT, parse_mode=enums.ParseMode.HTML, supports_streaming=True)


@app.on_message(filters.command("force", [".", "/"]) & filters.private)
async def force_handler(client: Client, message: Message):
    if not await _force_joined(client, message.from_user.id):
        try:
            return await client.send_video(message.chat.id, START_VIDEO_URL, caption=_force_caption(message), reply_markup=_force_markup(), parse_mode=enums.ParseMode.HTML, supports_streaming=True)
        except Exception:
            return await client.send_message(message.chat.id, _force_caption(message), reply_markup=_force_markup(), parse_mode=enums.ParseMode.HTML)
    try:
        return await client.send_video(message.chat.id, START_VIDEO_URL, caption=_bot_force_page_text(0), reply_markup=_bot_force_keyboard(0), parse_mode=enums.ParseMode.HTML, supports_streaming=True)
    except Exception:
        return await client.send_message(message.chat.id, _bot_force_page_text(0), reply_markup=_bot_force_keyboard(0), parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex(r"^botforce:"))
async def bot_force_callback(client: Client, query: CallbackQuery):
    await query.answer()
    data = query.data.split(":", 1)[1]
    if data == "noop":
        return
    if data == "menu":
        try:
            return await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=_bot_force_page_text(0), parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=_bot_force_keyboard(0))
        except Exception:
            return await query.message.edit_text(BOT_FORCE_TEXT, reply_markup=_bot_force_keyboard(0), parse_mode=enums.ParseMode.HTML)
    if data.startswith("page:"):
        page = int(data.split(":", 1)[1])
        try:
            return await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=_bot_force_page_text(page), parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=_bot_force_keyboard(page))
        except Exception:
            return await query.message.edit_text(_bot_force_page_text(page), reply_markup=_bot_force_keyboard(page), parse_mode=enums.ParseMode.HTML)
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
    await query.message.edit_caption(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ ᴛᴏ ꜰᴏʀᴄᴇ ᴄᴏᴍᴍᴀɴᴅs", callback_data="botforce:menu")]]), parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex(r"^start_force_check$"))
async def start_force_check(client: Client, query: CallbackQuery):
    if not await _force_joined(client, query.from_user.id):
        await query.answer("Please join both channels first.", show_alert=True)
        return
    await query.answer("Verified successfully")
    try:
        await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=_start_caption(query), parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=InlineKeyboardMarkup(START_BUTTONS))
    except Exception:
        await query.message.edit_caption(_start_caption(query), reply_markup=InlineKeyboardMarkup(START_BUTTONS), parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.command("about", [".", "/"]) & filters.private)
async def about_command(client: Client, message: Message):
    await message.reply_text(ABOUT_TEXT, reply_markup=InlineKeyboardMarkup(HOME_BUTTONS))

@app.on_callback_query(filters.regex(r"^(home|help|force_menu|about|donate|guide)$"))
async def callback_handler(client: Client, query: CallbackQuery):
    await query.answer()
    data = query.data
    if data == "home":
        try:
            await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=_start_caption(query), parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=InlineKeyboardMarkup(START_BUTTONS))
        except Exception:
            await query.message.edit_caption(_start_caption(query), reply_markup=InlineKeyboardMarkup(START_BUTTONS), parse_mode=enums.ParseMode.HTML)
    elif data in {"help", "force_menu"}:
        try:
            await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=_bot_force_page_text(0), parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=_bot_force_keyboard(0))
        except Exception:
            await query.message.edit_text(BOT_FORCE_TEXT, reply_markup=_bot_force_keyboard(0), parse_mode=enums.ParseMode.HTML)
    elif data == "about":
        try:
            await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=ABOUT_TEXT, parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=InlineKeyboardMarkup(HOME_BUTTONS))
        except Exception:
            await query.message.edit_caption(ABOUT_TEXT, reply_markup=InlineKeyboardMarkup(HOME_BUTTONS), parse_mode=enums.ParseMode.HTML)
    elif data == "donate":
        await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=DONATE_TEXT, parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=InlineKeyboardMarkup(START_BUTTONS))
    elif data == "guide":
        try:
            await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=GUIDE_TEXT, parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=InlineKeyboardMarkup(START_BUTTONS))
        except Exception:
            await query.message.edit_caption(GUIDE_TEXT, reply_markup=InlineKeyboardMarkup(START_BUTTONS), parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.command("subscription", [".", "/"]) & filters.private & filters.user(OWNER_ID))
async def subscription_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /subscription <user_id> [username]")
    uid, username = _parse_target(message.command[1:])
    if uid is None:
        return await message.reply_text(f"{_pe(PE_USER)} <b>ᴜsᴇʀ ɪᴅ ʀᴇǫᴜɪʀᴇᴅ.</b> ᴇxᴀᴍᴘʟᴇ: /subscription 123456789 username")
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
        await client.send_message(uid, f"{_pe(PE_USER)} **Subscription Activated**\n\nYour Promotion subscription is active for **30 days**.")
    except Exception as exc:
        log.warning("Could not notify subscriber %s: %s", uid, exc)
    await message.reply_text(f"{_pe(PE_USER)} Subscription activated for `{uid}` for 30 days.\n{_pe(PE_USER)} Expires: `{expires.isoformat()}`")

@app.on_message(filters.command("disubscription", [".", "/"]) & filters.private & filters.user(OWNER_ID))
async def disubscription_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /disubscription <user_id> [username]")
    uid, username = _parse_target(message.command[1:])
    if uid is None:
        return await message.reply_text(f"{_pe(PE_USER)} <b>ᴜsᴇʀ ɪᴅ ʀᴇǫᴜɪʀᴇᴅ.</b>")
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
        await client.send_message(uid, f"{_pe(PE_USER)} **Subscription Deactivated**\n\nYour Promotion subscription has ended. Contact @day1Nomore to reactivate it.")
    except Exception as exc:
        log.warning("Could not notify unsubscribed user %s: %s", uid, exc)
    await message.reply_text(f"{_pe(PE_USER)} Subscription removed." if result.deleted_count else f"{_pe(PE_USER)} No active subscription found.")

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
        await msg.reply(f"{_pe(PE_USER)} ɴᴏᴡ ʏᴏᴜ ᴀʀᴇ ʀᴇᴀᴅʏ ᴛᴏ ғɪɢʜᴛ\n\n{_pe(PE_USER)} ᴀᴄᴄᴏᴜɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ\n\n{_pe(PE_USER)} {escape(str(user.first_name))}")
    except Exception as e:
        await msg.reply(f"**ERROR:** `{e}`")

@app.on_message(filters.command("add") & filters.private)
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
    await msg.reply(f"{_pe(PE_USER)} ʏᴏᴜʀ sᴇssɪᴏɴ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ." if result.deleted_count else f"{_pe(PE_USER)} ɴᴏ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ ғᴏᴜɴᴅ.", parse_mode=enums.ParseMode.HTML)

@app.on_message()
async def session_handler(client: Client, msg: Message):
    if not msg.from_user or not msg.text:
        return
    if msg.text.strip().startswith(("/", ".")):
        return
    uid = msg.from_user.id
    session = user_sessions.get(uid)
    if not session:
        return
    step = session.get("step")
    if step == "awaiting_phone":
        phone = msg.text.strip()
        temp = Client(name=f"gen_{uid}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
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
        from Waste.modules.basic.vctalk import start_background_for_client as start_vctalk_background
        await start_vctalk_background(hosted)
    except Exception as exc:
        log.warning("VC Talk background start failed for %s: %s", uid, exc)
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
            await app.send_message(uid, f"{_pe(PE_USER)} <b>ᴜsᴇʀʙᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ</b>\n\n{_pe(PE_USER)} ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ɪs ɴᴏᴡ ᴏɴʟɪɴᴇ ᴡɪᴛʜ ᴛʜᴇ ᴡᴀsᴛᴇ x ᴜsᴇʀʙᴏᴛ ғᴇᴀᴛᴜʀᴇs.", parse_mode=enums.ParseMode.HTML)
        except Exception as exc:
            log.warning("Notification failed for %s: %s", uid, exc)
    return hosted

async def finalize_login(client: Client, msg: Message, uid: int):
    try:
        string = await client.export_session_string()
        user = await client.get_me()
        sessions_col.update_one({"_id": uid}, {"$set": {"session": string, "name": user.first_name, "user_id": user.id, "username": user.username}}, upsert=True)
        await start_hosted_session(uid, string, notify=False)
        await msg.reply(f"{_pe(PE_USER)} ʟᴏɢɢᴇᴅ ɪɴ ᴀs <b>{escape(str(user.first_name))}</b>.\n\n{_pe(PE_USER)} ᴀᴜᴛᴏ-ʜᴏsᴛ ɴᴏᴡ ᴏɴ.\n\n{_pe(PE_USER)} ᴜss ᴀᴄᴄᴏᴜɴᴛ ᴍᴇ <code>.help</code> sᴇ ᴄᴏᴍᴍᴀɴᴅs ᴅᴇᴋʜᴏ.", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await msg.reply(f"{_pe(PE_USER)} ғɪɴᴀʟ sᴛᴇᴘ ғᴀɪʟᴇᴅ: <code>{escape(str(e))}</code>", parse_mode=enums.ParseMode.HTML)
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

