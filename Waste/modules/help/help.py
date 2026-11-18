from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Waste import app, CMD_HELP, SUDO_USER
from config import ALIVE_PIC, ALIVE_VIDEO

# Telegram custom emoji IDs supplied for the Waste X Ubot UI.
EMOJI_MAIN = "5471952986970267163"
EMOJI_DETAIL = "5445284980978621387"
EMOJI_QUOTE = "5445284980978621387"
EMOJI_DEPLOY = "5445284980978621387"
EMOJI_PAGE = "5226512880362332956"
EMOJI_MENU = "5989975649740134220"


def E(emoji_id: str, fallback: str = "✨") -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


HELP_COMMANDS = [
    "Autopic", "admin", "afk", "animation", "anime_cf", "antipm", "autoscroll", "banall",
    "birthday", "broadcast", "carbon", "clone", "create", "destruct", "dictionary", "dmspam",
    "emoji", "flirt", "globals", "google", "info", "invite", "joinleave", "locks", "memify",
    "mention", "metrics", "paste", "pats", "ping", "profile", "purge", "quotly", "raid",
    "replyraid", "restart", "sangmata", "screenshot", "spam", "start", "stats", "sticker",
    "stickers", "sudos", "tag", "tagalert", "tagall", "text", "tiny", "translate", "truth-dare",
    "update", "upload", "vctools", "vulgar", "waifu", "weather", "promotion", "aichat", "Music",
    "VcFight", "AutoTextPromo", "VcTalk", "Reactions",
]
PAGE_SIZE = 10


def _page_commands(page: int):
    page = max(1, min(6, page))
    return HELP_COMMANDS[(page - 1) * PAGE_SIZE: page * PAGE_SIZE]


def _help_page_text(page: int) -> str:
    commands = _page_commands(page)
    lines = [
        f"<blockquote>{E(EMOJI_MAIN, '✨')} <b>ＷＡＳＴＥ Ｘ ᴜʙᴏᴛ — 𝐅𝐎𝐑𝐂𝐄 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒</b>",
        "",
        f"{E(EMOJI_DETAIL, '🔹')} <b>ᴘᴀɢᴇ {page}/6</b>",
        f"{E(EMOJI_DETAIL, '🔹')} ᴛᴀᴘ ᴀɴʏ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ᴅᴇᴛᴀɪʟs.",
        "",
    ]
    for name in commands:
        lines.append(f"{E(EMOJI_MAIN, '📌')} <code>{name}</code>")
    lines.append("</blockquote>")
    return "\n".join(lines)


def _help_page_keyboard(page: int):
    rows = []
    commands = _page_commands(page)
    for i in range(0, len(commands), 2):
        row = [InlineKeyboardButton(f"{commands[i]}", callback_data=f"grouphelp:{commands[i]}")]
        if i + 1 < len(commands):
            row.append(InlineKeyboardButton(f"{commands[i+1]}", callback_data=f"grouphelp:{commands[i+1]}"))
        rows.append(row)
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("ᴘʀᴇᴠ", callback_data=f"help_page:{page-1}"))
    nav.append(InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="help_page:noop"))
    if page < 6:
        nav.append(InlineKeyboardButton("ᴅᴇᴘʟᴏʏ ➡️", callback_data=f"help_page:{page+1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton("ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="force_menu")])
    return InlineKeyboardMarkup(rows)


FORCE_TEXT = f"""<blockquote>{E(EMOJI_MAIN, '✨')} <b>ＷＡＳＴＥ Ｘ 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐇𝐎𝐒𝐓</b>

{E(EMOJI_DETAIL, '🔹')} ᴄʜᴏᴏsᴇ ᴀ ᴄᴏᴍᴍᴀɴᴅ/ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ᴏᴘᴇɴ ɪᴛs ᴅᴇᴛᴀɪʟs.
{E(EMOJI_DETAIL, '🔹')} ᴛᴀᴘ ᴀɴʏ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ᴜsᴀɢᴇ.
{E(EMOJI_DETAIL, '🔹')} ᴍᴜsɪᴄ, ᴠᴄғɪɢʜᴛ ᴀɴᴅ ʀᴇᴄᴏʀᴅɪɴɢs ʜᴀᴠᴇ ᴛʜᴇɪʀ ᴏᴡɴ ᴄᴏᴍᴍᴀɴᴅ ᴘᴀɢᴇs.
{E(EMOJI_DETAIL, '🔹')} ᴜsᴇ <code>.help &lt;command&gt;</code> ғʀᴏᴍ ᴀ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪᴅ ғᴏʀ ᴅɪʀᴇᴄᴛ ᴅᴇᴛᴀɪʟs.</blockquote>"""

HELP_MENU = _help_page_text(1)


def _force_keyboard():
    rows = [
        [InlineKeyboardButton("ᴍᴜsɪᴄ / sᴏɴɢ", callback_data="force_mod:Music"), InlineKeyboardButton("ᴠᴄғɪɢʜᴛ", callback_data="force_mod:VcFight")],
        [InlineKeyboardButton("ʀᴇᴄᴏʀᴅɪɴɢs", callback_data="force_recordings"), InlineKeyboardButton("ᴀᴜᴛᴏᴛᴇxᴛᴘʀᴏᴍᴏ", callback_data="force_mod:AutoTextPromo")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ ➡️", callback_data="help_page:2")],
        [InlineKeyboardButton("ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="force_help")],
    ]
    return InlineKeyboardMarkup(rows)


def _recordings_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴀᴅᴅʀᴄ", callback_data="force_record:addrc"), InlineKeyboardButton("ʀᴇᴍᴏᴠᴇʀᴄ", callback_data="force_record:removerc")],
        [InlineKeyboardButton("ᴍʏʀᴄ", callback_data="force_record:myrc"), InlineKeyboardButton("ʀᴄɪɴғᴏ", callback_data="force_record:rcinfo")],
        [InlineKeyboardButton("ʙᴀss 100–500", callback_data="force_record:bass")],
        [InlineKeyboardButton("ғᴏʀᴄᴇ ᴄᴏᴍᴍᴀɴᴅs", callback_data="force_menu")],
    ])


def _force_join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ sᴜᴘᴘᴏʀᴛ ➜", url="https://t.me/wasteBotz")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ ᴜᴘᴅᴀᴛᴇs ➜", url="https://t.me/wasteuserbotUpdates")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ", callback_data="force_check")],
    ])


def _force_join_text():
    return f"""<blockquote>{E(EMOJI_MAIN, '✨')} <b>⚡ WASTE X 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐇𝐎𝐒𝐓 👑</b>

{E(EMOJI_DETAIL, '👤')} ᴜꜱᴇʀ : <b>𝐉 𝐏 𝐄 𝐗 𝐎 🚩</b>

{E(EMOJI_DETAIL, '💎')} ꜱᴛᴀᴛᴜꜱ : ❌ ɪɴᴀᴄᴛɪᴠᴇ

{E(EMOJI_DETAIL, '🚀')} ᴡᴇʟᴄᴏᴍᴇ! ᴅᴇᴘʟᴏʏ ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ᴜꜱᴇʀʙᴏᴛ ɪɴꜱᴛᴀɴᴛʟʏ ᴡɪᴛʜ ꜱᴇᴄᴜʀᴇ ᴏᴛᴘ ʟᴏɢɪɴ.

{E(EMOJI_DEPLOY, '✨')} ᴊᴏɪɴ ʙᴏᴛʜ ᴏꜰꜰɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.

{E(EMOJI_DEPLOY, '✨')} ᴘʀᴇꜱꜱ <b>ᴅᴇᴘʟᴏʏ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ</b> ᴀꜰᴛᴇʀ ᴊᴏɪɴɪɴɢ.</blockquote>"""
async def _joined(client, user_id):
    for chat in ("@wasteBotz", "@wasteuserbotUpdates"):
        try:
            member = await client.get_chat_member(chat, user_id)
            status = getattr(member, "status", None)
            value = getattr(status, "value", status)
            if value in {"left", "kicked", "banned"}:
                return False
        except Exception:
            return False
    return True


async def _send_force_join(client, message):
    if ALIVE_VIDEO:
        try:
            return await message.reply_video(ALIVE_VIDEO, caption=_force_join_text(), reply_markup=_force_join_keyboard(), parse_mode="HTML")
        except Exception:
            pass
    try:
        return await message.reply_photo(ALIVE_PIC, caption=_force_join_text(), reply_markup=_force_join_keyboard(), parse_mode="HTML")
    except Exception:
        return await message.reply_text(_force_join_text(), reply_markup=_force_join_keyboard(), parse_mode="HTML")


def _group_help_keyboard():
    return _help_page_keyboard(1)


def _find_help_key(name: str):
    name = (name or "").strip().lower()
    aliases = {"music": "Music", "song": "Music", "play": "Music", "autotextpromo": "AutoTextPromo", "autotext": "AutoTextPromo", "vcfight": "VcFight", "recordings": "VcFight", "record": "VcFight", "vctalk": "VcTalk", "mmar": "Reactions", "omar": "Reactions"}
    if name in aliases:
        return aliases[name]
    for key in CMD_HELP:
        if key.lower() == name:
            return key
    return None


def _module_text(key):
    commands = CMD_HELP.get(key, {})
    if not commands:
        if key == "AutoTextPromo":
            commands = {"autotextpromo": "Premium: `.autotextpromo on/off` — sends a different casual text every 30 minutes."}
        else:
            return f"<blockquote>{E(EMOJI_DETAIL, '❌')} <b>{key}</b>\n\nNo command details are registered for this module yet.</blockquote>"
    lines = [f"<blockquote>{E(EMOJI_DETAIL, '✦')} <b>{key.upper()} COMMANDS</b></blockquote>", ""]
    for command, desc in commands.items():
        lines.append(f"<blockquote>{E(EMOJI_QUOTE, '✦')} <code>.{command}</code>  |  <code>/{command}</code>\n  {desc}</blockquote>")
    return "\n".join(lines)


@Client.on_message(filters.command("force", [".", "/"]) & (filters.me | filters.user(SUDO_USER)))
async def force_command(client, message):
    if not await _joined(client, message.from_user.id if message.from_user else (await client.get_me()).id):
        return await _send_force_join(client, message)
    try:
        if ALIVE_VIDEO:
            return await message.reply_video(ALIVE_VIDEO, caption=FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="HTML")
        return await message.reply_photo(ALIVE_PIC, caption=FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="HTML")
    except Exception:
        return await message.reply_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="HTML")


@Client.on_message(filters.command(["help", "helpme"], [".", "/"]) & (filters.me | filters.user(SUDO_USER)))
async def module_help(client: Client, message: Message):
    help_arg = " ".join(message.command[1:]).strip() if len(message.command) > 1 else ""
    is_private = bool(message.chat and getattr(message.chat.type, "value", message.chat.type) == "private")

    if is_private:
        if not await _joined(client, message.from_user.id if message.from_user else (await client.get_me()).id):
            return await _send_force_join(client, message)
        if not help_arg:
            try:
                if ALIVE_VIDEO:
                    return await message.reply_video(ALIVE_VIDEO, caption=FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="HTML")
                return await message.reply_photo(ALIVE_PIC, caption=FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="HTML")
            except Exception:
                return await message.reply_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="HTML")

    if not help_arg:
        return await message.reply_text(_help_page_text(1), parse_mode=enums.ParseMode.HTML, reply_markup=_help_page_keyboard(1))

    key = _find_help_key(help_arg)
    if key:
        return await message.reply_text(_module_text(key), parse_mode="HTML")
    await message.reply_text(f"`{help_arg}` **Not a Valid Module Name.**")


@Client.on_callback_query(filters.regex(r"^(grouphelp:|help_page:)"))
async def group_help_callback(client, query):
    await query.answer()
    if query.data.startswith("help_page:"):
        raw = query.data.split(":", 1)[1]
        if raw == "noop":
            return
        page = int(raw)
        try:
            return await query.message.edit_caption(_help_page_text(page), reply_markup=_help_page_keyboard(page), parse_mode="HTML")
        except Exception:
            return await query.message.edit_text(_help_page_text(page), reply_markup=_help_page_keyboard(page), parse_mode="HTML")
    key = query.data.split(":", 1)[1]
    if key == "menu":
        try:
            return await query.message.edit_caption(_help_page_text(1), reply_markup=_help_page_keyboard(1), parse_mode="HTML")
        except Exception:
            return await query.message.edit_text(_help_page_text(1), reply_markup=_help_page_keyboard(1), parse_mode="HTML")
    text = _module_text(key)
    try:
        await query.message.edit_caption(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs", callback_data="help_page:1")]]), parse_mode="HTML")
    except Exception:
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs", callback_data="help_page:1")]]), parse_mode="HTML")


@Client.on_callback_query(filters.regex(r"^force_(menu|help|check|recordings|mod:|record:)"))
async def force_callback(client, query):
    user_id = query.from_user.id
    if query.data == "force_check":
        if not await _joined(client, user_id):
            await query.answer("Join both channels first.", show_alert=True)
            return
        await query.answer("Verified ✓")
        try:
            await query.message.edit_caption(FORCE_TEXT, reply_markup=_force_keyboard())
        except Exception:
            await query.message.edit_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="HTML")
        return
    if query.data == "force_help":
        await query.answer()
        try:
            await query.message.edit_caption(_help_page_text(1), reply_markup=_help_page_keyboard(1))
        except Exception:
            await query.message.edit_text(_help_page_text(1), reply_markup=_help_page_keyboard(1), parse_mode="HTML")
        return
    if query.data == "force_menu":
        await query.answer()
        try:
            await query.message.edit_caption(FORCE_TEXT, reply_markup=_force_keyboard())
        except Exception:
            await query.message.edit_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="HTML")
        return
    if query.data.startswith("force_mod:"):
        key = query.data.split(":", 1)[1]
        await query.answer()
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="force_menu")]])
        try:
            await query.message.edit_caption(_module_text(key), reply_markup=kb, parse_mode="HTML")
        except Exception:
            await query.message.edit_text(_module_text(key), reply_markup=kb, parse_mode="HTML")
        return
    if query.data.startswith("force_record:"):
        await query.answer()
        action = query.data.split(":", 1)[1]
        descriptions = {"bass": "<blockquote>🔊 <b>BASS</b>\n\nUse <code>.bass 100</code> through <code>.bass 500</code>.</blockquote>"}
        text = descriptions.get(action, "<blockquote>Use the corresponding recording command from the menu.</blockquote>")
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 RECORDINGS", callback_data="force_recordings")]])
        try:
            await query.message.edit_caption(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await query.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        return
    if query.data == "force_recordings":
        await query.answer()
        text = "<blockquote>🎙️ <b>VCFIGHT RECORDINGS</b>\n\nManage your saved recordings below.</blockquote>"
        try:
            await query.message.edit_caption(text, reply_markup=_recordings_keyboard(), parse_mode="HTML")
        except Exception:
            await query.message.edit_text(text, reply_markup=_recordings_keyboard(), parse_mode="HTML")


async def module_helper(client: Client, message: Message):
    help_arg = ""
    if message.reply_to_message and message.reply_to_message.text:
        help_arg = message.reply_to_message.text.strip()
    elif len(message.command) > 1:
        help_arg = " ".join(message.command[1:]).strip()
    if not help_arg:
        return await module_help(client, message)
    key = _find_help_key(help_arg)
    if key:
        return await message.reply_text(_module_text(key), parse_mode="HTML")
    await message.reply_text(f"`{help_arg}` **Not a Valid Module Name.**")


def add_command_help(module_name, commands):
    command_dict = CMD_HELP.get(module_name, {})
    for item in commands:
        if not item:
            continue
        command_dict[item[0]] = item[1]
    CMD_HELP[module_name] = command_dict
