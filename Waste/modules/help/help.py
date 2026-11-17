from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Waste import app, CMD_HELP, SUDO_USER
from config import ALIVE_PIC

FORCE_VIDEO_URL = "https://www.image2url.com/r2/default/videos/1794758121681-9a91954b-c9c6-4323-9fd0-9bf9e42ed0fa.mp4"
PE = lambda eid, fallback="✦": f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'

HELP_MENU = r"""<blockquote>| ❁ ＷＡＳＴＥ Ｘ ＵＢＯＴ - ＨＥＬＰ ＭＥＮＵ ❁ |
+-----------------------+------------------------+
| Autopic               | admin                  |
| afk                   | animation              |
| anime_cf              | antipm                 |
| autoscroll            | banall                 |
| birthday              | broadcast              |
| carbon                | clone                  |
| create                | destruct               |
| dictionary            | dmspam                 |
| emoji                 | flirt                  |
| globals               | google                 |
| info                  | invite                 |
| joinleave             | locks                  |
| memify                | mention                |
| metrics               | paste                  |
| pats                  | ping                   |
| profile               | purge                  |
| quotly                | raid                   |
| replyraid             | restart                |
| sangmata              | screenshot             |
| spam                  | start                  |
| stats                 | sticker                |
| stickers              | sudos                  |
| tag                   | tagalert               |
| tagall                | text                   |
| tiny                  | translate              |
| truth-dare            | update                 |
| upload                | vctools                |
| vulgar                | waifu                  |
| weather               | VcFight                |
| promotion             | aichat                 |
| Music                 | AutoTextPromo          |
+-----------------------+------------------------+
• @wasteuserbotUpdates × @wasteBotz .</blockquote>"""

FORCE_TEXT = f"""<blockquote>{PE(5992130701120507687)} <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ꜰᴏʀᴄᴇ ᴄᴏᴍᴍᴀɴᴅs</b>

{PE(5992130701120507687)} <b>ᴄʜᴏᴏsᴇ ᴀ ᴄᴏᴍᴍᴀɴᴅ / ᴍᴏᴅᴜʟᴇ ʙᴇʟᴏᴡ ᴛᴏ ᴏᴘᴇɴ ɪᴛs ᴅᴇᴛᴀɪʟs.</b>
{PE(5992130701120507687)} <b>ᴛᴀᴘ ᴀɴʏ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴠɪᴇᴡ ɪᴛs ᴜsᴀɢᴇ.</b>
{PE(5992130701120507687)} <b>ᴍᴜsɪᴄ, ᴠᴄғɪɢʜᴛ ᴀɴᴅ ʀᴇᴄᴏʀᴅɪɴɢs ʜᴀᴠᴇ ᴛʜᴇɪʀ ᴏᴡɴ ᴄᴏᴍᴍᴀɴᴅ ᴘᴀɢᴇs.</b>
{PE(5992130701120507687)} <b>ᴜsᴇ .ʜᴇʟᴘ &lt;ᴄᴏᴍᴍᴀɴᴅ&gt; ғʀᴏᴍ ᴀ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪᴅ ғᴏʀ ᴅɪʀᴇᴄᴛ ᴅᴇᴛᴀɪʟs.</b></blockquote>"""

FORCE_CHANNELS = [
    ("wasteBotz", "🛡️ SUPPORT CHANNEL"),
    ("wasteuserbotUpdates", "📢 UPDATE CHANNEL"),
]


FORCE_COMMANDS = [
    "Autopic", "admin", "afk", "animation", "anime_cf", "antipm", "autoscroll", "banall", "birthday", "broadcast", "carbon", "clone",
    "create", "destruct", "dictionary", "dmspam", "emoji", "flirt", "globals", "google", "info", "invite", "joinleave", "locks",
    "memify", "mention", "metrics", "paste", "pats", "ping", "profile", "purge", "quotly", "raid", "replyraid", "restart",
    "sangmata", "screenshot", "spam", "start", "stats", "sticker", "stickers", "sudos", "tag", "tagalert", "tagall", "text",
    "tiny", "translate", "truth-dare", "update", "upload", "vctools", "vulgar", "waifu", "weather", "VcFight", "promotion", "aichat",
    "Music", "AutoTextPromo"
]

def _force_page_text(page=0):
    page = max(0, min(int(page), 5))
    chunks = [FORCE_COMMANDS[i:i+11] for i in range(0, 55, 11)] + [FORCE_COMMANDS[55:]]
    lines = [f"<blockquote>{PE(5992130701120507687)} <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ꜰᴏʀᴄᴇ ᴄᴏᴍᴍᴀɴᴅs</b>", "", f"{PE(5226512880362332956)} <b>ᴘᴀɢᴇ {page+1}/6</b>", ""]
    lines.extend(f"{PE(5989952280823076303)} <b>{name}</b>" for name in chunks[page])
    lines.append("</blockquote>")
    return "\n".join(lines)

def _force_keyboard(page=0):
    page = max(0, min(int(page), 5))
    chunks = [FORCE_COMMANDS[i:i+11] for i in range(0, 55, 11)] + [FORCE_COMMANDS[55:]]
    rows = []
    chunk = chunks[page]
    for i in range(0, len(chunk), 2):
        row = [InlineKeyboardButton(f"✦ {chunk[i]}", callback_data=f"force_mod:{chunk[i]}")]
        if i + 1 < len(chunk):
            row.append(InlineKeyboardButton(f"✦ {chunk[i+1]}", callback_data=f"force_mod:{chunk[i+1]}"))
        rows.append(row)
    nav=[]
    if page > 0:
        nav.append(InlineKeyboardButton("ʙᴀᴄᴋ", callback_data=f"force_page:{page-1}"))
    nav.append(InlineKeyboardButton(f"ᴘᴀɢᴇ {page+1}/6", callback_data="force_noop"))
    if page < 5:
        nav.append(InlineKeyboardButton("ɴᴇxᴛ", callback_data=f"force_page:{page+1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton("ᴍᴀɪɴ ᴍᴇɴᴜ", callback_data="force_help")])
    return InlineKeyboardMarkup(rows)


def _recordings_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ADDRC", callback_data="force_record:addrc"), InlineKeyboardButton("🗑️ REMOVERC", callback_data="force_record:removerc")],
        [InlineKeyboardButton("📂 MYRC", callback_data="force_record:myrc"), InlineKeyboardButton("ℹ️ RCINFO", callback_data="force_record:rcinfo")],
        [InlineKeyboardButton("🔊 BASS 100–500", callback_data="force_record:bass")],
        [InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="force_menu")],
    ])


def _force_join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡️ ᴅᴇᴘʟᴏʏ", url="https://t.me/wasteBotz")],
        [InlineKeyboardButton("📢 ᴅᴇᴘʟᴏʏ", url="https://t.me/wasteuserbotUpdates")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ", callback_data="force_check")],
    ])


def _force_join_text():
    return f"""<blockquote>{PE(5989952280823076303)} <b>ＷＡＳＴＥ Ｘ 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐇𝐎𝐒𝐓</b>

{PE(5989952280823076303)} <b>ᴜꜱᴇʀ : 𝐉 𝐏 𝐄 𝐗 𝐎 🚩</b>
{PE(5989952280823076303)} <b>ꜱᴛᴀᴛᴜꜱ : ❌ ɪɴᴀᴄᴛɪᴠᴇ</b>

{PE(5989952280823076303)} <b>ᴡᴇʟᴄᴏᴍᴇ! ᴅᴇᴘʟᴏʏ ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ᴜꜱᴇʀʙᴏᴛ ɪɴꜱᴛᴀɴᴛʟʏ ᴡɪᴛʜ ꜱᴇᴄᴜʀᴇ ᴏᴛᴘ ʟᴏɢɪɴ.</b>

{PE(5445284980978621387)} <b>ᴊᴏɪɴ sᴜᴘᴘᴏʀᴛ + ᴜᴘᴅᴀᴛᴇs ᴛᴏ ᴜɴʟᴏᴄᴋ ᴀᴄᴄᴇss.</b>
{PE(5992130701120507687)} <b>ᴀғᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴛᴀᴘ ᴅᴇᴘʟᴏʏ ᴛᴏ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ.</b></blockquote>"""


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
    try:
        await message.reply_video(FORCE_VIDEO_URL, caption=_force_join_text(), reply_markup=_force_join_keyboard(), parse_mode=enums.ParseMode.HTML, supports_streaming=True)
    except Exception:
        try:
            await message.reply_photo(ALIVE_PIC, caption=_force_join_text(), reply_markup=_force_join_keyboard(), parse_mode=enums.ParseMode.HTML)
        except Exception:
            await message.reply_text(_force_join_text(), reply_markup=_force_join_keyboard(), parse_mode=enums.ParseMode.HTML)


def _group_help_keyboard():
    explicit = ["Autopic", "admin", "afk", "animation", "anime_cf", "antipm", "autoscroll", "banall", "birthday", "broadcast", "carbon", "clone", "create", "destruct", "dictionary", "dmspam", "emoji", "flirt", "globals", "google", "info", "invite", "joinleave", "locks", "memify", "mention", "metrics", "paste", "pats", "ping", "profile", "purge", "quotly", "raid", "replyraid", "restart", "sangmata", "screenshot", "spam", "start", "stats", "sticker", "stickers", "sudos", "tag", "tagalert", "tagall", "text", "tiny", "translate", "truth-dare", "update", "upload", "vctools", "vulgar", "waifu", "weather", "promotion", "aichat", "vctalk", "autoreact", "mmar", "omar", "Music", "VcFight", "AutoTextPromo"]
    keys = list(dict.fromkeys(explicit + list(CMD_HELP.keys())))
    rows = []
    for i in range(0, len(keys), 2):
        row = [InlineKeyboardButton(keys[i], callback_data=f"grouphelp:{keys[i]}")]
        if i + 1 < len(keys):
            row.append(InlineKeyboardButton(keys[i + 1], callback_data=f"grouphelp:{keys[i + 1]}"))
        rows.append(row)
    return InlineKeyboardMarkup(rows)


MODULE_ALIASES = {
    "music": "Music", "song": "Music", "play": "Music",
    "autotextpromo": "AutoTextPromo", "autotext": "AutoTextPromo",
    "vcfight": "VcFight", "vc fight": "VcFight", "recordings": "VcFight", "record": "VcFight",
    "aichat": "AI Chat", "ai chat": "AI Chat",
    "welcome": "Welcome", "promotion": "Promotion",
    "autopic": "Autopic",
    "vctalk": "VcTalk", "vc talk": "VcTalk",
    "autoreact": "Promotion", "mmar": "ReactionPlus", "omar": "ReactionPlus",
}

# Modules that may not register a CMD_HELP block still get a useful usage page.
MODULE_FALLBACKS = {
    "AutoTextPromo": [
        ("autotextpromo on", "Enable automatic promotional text."),
        ("autotextpromo off", "Disable automatic promotional text."),
    ],
    "AI Chat": [
        ("aichat on", "Enable AI replies."),
        ("aichat off", "Disable AI replies."),
        ("aichat status", "Show the current AI-chat status."),
    ],
    "Welcome": [
        ("welcome on", "Enable automatic welcome messages."),
        ("welcome off", "Disable automatic welcome messages."),
    ],
    "VcTalk": [
        ("vctalk on", "Enable AI voice conversation in the current VC."),
        ("vctalk off", "Disable AI voice conversation in the current VC."),
        ("vctalk status", "Show VC Talk status."),
    ],
    "ReactionPlus": [
        ("mmar on 😂😭😑🤣💔🖕🍌", "React to your own messages with the selected emoji pool."),
        ("mmar off", "Disable reactions on your own messages."),
        ("omar on @username", "Target a user and react to their messages."),
        ("omar on 123456789", "Target a user by ID and react to their messages."),
        ("omar off", "Disable target reactions."),
    ],
}

# Every command displayed in the Force Commands menu gets a usable help page,
# even when its legacy module has no CMD_HELP registration.
_GENERIC_COMMANDS = [
    "autopic", "admin", "afk", "animation", "anime_cf", "antipm", "autoscroll",
    "banall", "birthday", "broadcast", "carbon", "clone", "create", "destruct",
    "dictionary", "dmspam", "emoji", "flirt", "globals", "google", "info", "invite",
    "joinleave", "locks", "memify", "mention", "metrics", "paste", "pats", "ping",
    "profile", "purge", "quotly", "raid", "replyraid", "restart", "sangmata",
    "screenshot", "spam", "start", "stats", "sticker", "stickers", "sudos", "tag",
    "tagalert", "tagall", "text", "tiny", "translate", "truth-dare", "update",
    "upload", "vctools", "vulgar", "waifu", "weather",
]
for _cmd in _GENERIC_COMMANDS:
    _key = _cmd
    MODULE_FALLBACKS.setdefault(_key, [
        (_cmd, f"Use <code>.{_cmd}</code> or <code>/{_cmd}</code>. This command is available from the connected userbot.")
    ])

def _find_help_key(name: str):
    """Resolve a module name, command name, or common alias reliably."""
    name = (name or "").strip().lower().lstrip("./")
    if not name:
        return None
    if name in MODULE_ALIASES:
        return MODULE_ALIASES[name]
    # Exact module-name match, case-insensitive.
    for key in CMD_HELP:
        if str(key).strip().lower() == name:
            return key
    # Match a registered command (including commands with arguments).
    for key, commands in CMD_HELP.items():
        iterable = commands.keys() if isinstance(commands, dict) else [x[0] for x in commands if x]
        for command in iterable:
            first = str(command).strip().lstrip("./").split()[0].lower()
            if first == name:
                return key
    # Finally, resolve every module shown in the force menu even if that
    # module did not register CMD_HELP yet. This prevents `.help <command>`
    # from falling through to the old "Not a Valid Module Name" response.
    explicit = {
        "autopic":"Autopic", "admin":"admin", "afk":"afk",
        "animation":"animation", "anime_cf":"anime_cf", "antipm":"antipm",
        "autoscroll":"autoscroll", "banall":"banall", "birthday":"birthday",
        "broadcast":"broadcast", "carbon":"carbon", "clone":"clone",
        "create":"create", "destruct":"destruct", "dictionary":"dictionary",
        "dmspam":"dmspam", "emoji":"emoji", "flirt":"flirt", "globals":"globals",
        "google":"google", "info":"info", "invite":"invite", "joinleave":"joinleave",
        "locks":"locks", "memify":"memify", "mention":"mention", "metrics":"metrics",
        "paste":"paste", "pats":"pats", "ping":"ping", "profile":"profile",
        "purge":"purge", "quotly":"quotly", "raid":"raid", "replyraid":"replyraid",
        "restart":"restart", "sangmata":"sangmata", "screenshot":"screenshot",
        "spam":"spam", "start":"start", "stats":"stats", "sticker":"sticker",
        "stickers":"stickers", "sudos":"sudos", "tag":"tag", "tagalert":"tagalert",
        "tagall":"tagall", "text":"text", "tiny":"tiny", "translate":"translate",
        "truth-dare":"truth-dare", "update":"update", "upload":"upload",
        "vctools":"vctools", "vulgar":"vulgar", "waifu":"waifu", "weather":"weather",
        "promotion":"Promotion", "aichat":"AI Chat", "vctalk":"VcTalk",
        "autoreact":"Promotion", "mmar":"ReactionPlus", "omar":"ReactionPlus",
        "music":"Music", "song":"Music", "play":"Music", "vcfight":"VcFight",
        "recordings":"VcFight", "record":"VcFight", "autotextpromo":"AutoTextPromo",
        "autotext":"AutoTextPromo", "welcome":"Welcome",
    }
    return explicit.get(name)


def _module_text(key):
    commands = CMD_HELP.get(key, {})
    if commands and not isinstance(commands, dict):
        try:
            commands = dict(commands)
        except Exception:
            commands = {}
    if not commands:
        commands = dict(MODULE_FALLBACKS.get(key, []))
    if not commands:
        return f"<blockquote><b>❌ {key}</b>\n\nNo command details are registered for this module yet.</blockquote>"
    lines = [f"<blockquote><b>❖ {key.upper()} COMMANDS</b></blockquote>", ""]
    for command, desc in commands.items():
        command = str(command).strip()
        if command.startswith((".", "/")):
            display = command
        else:
            display = f".{command}"
        slash = display.replace(".", "/", 1) if display.startswith(".") else display
        lines.append(f"<blockquote>• <code>{display}</code>  |  <code>{slash}</code>\n  {desc}</blockquote>")
    return "\n".join(lines)


@Client.on_message(filters.command("force", [".", "/"]) & (filters.me | filters.user(SUDO_USER)))
async def force_command(client, message):
    if not await _joined(client, message.from_user.id if message.from_user else (await client.get_me()).id):
        return await _send_force_join(client, message)
    try:
        return await message.reply_video(FORCE_VIDEO_URL, caption=_force_page_text(0), reply_markup=_force_keyboard(0), parse_mode=enums.ParseMode.HTML, supports_streaming=True)
    except Exception:
        return await message.reply_text(_force_page_text(0), reply_markup=_force_keyboard(0), parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command(["help", "helpme"], [".", "/"]) & (filters.me | filters.user(SUDO_USER)))
async def module_help(client: Client, message: Message):
    help_arg = " ".join(message.command[1:]).strip() if len(message.command) > 1 else ""
    is_private = bool(message.chat and getattr(message.chat.type, "value", message.chat.type) == "private")

    if is_private:
        if not await _joined(client, message.from_user.id if message.from_user else (await client.get_me()).id):
            return await _send_force_join(client, message)
        if not help_arg:
            return await message.reply_text(
                HELP_MENU,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=_group_help_keyboard(),
            )

    if not help_arg:
        return await message.reply_text(
            HELP_MENU,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=_group_help_keyboard(),
        )

    key = _find_help_key(help_arg)
    if key:
        return await message.reply_text(_module_text(key), parse_mode=enums.ParseMode.HTML)
    await message.reply_text(f"`{help_arg}` **Not a Valid Module Name.**")


@Client.on_callback_query(filters.regex(r"^grouphelp:"))
async def group_help_callback(client, query):
    await query.answer()
    key = query.data.split(":", 1)[1]
    if key == "menu":
        await query.message.edit_text(HELP_MENU, reply_markup=_group_help_keyboard(), parse_mode=enums.ParseMode.HTML)
        return
    text = _module_text(key)
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ALL COMMANDS", callback_data="grouphelp:menu")]]), parse_mode=enums.ParseMode.HTML)

async def _hosted_for_user(user_id):
    try:
        from Waste.modules.bot.start import active_sessions
        for hosted in list(active_sessions):
            if getattr(hosted, "_waste_owner_uid", None) == int(user_id):
                return hosted
    except Exception:
        pass
    return None


def _force_recordings_keyboard(user_id):
    try:
        from Waste.modules.bot.start import recordings_col
        rows = list(recordings_col.find({"user_id": int(user_id)}).sort("created_at", -1).limit(30))
    except Exception:
        rows = []
    buttons = []
    for r in rows:
        rid = str(r.get("_id"))
        name = str(r.get("name", "Recording"))[:30]
        buttons.append([InlineKeyboardButton(f"✦ {name}", callback_data=f"force_rcplay:{rid}")])
    buttons.append([InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="force_menu")])
    return rows, InlineKeyboardMarkup(buttons)


@Client.on_callback_query(filters.regex(r"^force_(menu|help|check|noop|page:|recordings|mod:|record:|rcdelete:|vcplay:|rcplay:)"))
async def force_callback(client, query):
    user_id = query.from_user.id
    if query.data == "force_check":
        if not await _joined(client, user_id):
            await query.answer("Join both channels first.", show_alert=True)
            return
        await query.answer("Verified ✓")
        try:
            await query.message.edit_media(__import__("pyrogram").types.InputMediaVideo(FORCE_VIDEO_URL, caption=_force_page_text(0), parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=_force_keyboard(0))
        except Exception:
            await query.message.edit_text(_force_page_text(0), reply_markup=_force_keyboard(0), parse_mode=enums.ParseMode.HTML)
        return
    if query.data == "force_help":
        await query.answer()
        try:
            await query.message.edit_caption(HELP_MENU, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ FORCE COMMANDS", callback_data="force_menu")]]), parse_mode=enums.ParseMode.HTML)
        except Exception:
            await query.message.edit_text(HELP_MENU, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ FORCE COMMANDS", callback_data="force_menu")]]), parse_mode=enums.ParseMode.HTML)
        return
    if query.data == "force_menu":
        await query.answer()
        try:
            await query.message.edit_media(__import__("pyrogram").types.InputMediaVideo(FORCE_VIDEO_URL, caption=_force_page_text(0), parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=_force_keyboard(0))
        except Exception:
            await query.message.edit_text(_force_page_text(0), reply_markup=_force_keyboard(0), parse_mode=enums.ParseMode.HTML)
        return
    if query.data == "force_noop":
        await query.answer()
        return
    if query.data.startswith("force_page:"):
        page = int(query.data.split(":", 1)[1])
        await query.answer()
        try:
            await query.message.edit_media(__import__("pyrogram").types.InputMediaVideo(FORCE_VIDEO_URL, caption=_force_page_text(page), parse_mode=enums.ParseMode.HTML, supports_streaming=True), reply_markup=_force_keyboard(page))
        except Exception:
            await query.message.edit_text(_force_page_text(page), reply_markup=_force_keyboard(page), parse_mode=enums.ParseMode.HTML)
        return
    if query.data.startswith("force_mod:"):
        key = query.data.split(":", 1)[1]
        await query.answer()
        await query.message.edit_caption(_module_text(key), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="force_menu")]]), parse_mode=enums.ParseMode.HTML) if getattr(query.message, "photo", None) else await query.message.edit_text(_module_text(key), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="force_menu")]]), parse_mode=enums.ParseMode.HTML)
        return
    if query.data == "force_recordings":
        await query.answer()
        text = f"<blockquote>{PE(5992130701120507687)} <b>ᴠᴄғɪɢʜᴛ ʀᴇᴄᴏʀᴅɪɴɢs</b>\n\n{PE(5989952280823076303)} <b>ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ sᴀᴠᴇᴅ ʀᴇᴄᴏʀᴅɪɴɢs ʜᴇʀᴇ.</b></blockquote>"
        return await query.message.edit_text(text, reply_markup=_recordings_keyboard(), parse_mode=enums.ParseMode.HTML)
    if query.data.startswith("force_record:"):
        await query.answer()
        action = query.data.split(":", 1)[1]
        hosted = await _hosted_for_user(user_id)
        if not hosted:
            return await query.message.edit_text("<blockquote>❌ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪᴅ ɪs ɴᴏᴛ ᴏɴʟɪɴᴇ.</blockquote>", parse_mode=enums.ParseMode.HTML)
        if action == "addrc":
            return await query.message.edit_text("<blockquote>➕ <b>ᴀᴅᴅʀᴄ</b>\n\nꜱᴇɴᴅ ᴀɴ ᴀᴜᴅɪᴏ / ᴠᴏɪᴄᴇ ᴛᴏ ᴛʜᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪᴅ ᴄʜᴀᴛ ᴏʀ ᴜsᴇ <code>.addrc</code> ᴏɴ ᴛʜᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪᴅ.</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="force_recordings")]]), parse_mode=enums.ParseMode.HTML)
        if action in {"myrc", "rcinfo", "removerc"}:
            try:
                from Waste.modules.bot.start import recordings_col
                rows = list(recordings_col.find({"user_id": int(user_id)}).sort("created_at", -1).limit(30))
            except Exception:
                rows = []
            if not rows:
                return await query.message.edit_text("<blockquote>📂 ɴᴏ sᴀᴠᴇᴅ ʀᴇᴄᴏʀᴅɪɴɢs.</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="force_recordings")]]), parse_mode=enums.ParseMode.HTML)
            if action == "rcinfo":
                text = "<blockquote>" + PE(5992130701120507687) + " <b>ʀᴇᴄᴏʀᴅɪɴɢ ɪɴғᴏ</b>\n\n" + "\n".join(f"{i+1}. {r.get('name','Recording')} — {int(r.get('duration',0))}s" for i,r in enumerate(rows)) + "</blockquote>"
                return await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="force_recordings")]]), parse_mode=enums.ParseMode.HTML)
            buttons=[]
            for r in rows:
                rid=str(r.get("_id")); name=str(r.get("name","Recording"))[:30]
                cb = f"force_rcplay:{rid}" if action == "myrc" else f"force_rcdelete:{rid}"
                buttons.append([InlineKeyboardButton(f"✦ {name}", callback_data=cb)])
            buttons.append([InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="force_recordings")])
            title = "📂 ᴍʏ ʀᴇᴄᴏʀᴅɪɴɢs" if action == "myrc" else "🗑️ ʀᴇᴍᴏᴠᴇ ʀᴇᴄᴏʀᴅɪɴɢ"
            return await query.message.edit_text(f"<blockquote>{PE(5992130701120507687)} <b>{title}</b>\n\nꜱᴇʟᴇᴄᴛ ᴀ ʀᴇᴄᴏʀᴅɪɴɢ.</blockquote>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        if action == "bass":
            return await query.message.edit_text("<blockquote>🔊 <b>ʙᴀss</b>\n\nᴜsᴇ <code>.bass 100</code> ᴛᴏ <code>.bass 500</code> ᴏɴ ᴛʜᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪᴅ.</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="force_recordings")]]), parse_mode=enums.ParseMode.HTML)
        return
    if query.data.startswith("force_rcdelete:"):
        await query.answer()
        try:
            from bson import ObjectId
            from Waste.modules.bot.start import recordings_col
            rid = ObjectId(query.data.split(":", 1)[1])
            rec = recordings_col.find_one({"_id": rid, "user_id": int(user_id)})
            if not rec:
                return await query.answer("Recording not found", show_alert=True)
            recordings_col.delete_one({"_id": rid, "user_id": int(user_id)})
            try:
                import os
                if rec.get("path") and os.path.exists(rec["path"]): os.remove(rec["path"])
            except Exception:
                pass
            return await query.message.edit_text("<blockquote>🗑️ ʀᴇᴄᴏʀᴅɪɴɢ ʀᴇᴍᴏᴠᴇᴅ.</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="force_recordings")]]), parse_mode=enums.ParseMode.HTML)
        except Exception as exc:
            return await query.answer(f"Delete failed: {type(exc).__name__}", show_alert=True)
    if query.data.startswith("force_rcplay:"):
        await query.answer()
        try:
            from bson import ObjectId
            from Waste.modules.bot.start import recordings_col
            from Waste.modules.basic.vcfight import _bridge, _states
            rid = ObjectId(query.data.split(":", 1)[1])
            rec = recordings_col.find_one({"_id": rid, "user_id": int(user_id)})
            if not rec:
                return await query.answer("Recording not found", show_alert=True)
            state, call = await _bridge(hosted)
            joined = sorted(list(state.joined))
            if not joined:
                return await query.message.edit_text("<blockquote>❌ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪᴅ ɪs ɴᴏᴛ ɪɴ ᴀɴʏ ᴠᴄ. ᴜsᴇ <code>.join &lt;chat_id&gt;</code> ᴏɴ ᴛʜᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪᴅ ғɪʀsᴛ.</blockquote>", parse_mode=enums.ParseMode.HTML)
            kb=[[InlineKeyboardButton(f"▶️ ᴘʟᴀʏ ɪɴ {cid}", callback_data=f"force_vcplay:{rid}:{cid}")] for cid in joined]
            kb.append([InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="force_recordings")])
            return await query.message.edit_text(f"<blockquote>{PE(5992130701120507687)} <b>ᴄʜᴏᴏsᴇ ᴠᴄ</b>\n\n🎙️ {rec.get('name','Recording')}</blockquote>", reply_markup=InlineKeyboardMarkup(kb), parse_mode=enums.ParseMode.HTML)
        except Exception as exc:
            return await query.answer(f"Play menu failed: {type(exc).__name__}", show_alert=True)
    if query.data.startswith("force_vcplay:"):
        await query.answer()
        try:
            from bson import ObjectId
            from Waste.modules.bot.start import recordings_col
            from Waste.modules.basic.vcfight import _bridge
            _, call = await _bridge(hosted)
            _, rid, cid = query.data.split(":", 2)
            rec = recordings_col.find_one({"_id": ObjectId(rid), "user_id": int(user_id)})
            if not rec:
                return await query.answer("Recording not found", show_alert=True)
            await call.play(int(cid), rec["path"], config=__import__("pytgcalls").types.GroupCallConfig(auto_start=False))
            return await query.message.edit_text(f"<blockquote>▶️ <b>ɴᴏᴡ ᴘʟᴀʏɪɴɢ</b>\n\n🎙️ {rec.get('name','Recording')}\n🔊 ᴠᴄ: <code>{cid}</code></blockquote>", parse_mode=enums.ParseMode.HTML)
        except Exception as exc:
            return await query.answer(f"Play failed: {type(exc).__name__}", show_alert=True)


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
        return await message.reply_text(_module_text(key), parse_mode=enums.ParseMode.HTML)
    await message.reply_text(f"`{help_arg}` **Not a Valid Module Name.**")


def add_command_help(module_name, commands):
    command_dict = CMD_HELP.get(module_name, {})
    for item in commands:
        if not item:
            continue
        command_dict[item[0]] = item[1]
    CMD_HELP[module_name] = command_dict
