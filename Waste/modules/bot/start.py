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

OWNER_USERNAME = "day1Nomore"
SUPPORT_USERNAME = "wasteBotz"
FORCE_SUPPORT = "wasteBotz"
FORCE_UPDATES = "wasteuserbotUpdates"
START_VIDEO_URL = "https://www.image2url.com/r2/default/videos/1795028137883-50dbfe05-30ea-4fdd-bee6-9918b92c79db.mp4"

# Premium custom-emoji IDs requested for the WASTE X UBOT UI.
PE_USER = 5471952986970267163
PE_COMMAND = 5445284980978621387
PE_SUPPORT = 5445284980978621387
PE_VERIFIED = 5226512880362332956

# Start-menu buttons are defined here so /start never depends on the legacy
# Data object, which does not contain the old buttons in this build.
def _ser_name(name):
    lower = "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯"
    upper = "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"
    return str(name).translate(str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", lower + upper))

START_BUTTONS = [
    [InlineKeyboardButton(_ser_name("basic guide"), callback_data="guide")],
    [InlineKeyboardButton(_ser_name("waste ↗"), url="https://t.me/wasteBotz"), InlineKeyboardButton(_ser_name("about"), callback_data="about")],
    [InlineKeyboardButton(_ser_name("help"), callback_data="help"), InlineKeyboardButton(_ser_name("music"), callback_data="botforce:cmd:Music")],
    [InlineKeyboardButton(_ser_name("updates ↗"), url="https://t.me/wasteuserbotUpdates"), InlineKeyboardButton(_ser_name("support ↗"), url="https://t.me/wasteBotz")],
]

HOME_BUTTONS = START_BUTTONS

ABOUT_TEXT = "<blockquote><tg-emoji emoji-id=\"5471952986970267163\">✦</tg-emoji> <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ</b>\n\n<tg-emoji emoji-id=\"5471952986970267163\">✦</tg-emoji> <b>ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴜsᴇʀʙᴏᴛ ᴡɪᴛʜ ᴍᴜsɪᴄ, ᴠᴄғɪɢʜᴛ, ᴜᴛɪʟɪᴛɪᴇs ᴀɴᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴏɴ.</b></blockquote>"
DONATE_TEXT = ABOUT_TEXT
GUIDE_TEXT = "<blockquote><tg-emoji emoji-id=\"5471952986970267163\">✦</tg-emoji> <b>ＢＡＳＩＣ ＧＵＩＤＥ</b>\n\n<tg-emoji emoji-id=\"5471952986970267163\">✦</tg-emoji> <b>ᴜsᴇ <code>/add</code> ᴛᴏ ʟᴏɢɪɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ.</b>\n<tg-emoji emoji-id=\"5471952986970267163\">✦</tg-emoji> <b>ᴀғᴛᴇʀ ᴄᴏɴɴᴇᴄᴛɪɴɢ, ᴜsᴇ <code>/help</code> ᴛᴏ ᴏᴘᴇɴ ᴛʜᴇ ғᴜʟʟ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇɴᴜ.</b>\n<tg-emoji emoji-id=\"5471952986970267163\">✦</tg-emoji> <b>ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ . ᴏʀ / ᴡʜᴇʀᴇ sᴜᴘᴘᴏʀᴛᴇᴅ.</b></blockquote>"

def _pe(eid, fallback="✦"):
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'

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
    return f"""<blockquote>{_pe(PE_USER)} <b>ＷＡＳＴＥ Ｘ 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐇𝐎𝐒𝐓</b>

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
        [InlineKeyboardButton(_ser_name("waste botz ↗"), url="https://t.me/wasteBotz")],
        [InlineKeyboardButton(_ser_name("waste updates ↗"), url="https://t.me/wasteuserbotUpdates")],
        [InlineKeyboardButton(_ser_name("verified"), callback_data="start_force_check")],
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


BOT_FORCE_TEXT = "<blockquote>✦ <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ꜰᴏʀᴄᴇ ᴄᴏᴍᴍᴀɴᴅs</b></blockquote>"

FORCE_COMMANDS = [
    "Autopic", "admin", "afk", "animation", "anime_cf", "antipm", "autoscroll", "banall", "birthday", "broadcast", "carbon", "clone",
    "create", "destruct", "dictionary", "dmspam", "emoji", "flirt", "globals", "google", "info", "invite", "joinleave", "locks",
    "memify", "mention", "metrics", "paste", "pats", "ping", "profile", "purge", "quotly", "raid", "replyraid", "restart",
    "sangmata", "screenshot", "spam", "start", "stats", "sticker", "stickers", "sudos", "tag", "tagalert", "tagall", "text",
    "tiny", "translate", "truth-dare", "update", "upload", "vctools", "vulgar", "waifu", "weather", "VcFight", "promotion", "aichat",
    "Music", "AutoTextPromo"
]
PAGE_SIZE = 11
TOTAL_PAGES = 6

def _bot_force_page_text(page):
    page = max(0, min(int(page), TOTAL_PAGES - 1))
    items = FORCE_COMMANDS[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    lines = ["<blockquote>✦ <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ꜰᴏʀᴄᴇ ᴄᴏᴍᴍᴀɴᴅs</b>"]
    for name in items:
        lines.append(f"{_pe(PE_COMMAND)} <b>{_ser_name(name)}</b>")
    lines.append(f"{_pe(5226512880362332956)} <b>ᴘᴀɢᴇ {page + 1}/{TOTAL_PAGES}</b>")
    if page < TOTAL_PAGES - 1:
        lines.append(f"{_pe(5992269308305084799)} <b>ɴᴇxᴛ</b>")
    lines.append(f"{_pe(5989975649740134220)} <b>ᴍᴀɪɴ ᴍᴇɴᴜ</b>")
    lines.append("</blockquote>")
    return "\n".join(lines)

def _bot_force_keyboard(page=0):
    page = max(0, min(int(page), TOTAL_PAGES - 1))
    items = FORCE_COMMANDS[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    rows=[]
    for i in range(0, len(items), 2):
        row=[InlineKeyboardButton(_ser_name(items[i]), callback_data=f"botforce:cmd:{items[i]}")]
        if i+1 < len(items):
            row.append(InlineKeyboardButton(_ser_name(items[i+1]), callback_data=f"botforce:cmd:{items[i+1]}"))
        rows.append(row)
    nav=[]
    if page > 0:
        nav.append(InlineKeyboardButton(_ser_name("prev"), callback_data=f"botforce:page:{page-1}"))
    nav.append(InlineKeyboardButton(_ser_name(f"page {page+1}/{TOTAL_PAGES}"), callback_data="botforce:noop"))
    if page < TOTAL_PAGES - 1:
        nav.append(InlineKeyboardButton(_ser_name("next"), callback_data=f"botforce:page:{page+1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton(_ser_name("main menu"), callback_data="home")])
    return InlineKeyboardMarkup(rows)

@app.on_message(filters.command("force", [".", "/"]) & filters.private)
async def force_handler(client: Client, message: Message):
    if not await _force_joined(client, message.from_user.id):
        return await client.send_video(message.chat.id, START_VIDEO_URL, caption=_force_caption(message), reply_markup=_force_markup(), parse_mode=enums.ParseMode.HTML, supports_streaming=True)
    return await client.send_video(message.chat.id, START_VIDEO_URL, caption=_bot_force_page_text(0), reply_markup=_bot_force_keyboard(0), parse_mode=enums.ParseMode.HTML, supports_streaming=True)

@app.on_callback_query(filters.regex(r"^botforce:"))
async def bot_force_callback(client: Client, query: CallbackQuery):
    await query.answer()
    data=query.data.split(":",1)[1]
    if data == "noop":
        return
    if data == "menu":
        return await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=_bot_force_page_text(0), parse_mode=enums.ParseMode.HTML), reply_markup=_bot_force_keyboard(0))
    if data.startswith("page:"):
        page=int(data.split(":",1)[1])
        return await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=_bot_force_page_text(page), parse_mode=enums.ParseMode.HTML), reply_markup=_bot_force_keyboard(page))
    if data.startswith("cmd:"):
        from Waste.modules.help.help import _find_help_key, _module_text
        raw=data.split(":",1)[1]
        key=_find_help_key(raw) or raw
        return await query.message.edit_caption(_module_text(key), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(_ser_name("back to force commands"), callback_data="botforce:menu")]]), parse_mode=enums.ParseMode.HTML)

@app.on_callback_query(filters.regex(r"^start_force_check$"))
async def start_force_check(client: Client, query: CallbackQuery):
    if not await _force_joined(client, query.from_user.id):
        await query.answer("Please join both channels first.", show_alert=True)
        return
    await query.answer("Verified")
    await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=_start_caption(query.from_user), parse_mode=enums.ParseMode.HTML), reply_markup=InlineKeyboardMarkup(START_BUTTONS))

@app.on_message(filters.command("about", [".", "/"]) & filters.private)
async def about_command(client: Client, message: Message):
    await client.send_video(message.chat.id, START_VIDEO_URL, caption=ABOUT_TEXT, reply_markup=InlineKeyboardMarkup(HOME_BUTTONS), parse_mode="html", supports_streaming=True)

@app.on_callback_query(filters.regex(r"^(home|help|force_menu|about|donate|guide)$"))
async def callback_handler(client: Client, query: CallbackQuery):
    await query.answer()
    data=query.data
    if data == "home":
        caption=_start_caption(query.from_user); markup=InlineKeyboardMarkup(START_BUTTONS)
    elif data in {"help", "force_menu"}:
        caption=_bot_force_page_text(0); markup=_bot_force_keyboard(0)
    elif data == "about":
        caption=ABOUT_TEXT; markup=InlineKeyboardMarkup(HOME_BUTTONS)
    elif data == "donate":
        caption=DONATE_TEXT; markup=InlineKeyboardMarkup(START_BUTTONS)
    else:
        caption=GUIDE_TEXT
        markup=InlineKeyboardMarkup([[InlineKeyboardButton(_ser_name("add"), callback_data="guide_add")],[InlineKeyboardButton(_ser_name("main menu"), callback_data="home")]])
    await query.message.edit_media(InputMediaVideo(START_VIDEO_URL, caption=caption, parse_mode="html"), reply_markup=markup)

@app.on_callback_query(filters.regex(r"^guide_add$"))
async def guide_add_callback(client: Client, query: CallbackQuery):
    await query.answer()
    uid=query.from_user.id
    if _session_doc(uid):
        return await query.message.reply_text(f"{_pe(PE_USER)} <b>ᴜsᴇ /remove ғɪʀsᴛ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴀ ɴᴇᴡ ᴀᴄᴄᴏᴜɴᴛ.</b>", parse_mode="html")
    user_sessions.pop(uid, None)
    user_sessions[uid]={"step":"awaiting_phone"}
    await query.message.reply_text(f"{_pe(PE_USER)} <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪɴ ɪɴᴛᴇʀɴᴀᴛɪᴏɴᴀʟ ғᴏʀᴍᴀᴛ (e.g. +918200000009):</b>", parse_mode="html")

@app.on_message(filters.command(["play", "vplay"], [".", "/"]) & filters.group)
async def group_play_command(client: Client, message: Message):
    parts = message.text.split(None, 1) if message.text else []
    query = parts[1].strip() if len(parts) > 1 else ""
    if not query:
        return await message.reply_text(f"{_pe(PE_USER)} <b>ᴜsᴀɢᴇ: /play song name</b>", parse_mode="html")
    if not active_sessions:
        return await message.reply_text(f"{_pe(PE_USER)} <b>ɴᴏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪᴅ ɪs ᴏɴʟɪɴᴇ ʀɪɢʜᴛ ɴᴏᴡ.</b>", parse_mode="html")

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

    status = await message.reply_text(f"{_pe(PE_USER)} <b>sᴇᴀʀᴄʜɪɴɢ ʏᴏᴜᴛᴜʙᴇ...</b>", parse_mode="html")
    path = None
    try:
        from Waste.modules.basic.playvc import play_song_in_chat
        path, info, queued = await play_song_in_chat(hosted, message.chat.id, query)
        title = info.get("title") or query
        duration = info.get("duration_string") or "Unknown"
        if queued:
            await status.edit_text(f"{_pe(PE_USER)} <b>ǫᴜᴇᴜᴇᴅ</b>\n\n{_pe(PE_USER)} <b>{escape(str(title))}</b>\n{_pe(PE_USER)} <b>{escape(str(duration))}</b>", parse_mode="html")
        else:
            await status.edit_text(f"{_pe(PE_USER)} <b>ɴᴏᴡ ᴘʟᴀʏɪɴɢ</b>\n\n{_pe(PE_USER)} <b>{escape(str(title))}</b>\n{_pe(PE_USER)} <b>{escape(str(duration))}</b>\n{_pe(PE_USER)} <b>ᴘʟᴀʏɪɴɢ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘs ᴠᴏɪᴄᴇ ᴄʜᴀᴛ</b>", parse_mode="html")
    except Exception as exc:
        await status.edit_text(f"{_pe(PE_USER)} <b>ᴍᴜsɪᴄ ғᴀɪʟᴇᴅ: <code>{escape(type(exc).__name__)}</code></b>\n\n<code>{escape(str(exc)[:500])}</code>", parse_mode="html")
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
        return await message.reply_text(f"{_pe(PE_USER)} <b>ᴜsᴀɢᴇ: /subscription &lt;user_id&gt; [username]</b>", parse_mode="html")
    uid, username = _parse_target(message.command[1:])
    if uid is None:
        return await message.reply_text(f"{_pe(PE_USER)} <b>ᴜsᴇʀ ɪᴅ ʀᴇǫᴜɪʀᴇᴅ. ᴇxᴀᴍᴘʟᴇ: /subscription 123456789 username</b>", parse_mode="html")
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
        await client.send_message(uid, f"{_pe(PE_USER)} <b>sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ</b>\n\n{_pe(PE_USER)} <b>ʏᴏᴜʀ ᴘʀᴏᴍᴏᴛɪᴏɴ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ɪs ᴀᴄᴛɪᴠᴇ ғᴏʀ 30 ᴅᴀʏs.</b>", parse_mode="html")
    except Exception as exc:
        log.warning("Could not notify subscriber %s: %s", uid, exc)
    await message.reply_text(f"{_pe(PE_USER)} <b>sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴀᴄᴛɪᴠᴀᴛᴇᴅ ғᴏʀ <code>{uid}</code> ғᴏʀ 30 ᴅᴀʏs.\nᴇxᴘɪʀᴇs: <code>{escape(expires.isoformat())}</code></b>", parse_mode="html")

@app.on_message(filters.command("disubscription", [".", "/"]) & filters.private & filters.user(OWNER_ID))
async def disubscription_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /disubscription <user_id> [username]")
    uid, username = _parse_target(message.command[1:])
    if uid is None:
        return await message.reply_text(f"{_pe(PE_USER)} <b>ᴜsᴇʀ ɪᴅ ʀᴇǫᴜɪʀᴇᴅ.</b>", parse_mode="html")
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
        await client.send_message(uid, f"{_pe(PE_USER)} <b>sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ</b>\n\n{_pe(PE_USER)} <b>ʏᴏᴜʀ ᴘʀᴏᴍᴏᴛɪᴏɴ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ᴇɴᴅᴇᴅ. ᴄᴏɴᴛᴀᴄᴛ @day1Nomore ᴛᴏ ʀᴇᴀᴄᴛɪᴠᴀᴛᴇ ɪᴛ.</b>", parse_mode="html")
    except Exception as exc:
        log.warning("Could not notify unsubscribed user %s: %s", uid, exc)
    await message.reply_text(f"{_pe(PE_USER)} <b>{"sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʀᴇᴍᴏᴠᴇᴅ." if result.deleted_count else "ɴᴏ ᴀᴄᴛɪᴠᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴏᴜɴᴅ."}</b>", parse_mode="html")

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

@app.on_message(filters.regex(r"^[./]add(?:@\w+)?(?:\s+.*)?$", flags=0) & filters.private)
async def add_session_command(client: Client, message: Message):
    uid = message.from_user.id
    if _session_doc(uid):
        return await message.reply(f"{_pe(PE_USER)} <b>ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ. ᴜsᴇ /remove ғɪʀsᴛ.</b>", parse_mode="html")
    # A previous expired/failed login must never leave a stale wizard behind.
    old = user_sessions.pop(uid, None)
    if old and old.get("client"):
        try:
            await old["client"].disconnect()
        except Exception:
            pass
    args = (message.text or "").split(maxsplit=1)
    if len(args) == 2 and args[1].strip():
        user_sessions[uid] = {"step": "awaiting_phone"}
        # Reuse the normal wizard by handling the supplied number below.
        phone_msg = message
        phone_text = args[1].strip()
        if phone_text.startswith("+") and phone_text[1:].isdigit() and 8 <= len(phone_text) <= 16:
            temp = Client(name=f"gen_{uid}", api_id=API_ID, api_hash=API_HASH, in_memory=True, device_model="Waste", app_version="1.0")
            user_sessions[uid].update({"phone": phone_text, "client": temp})
            try:
                await temp.connect()
                sent = await temp.send_code(phone_text)
                user_sessions[uid]["phone_code_hash"] = sent.phone_code_hash
                user_sessions[uid]["step"] = "awaiting_otp"
                return await message.reply(f"{_pe(PE_USER)} <b>ᴏᴛᴘ sᴇɴᴛ! sᴇɴᴅ ɪᴛ ʟɪᴋᴇ: <code>1 2 3 4 5</code></b>", parse_mode="html")
            except Exception as e:
                try: await temp.disconnect()
                except Exception: pass
                user_sessions.pop(uid, None)
                return await message.reply(f"{_pe(PE_USER)} <b>ᴏᴛᴘ ᴇʀʀᴏʀ: <code>{escape(str(e))}</code>\nᴘʟᴇᴀsᴇ ᴜsᴇ /add ᴀɢᴀɪɴ.</b>", parse_mode="html")
        return await message.reply(f"{_pe(PE_USER)} <b>ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ. sᴇɴᴅ ɪᴛ ʟɪᴋᴇ: <code>+918200000009</code></b>", parse_mode="html")
    await message.reply(f"{_pe(PE_USER)} <b>ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪɴ ɪɴᴛᴇʀɴᴀᴛɪᴏɴᴀʟ ғᴏʀᴍᴀᴛ (e.g. +918200000009):</b>", parse_mode="html")
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
    await msg.reply(f"{_pe(PE_USER)} <b>{"ʏᴏᴜʀ sᴇssɪᴏɴ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ." if result.deleted_count else "ɴᴏ ᴀᴄᴛɪᴠᴇ sᴇssɪᴏɴ ғᴏᴜɴᴅ."}</b>", parse_mode="html")

@app.on_message()
async def session_handler(client: Client, msg: Message):
    if not msg.from_user or not msg.text:
        return
    # Do not let the catch-all login wizard consume bot commands.
    # Without this guard, /add itself can be seen again by this handler
    # immediately after the /add handler sets awaiting_phone, causing
    # "/add" to be sent to Telegram as if it were a phone number.
    stripped = msg.text.strip()
    if stripped.startswith(("/", ".")):
        return
    uid = msg.from_user.id
    session = user_sessions.get(uid)
    if not session:
        return
    step = session.get("step")
    if step == "awaiting_phone":
        phone = msg.text.strip().replace(" ", "")
        if not phone.startswith("+") or not phone[1:].isdigit() or len(phone) < 8 or len(phone) > 16:
            return await msg.reply(f"{_pe(PE_USER)} <b>ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ. sᴇɴᴅ ɪᴛ ʟɪᴋᴇ: <code>+918200000009</code></b>", parse_mode="html")
        temp = Client(name=f"gen_{uid}", api_id=API_ID, api_hash=API_HASH, in_memory=True, device_model="Waste", app_version="1.0")
        session.update({"phone": phone, "client": temp})
        try:
            await temp.connect()
            sent = await temp.send_code(phone)
            session["phone_code_hash"] = sent.phone_code_hash
            session["step"] = "awaiting_otp"
            await msg.reply(f"{_pe(PE_USER)} <b>ᴏᴛᴘ sᴇɴᴛ! sᴇɴᴅ ɪᴛ ʟɪᴋᴇ: <code>1 2 3 4 5</code></b>", parse_mode="html")
        except Exception as e:
            await msg.reply(f"{_pe(PE_USER)} <b>ᴏᴛᴘ ᴇʀʀᴏʀ: <code>{escape(str(e))}</code>\nᴘʟᴇᴀsᴇ ᴜsᴇ /add ᴀɢᴀɪɴ.</b>", parse_mode="html")
            try: await temp.disconnect()
            except Exception: pass
            user_sessions.pop(uid, None)
    elif step == "awaiting_otp":
        temp = session["client"]
        try:
            await temp.sign_in(phone_number=session["phone"], phone_code_hash=session["phone_code_hash"], phone_code=msg.text.strip().replace(" ", ""))
        except SessionPasswordNeeded:
            session["step"] = "awaiting_2fa"
            return await msg.reply(f"{_pe(PE_USER)} <b>sᴇɴᴅ ʏᴏᴜʀ 2ғᴀ ᴘᴀssᴡᴏʀᴅ.</b>", parse_mode="html")
        except (PhoneCodeExpired, PhoneCodeInvalid) as e:
            await msg.reply(f"{_pe(PE_USER)} <b>ᴏᴛᴘ ʟᴏɢɪɴ ғᴀɪʟᴇᴅ: <code>{escape(str(e))}</code>\nᴘʟᴇᴀsᴇ ᴜsᴇ /add ᴀɢᴀɪɴ ᴀɴᴅ ᴇɴᴛᴇʀ ᴛʜᴇ ɴᴇᴡᴇsᴛ ᴏᴛᴘ.</b>", parse_mode="html")
            try: await temp.disconnect()
            except Exception: pass
            user_sessions.pop(uid, None)
            return
        except Exception as e:
            await msg.reply(f"{_pe(PE_USER)} <b>ʟᴏɢɪɴ ғᴀɪʟᴇᴅ: <code>{escape(str(e))}</code>\nᴘʟᴇᴀsᴇ ᴜsᴇ /add ᴀɢᴀɪɴ.</b>", parse_mode="html")
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
            await msg.reply(f"{_pe(PE_USER)} <b>ɪɴᴄᴏʀʀᴇᴄᴛ 2ғᴀ ᴘᴀssᴡᴏʀᴅ: <code>{escape(str(e))}</code>\nᴘʟᴇᴀsᴇ ᴜsᴇ /add ᴀɢᴀɪɴ.</b>", parse_mode="html")
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
            await app.send_message(uid, f"{_pe(PE_USER)} <b>ᴜsᴇʀʙᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ</b>\n\n{_pe(PE_USER)} <b>ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ɪs ɴᴏᴡ ᴏɴʟɪɴᴇ ᴡɪᴛʜ ᴛʜᴇ ＷＡＳＴＥ Ｘ ＵＢＯＴ ғᴇᴀᴛᴜʀᴇs.</b>", parse_mode="html")
        except Exception as exc:
            log.warning("Notification failed for %s: %s", uid, exc)
    return hosted

async def finalize_login(client: Client, msg: Message, uid: int):
    try:
        string = await client.export_session_string()
        user = await client.get_me()
        sessions_col.update_one({"_id": uid}, {"$set": {"session": string, "name": user.first_name, "user_id": user.id, "username": user.username}}, upsert=True)
        await start_hosted_session(uid, string, notify=False)
        await msg.reply(f"{_pe(PE_USER)} <b>ʟᴏɢɢᴇᴅ ɪɴ ᴀs {escape(str(user.first_name))}.\n\nᴀᴜᴛᴏ-ʜᴏsᴛ ɴᴏᴡ ᴏɴ.\n\nᴜss ᴀᴄᴄᴏᴜɴᴛ ᴍᴇ <code>.help</code> sᴇ ᴄᴏᴍᴍᴀɴᴅs ᴅᴇᴋʜᴏ.</b>", parse_mode="html")
    except Exception as e:
        await msg.reply(f"{_pe(PE_USER)} <b>ғɪɴᴀʟ sᴛᴇᴘ ғᴀɪʟᴇᴅ: <code>{escape(str(e))}</code></b>", parse_mode="html")
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

