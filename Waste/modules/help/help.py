from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Waste import app, CMD_HELP, SUDO_USER
from config import ALIVE_PIC

# Premium custom-emoji IDs requested for the WASTE X UBOT UI.
PREMIUM_MAIN = "5989952280823076303"
PREMIUM_HELP = "5992130701120507687"
PREMIUM_NEXT = "5445284980978621387"
PREMIUM_PAGE = "5226512880362332956"
PREMIUM_QUOTE = "5992095761561554607"
PREMIUM_START = "5989975649740134220"


def _ce(emoji_id: str, fallback: str = "✦") -> str:
    """Telegram HTML custom emoji tag; fallback keeps plain-text readability."""
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


# Exact connected-ID help list requested by the user. It is split into six pages.
HELP_COMMANDS = [
    "Autopic", "admin", "afk", "animation", "anime_cf", "antipm",
    "autoscroll", "banall", "birthday", "broadcast", "carbon", "clone",
    "create", "destruct", "dictionary", "dmspam", "emoji", "flirt",
    "globals", "google", "info", "invite", "joinleave", "locks",
    "memify", "mention", "metrics", "paste", "pats", "ping", "profile",
    "purge", "quotly", "raid", "replyraid", "restart", "sangmata",
    "screenshot", "spam", "start", "stats", "sticker", "stickers", "sudos",
    "tag", "tagalert", "tagall", "text", "tiny", "translate", "truth-dare",
    "update", "upload", "vctools", "vulgar", "waifu", "weather", "VcFight",
    "promotion", "aichat", "Music", "AutoTextPromo",
]

PAGE_SIZE = 12
PAGE_COUNT = 6


def _help_page_text(page: int = 0) -> str:
    page = max(0, min(PAGE_COUNT - 1, int(page)))
    chunk = HELP_COMMANDS[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    lines = [
        f'<blockquote><b>{_ce(PREMIUM_HELP)} ＷＡＳＴＥ Ｘ ＵＢＯＴ — ᴅᴇᴘʟᴏʏ COMMANDS</b></blockquote>',
        f'{_ce(PREMIUM_HELP)} <b>Choose a command/module below to open its details.</b>',
        f'{_ce(PREMIUM_HELP)} Tap any command to view its usage.',
        f'{_ce(PREMIUM_HELP)} Music, VcFight and Recordings have their own command pages.',
        f'{_ce(PREMIUM_HELP)} Use <code>.help &lt;command&gt;</code> from a connected ID for direct details.',
        f'{_ce(PREMIUM_PAGE)} <b>PAGE {page + 1}/{PAGE_COUNT}</b>',
        "",
    ]
    for i in range(0, len(chunk), 2):
        left = chunk[i]
        right = chunk[i + 1] if i + 1 < len(chunk) else ""
        if right:
            lines.append(f'<code>{left:<22}</code> <code>{right}</code>')
        else:
            lines.append(f'<code>{left}</code>')
    lines.append("")
    lines.append(f'{_ce(PREMIUM_MAIN)} @wasteuserbotUpdates × @wasteBotz')
    return "<blockquote>" + "\n".join(lines) + "</blockquote>"


def _help_page_keyboard(page: int = 0):
    page = max(0, min(PAGE_COUNT - 1, int(page)))
    chunk = HELP_COMMANDS[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    rows = []
    for i in range(0, len(chunk), 2):
        row = [InlineKeyboardButton(chunk[i], callback_data=f"grouphelp:cmd:{chunk[i]}")]
        if i + 1 < len(chunk):
            row.append(InlineKeyboardButton(chunk[i + 1], callback_data=f"grouphelp:cmd:{chunk[i+1]}"))
        rows.append(row)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ PREV", callback_data=f"grouphelp:page:{page-1}"))
    nav.append(InlineKeyboardButton(f"PAGE {page+1}/{PAGE_COUNT}", callback_data="grouphelp:noop"))
    if page < PAGE_COUNT - 1:
        nav.append(InlineKeyboardButton("ᴅᴇᴘʟᴏʏ NEXT ➜", callback_data=f"grouphelp:page:{page+1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton("🏠 MAIN MENU", callback_data="home")])
    return InlineKeyboardMarkup(rows)


HELP_MENU = _help_page_text(0)

FORCE_TEXT = f"""<blockquote><b>{_ce(PREMIUM_HELP)} ＷＡＳＴＥ Ｘ ＵＢＯＴ — ᴅᴇᴘʟᴏʏ FORCE COMMANDS</b>

{_ce(PREMIUM_HELP)} Choose a command/module below to open its details.
{_ce(PREMIUM_HELP)} Tap any command to view its usage.
{_ce(PREMIUM_HELP)} Music, VcFight and Recordings have their own command pages.
{_ce(PREMIUM_HELP)} Use <code>.help &lt;command&gt;</code> from a connected ID for direct details.</blockquote>"""

FORCE_CHANNELS = [
    ("wasteBotz", "SUPPORT CHANNEL"),
    ("wasteuserbotUpdates", "UPDATE CHANNEL"),
]


def _force_keyboard():
    rows = [
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ MUSIC / SONG", callback_data="force_mod:Music"), InlineKeyboardButton("ᴅᴇᴘʟᴏʏ VCFIGHT", callback_data="force_mod:VcFight")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ RECORDINGS", callback_data="force_recordings"), InlineKeyboardButton("ᴅᴇᴘʟᴏʏ AUTOTEXTPROMO", callback_data="force_mod:AutoTextPromo")],
    ]
    keys = list(dict.fromkeys(HELP_COMMANDS + list(CMD_HELP.keys()) + list(MODULE_ALIASES.values())))
    keys = [k for k in keys if k not in {"Music", "VcFight", "AutoTextPromo", "Promotion"}]
    # Six pages, matching the connected-ID help design.
    page = 0
    chunk = keys[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    for i in range(0, len(chunk), 2):
        row = [InlineKeyboardButton(f"✦ {chunk[i]}", callback_data=f"force_mod:{chunk[i]}")]
        if i + 1 < len(chunk):
            row.append(InlineKeyboardButton(f"✦ {chunk[i+1]}", callback_data=f"force_mod:{chunk[i+1]}"))
        rows.append(row)
    rows.append([InlineKeyboardButton("ᴅᴇᴘʟᴏʏ NEXT ➜", callback_data="force_page:1")])
    rows.append([InlineKeyboardButton("🏠 MAIN MENU", callback_data="home")])
    return InlineKeyboardMarkup(rows)


def _force_page_keyboard(page: int = 0):
    keys = list(dict.fromkeys(HELP_COMMANDS + list(CMD_HELP.keys()) + list(MODULE_ALIASES.values())))
    keys = [k for k in keys if k not in {"Music", "VcFight", "AutoTextPromo", "Promotion"}]
    total = max(1, (len(keys) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(total - 1, int(page)))
    chunk = keys[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    rows = [
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ MUSIC / SONG", callback_data="force_mod:Music"), InlineKeyboardButton("ᴅᴇᴘʟᴏʏ VCFIGHT", callback_data="force_mod:VcFight")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ RECORDINGS", callback_data="force_recordings"), InlineKeyboardButton("ᴅᴇᴘʟᴏʏ AUTOTEXTPROMO", callback_data="force_mod:AutoTextPromo")],
    ]
    for i in range(0, len(chunk), 2):
        row = [InlineKeyboardButton(f"{chunk[i]}", callback_data=f"force_mod:{chunk[i]}")]
        if i + 1 < len(chunk):
            row.append(InlineKeyboardButton(f"{chunk[i+1]}", callback_data=f"force_mod:{chunk[i+1]}"))
        rows.append(row)
    nav=[]
    if page>0: nav.append(InlineKeyboardButton("◀️ PREV", callback_data=f"force_page:{page-1}"))
    nav.append(InlineKeyboardButton(f"PAGE {page+1}/{total}", callback_data="force_noop"))
    if page<total-1: nav.append(InlineKeyboardButton("ᴅᴇᴘʟᴏʏ NEXT ➜", callback_data=f"force_page:{page+1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton("🏠 MAIN MENU", callback_data="home")])
    return InlineKeyboardMarkup(rows)


def _recordings_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ ADDRC", callback_data="force_record:addrc"), InlineKeyboardButton("ᴅᴇᴘʟᴏʏ REMOVERC", callback_data="force_record:removerc")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ MYRC", callback_data="force_record:myrc"), InlineKeyboardButton("ᴅᴇᴘʟᴏʏ RCINFO", callback_data="force_record:rcinfo")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ BASS 100–500", callback_data="force_record:bass")],
        [InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="force_menu")],
    ])


def _force_join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ SUPPORT ➜", url="https://t.me/wasteBotz")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ UPDATES ➜", url="https://t.me/wasteuserbotUpdates")],
        [InlineKeyboardButton("ᴅᴇᴘʟᴏʏ CHECK AGAIN", callback_data="force_check")],
    ])


def _force_join_text():
    return f"""<blockquote>{_ce(PREMIUM_MAIN)} <b>WASTE X USERBOT</b>

{_ce(PREMIUM_MAIN)} <b>ᴜꜱᴇʀ : 𝐉 𝐏 𝐄 𝐗 𝐎 🚩</b>
{_ce(PREMIUM_MAIN)} <b>ꜱᴛᴀᴛᴜꜱ : ❌ ɪɴᴀᴄᴛɪᴠᴇ</b>

{_ce(PREMIUM_MAIN)} <i>ᴡᴇʟᴄᴏᴍᴇ! ᴅᴇᴘʟᴏʏ ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ᴜꜱᴇʀʙᴏᴛ ɪɴꜱᴛᴀɴᴛʟʏ ᴡɪᴛʜ ꜱᴇᴄᴜʀᴇ ᴏᴛᴘ ʟᴏɢɪɴ.</i></blockquote>"""


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
    # The force-join gate intentionally uses the configured ALIVE_PIC here.
    # /start in the bot module supplies the video version after verification.
    try:
        await message.reply_photo(ALIVE_PIC, caption=_force_join_text(), reply_markup=_force_join_keyboard(), parse_mode=enums.ParseMode.HTML)
    except Exception:
        await message.reply_text(_force_join_text(), reply_markup=_force_join_keyboard(), parse_mode=enums.ParseMode.HTML)


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

MODULE_FALLBACKS = {
    "AutoTextPromo": [("autotextpromo on", "Enable automatic promotional text."), ("autotextpromo off", "Disable automatic promotional text.")],
    "AI Chat": [("aichat on", "Enable AI replies."), ("aichat off", "Disable AI replies."), ("aichat status", "Show the current AI-chat status.")],
    "Welcome": [("welcome on", "Enable automatic welcome messages."), ("welcome off", "Disable automatic welcome messages.")],
    "VcTalk": [("vctalk on", "Enable AI voice conversation in the current VC."), ("vctalk on {chat_id}", "Enable AI voice conversation only in the specified VC."), ("vctalk off", "Disable AI voice conversation in the current VC."), ("vctalk off {chat_id}", "Disable AI voice conversation only in the specified VC."), ("vctalk status", "Show VC Talk status.")],
    "ReactionPlus": [("mmar on 😂😭😑🤣💔🖕🍌", "React to your own messages with the selected emoji pool."), ("mmar off", "Disable reactions on your own messages."), ("omar on @username", "Target a user and react to their messages."), ("omar on 123456789", "Target a user by ID and react to their messages."), ("omar on (reply)", "Reply to a user's message and enable reactions for that user."), ("omar off", "Disable target reactions.")],
}

_GENERIC_COMMANDS = [
    "autopic", "admin", "afk", "animation", "anime_cf", "antipm", "autoscroll", "banall", "birthday", "broadcast", "carbon", "clone", "create", "destruct", "dictionary", "dmspam", "emoji", "flirt", "globals", "google", "info", "invite", "joinleave", "locks", "memify", "mention", "metrics", "paste", "pats", "ping", "profile", "purge", "quotly", "raid", "replyraid", "restart", "sangmata", "screenshot", "spam", "start", "stats", "sticker", "stickers", "sudos", "tag", "tagalert", "tagall", "text", "tiny", "translate", "truth-dare", "update", "upload", "vctools", "vulgar", "waifu", "weather",
]
for _cmd in _GENERIC_COMMANDS:
    MODULE_FALLBACKS.setdefault(_cmd, [(_cmd, f"Use <code>.{_cmd}</code> or <code>/{_cmd}</code> from the connected ID.")])

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
        return await message.reply_photo(ALIVE_PIC, caption=FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)
    except Exception:
        return await message.reply_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command(["help", "helpme"], [".", "/"]) & (filters.me | filters.user(SUDO_USER)))
async def module_help(client: Client, message: Message):
    help_arg = " ".join(message.command[1:]).strip() if len(message.command) > 1 else ""
    is_private = bool(message.chat and getattr(message.chat.type, "value", message.chat.type) == "private")

    if is_private:
        if not await _joined(client, message.from_user.id if message.from_user else (await client.get_me()).id):
            return await _send_force_join(client, message)
        if not help_arg:
            try:
                return await message.reply_photo(ALIVE_PIC, caption=FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)
            except Exception:
                return await message.reply_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)

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
            await query.message.edit_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)
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
            await query.message.edit_caption(HELP_MENU, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)
        except Exception:
            await query.message.edit_text(HELP_MENU, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)
        return
    if query.data.startswith("force_mod:"):
        key = query.data.split(":", 1)[1]
        await query.answer()
        await query.message.edit_caption(_module_text(key), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="force_menu")]]), parse_mode=enums.ParseMode.HTML) if getattr(query.message, "photo", None) else await query.message.edit_text(_module_text(key), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="force_menu")]]), parse_mode=enums.ParseMode.HTML)
        return
    if query.data.startswith("force_record:"):
        await query.answer()
        action = query.data.split(":", 1)[1]
        if action in {"addrc", "removerc", "myrc", "rcinfo"}:
            try:
                from Waste.modules.basic import vcfight as vf
                if action == "addrc":
                    uid = getattr(client, "_waste_owner_uid", None)
                    if uid:
                        vf._pending_recording.add(int(uid))
                    text = "<blockquote><b>➕ ADDRC</b>\n\n🎙️ Send the next audio/voice message now. It will be saved automatically.</blockquote>"
                    await query.message.edit_caption(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 RECORDINGS", callback_data="force_recordings")]]), parse_mode=enums.ParseMode.HTML) if getattr(query.message, "photo", None) else await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 RECORDINGS", callback_data="force_recordings")]]), parse_mode=enums.ParseMode.HTML)
                    return
                fn = {"removerc": vf.remove_rc, "myrc": vf.my_rc, "rcinfo": vf.rc_info}[action]
                await query.message.delete()
                await fn(client, query.message)
                return
            except Exception:
                pass
        descriptions = {
            "bass": "<blockquote><b>🔊 BASS</b>\n\nUse <code>.bass 100</code> through <code>.bass 500</code> to control the recording playback bass level.</blockquote>",
        }
        text = descriptions.get(action, "<blockquote>Use the corresponding recording command from the menu.</blockquote>")
        await query.message.edit_caption(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 RECORDINGS", callback_data="force_recordings")]]), parse_mode=enums.ParseMode.HTML) if getattr(query.message, "photo", None) else await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 RECORDINGS", callback_data="force_recordings")]]), parse_mode=enums.ParseMode.HTML)
        return
    if query.data == "force_recordings":
        await query.answer()
        text = "<blockquote><b>🎙️ VCFIGHT RECORDINGS</b>\n\nManage your saved recordings below.</blockquote>"
        await query.message.edit_caption(text, reply_markup=_recordings_keyboard(), parse_mode=enums.ParseMode.HTML) if getattr(query.message, "photo", None) else await query.message.edit_text(text, reply_markup=_recordings_keyboard(), parse_mode=enums.ParseMode.HTML)


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




@Client.on_message(filters.command("force", [".", "/"]) & (filters.me | filters.user(SUDO_USER)))
async def force_command(client, message):
    if not await _joined(client, message.from_user.id if message.from_user else (await client.get_me()).id):
        return await _send_force_join(client, message)
    try:
        return await message.reply_photo(ALIVE_PIC, caption=FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)
    except Exception:
        return await message.reply_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command(["help", "helpme"], [".", "/"]) & (filters.me | filters.user(SUDO_USER)))
async def module_help(client: Client, message: Message):
    help_arg = " ".join(message.command[1:]).strip() if len(message.command) > 1 else ""
    is_private = bool(message.chat and getattr(message.chat.type, "value", message.chat.type) == "private")
    if is_private and not await _joined(client, message.from_user.id if message.from_user else (await client.get_me()).id):
        return await _send_force_join(client, message)
    if not help_arg:
        return await message.reply_text(_help_page_text(0), parse_mode=enums.ParseMode.HTML, reply_markup=_help_page_keyboard(0))
    key = _find_help_key(help_arg)
    if key:
        return await message.reply_text(_module_text(key), parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ALL COMMANDS", callback_data="grouphelp:page:0")]]))
    return await message.reply_text(f"❌ <code>{help_arg}</code> — Not a Valid Module Name.", parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^grouphelp:"))
async def group_help_callback(client, query):
    await query.answer()
    data = query.data.split(":", 2)
    if len(data) >= 2 and data[1] == "noop":
        return
    if len(data) >= 3 and data[1] == "page":
        page = int(data[2])
        return await query.message.edit_text(_help_page_text(page), reply_markup=_help_page_keyboard(page), parse_mode=enums.ParseMode.HTML)
    if len(data) >= 3 and data[1] == "cmd":
        key = _find_help_key(data[2]) or data[2]
        return await query.message.edit_text(_module_text(key), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ALL COMMANDS", callback_data="grouphelp:page:0")]]), parse_mode=enums.ParseMode.HTML)
    return await query.message.edit_text(_help_page_text(0), reply_markup=_help_page_keyboard(0), parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^force_(menu|help|check|recordings|mod:|record:|page:|noop)"))
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
            await query.message.edit_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)
        return
    if query.data == "force_noop":
        return
    if query.data.startswith("force_page:"):
        page = int(query.data.split(":", 1)[1])
        await query.answer()
        text = FORCE_TEXT + f"\n\n{_ce(PREMIUM_PAGE)} <b>PAGE {page + 1}</b>"
        try:
            return await query.message.edit_caption(text, reply_markup=_force_page_keyboard(page), parse_mode=enums.ParseMode.HTML)
        except Exception:
            return await query.message.edit_text(text, reply_markup=_force_page_keyboard(page), parse_mode=enums.ParseMode.HTML)
    if query.data == "force_help":
        await query.answer()
        try:
            return await query.message.edit_caption(_help_page_text(0), reply_markup=_help_page_keyboard(0), parse_mode=enums.ParseMode.HTML)
        except Exception:
            return await query.message.edit_text(_help_page_text(0), reply_markup=_help_page_keyboard(0), parse_mode=enums.ParseMode.HTML)
    if query.data == "force_menu":
        await query.answer()
        try:
            return await query.message.edit_caption(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)
        except Exception:
            return await query.message.edit_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode=enums.ParseMode.HTML)
    if query.data.startswith("force_mod:"):
        key = query.data.split(":", 1)[1]
        await query.answer()
        text = _module_text(key)
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="force_menu")]])
        try:
            return await query.message.edit_caption(text, reply_markup=kb, parse_mode=enums.ParseMode.HTML)
        except Exception:
            return await query.message.edit_text(text, reply_markup=kb, parse_mode=enums.ParseMode.HTML)
    if query.data.startswith("force_record:"):
        await query.answer()
        action = query.data.split(":", 1)[1]
        if action in {"addrc", "removerc", "myrc", "rcinfo"}:
            try:
                from Waste.modules.basic import vcfight as vf
                if action == "addrc":
                    uid = getattr(client, "_waste_owner_uid", None)
                    if uid:
                        vf._pending_recording.add(int(uid))
                    text = f"<blockquote>{_ce(PREMIUM_MAIN)} <b>ᴅᴇᴘʟᴏʏ ADDRC</b>\n\n{_ce(PREMIUM_QUOTE)} Send the next audio/voice message now. It will be saved automatically.</blockquote>"
                    return await query.message.edit_text(text, reply_markup=_recordings_keyboard(), parse_mode=enums.ParseMode.HTML)
                fn = {"removerc": vf.remove_rc, "myrc": vf.my_rc, "rcinfo": vf.rc_info}[action]
                return await fn(client, query.message)
            except Exception as exc:
                return await query.message.edit_text(f"❌ Recording action failed: <code>{type(exc).__name__}</code>", reply_markup=_recordings_keyboard(), parse_mode=enums.ParseMode.HTML)
        text = f"<blockquote>{_ce(PREMIUM_MAIN)} <b>ᴅᴇᴘʟᴏʏ BASS</b>\n\nUse <code>.bass 100</code> through <code>.bass 500</code> to control recording playback bass level.</blockquote>"
        return await query.message.edit_text(text, reply_markup=_recordings_keyboard(), parse_mode=enums.ParseMode.HTML)
    if query.data == "force_recordings":
        await query.answer()
        text = f"<blockquote>{_ce(PREMIUM_MAIN)} <b>ᴅᴇᴘʟᴏʏ VCFIGHT RECORDINGS</b>\n\nManage your saved recordings below.</blockquote>"
        return await query.message.edit_text(text, reply_markup=_recordings_keyboard(), parse_mode=enums.ParseMode.HTML)


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
        return await message.reply_text(_module_text(key), parse_mode=enums.ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ALL COMMANDS", callback_data="grouphelp:page:0")]]))
    return await message.reply_text(f"❌ <code>{help_arg}</code> — Not a Valid Module Name.", parse_mode=enums.ParseMode.HTML)

def add_command_help(module_name, commands):
    command_dict = CMD_HELP.get(module_name, {})
    for item in commands:
        if not item:
            continue
        command_dict[item[0]] = item[1]
    CMD_HELP[module_name] = command_dict
