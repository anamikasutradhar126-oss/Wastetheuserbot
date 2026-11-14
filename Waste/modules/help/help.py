from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Waste import app, CMD_HELP, SUDO_USER
from config import ALIVE_PIC

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
• @day1Nomore × @wasteBotz .</blockquote>"""

FORCE_TEXT = """<blockquote><b>👑 ＷＡＳＴＥ Ｘ ＵＢＯＴ — FORCE COMMANDS 👑</b>

✨ Choose a command/module below to open its details.
🔹 Music and VcFight use the existing registered command help.
🔹 Use <code>.help &lt;command&gt;</code> from a connected ID for direct details.</blockquote>"""

FORCE_CHANNELS = [
    ("wasteBotz", "🛡️ SUPPORT CHANNEL"),
    ("wasteuserbotUpdates", "📢 UPDATE CHANNEL"),
]


def _force_keyboard():
    rows = [
        [InlineKeyboardButton("🎵 MUSIC / SONG", callback_data="force_mod:Music"), InlineKeyboardButton("⚔️ VCFIGHT", callback_data="force_mod:VcFight")],
        [InlineKeyboardButton("🎙️ RECORDINGS", callback_data="force_recordings"), InlineKeyboardButton("📢 AUTOTEXTPROMO", callback_data="force_mod:AutoTextPromo")],
    ]
    explicit = ["Autopic", "admin", "afk", "animation", "anime_cf", "antipm", "autoscroll", "banall", "birthday", "broadcast", "carbon", "clone", "create", "destruct", "dictionary", "dmspam", "emoji", "flirt", "globals", "google", "info", "invite", "joinleave", "locks", "memify", "mention", "metrics", "paste", "pats", "ping", "profile", "purge", "quotly", "raid", "replyraid", "restart", "sangmata", "screenshot", "spam", "start", "stats", "sticker", "stickers", "sudos", "tag", "tagalert", "tagall", "text", "tiny", "translate", "truth-dare", "update", "upload", "vctools", "vulgar", "waifu", "weather", "promotion", "aichat"]
    keys = list(dict.fromkeys(explicit + list(CMD_HELP.keys())))
    keys = [k for k in keys if k not in {"Music", "VcFight", "AutoTextPromo", "Promotion"}]
    keys = sorted(keys, key=str.lower)
    for i in range(0, len(keys), 2):
        row = [InlineKeyboardButton(f"📌 {keys[i]}", callback_data=f"force_mod:{keys[i]}")]
        if i + 1 < len(keys):
            row.append(InlineKeyboardButton(f"📌 {keys[i+1]}", callback_data=f"force_mod:{keys[i+1]}"))
        rows.append(row)
    rows.append([InlineKeyboardButton("🔙 HELP MENU", callback_data="force_help")])
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
        [InlineKeyboardButton("🛡️  JOIN SUPPORT  ➜", url="https://t.me/wasteBotz")],
        [InlineKeyboardButton("📢  JOIN UPDATES  ➜", url="https://t.me/wasteuserbotUpdates")],
        [InlineKeyboardButton("💚  ✅ CHECK AGAIN  💚", callback_data="force_check")],
    ])


def _force_join_text():
    return """<blockquote><b>⚠️ FORCE JOIN REQUIRED</b>

To continue using <b>WASTE X UBOT</b>, you must join both channels below.

🛡️ Support: @wasteBotz
📢 Updates: @wasteuserbotUpdates

After joining both channels, tap <b>CHECK AGAIN</b>.</blockquote>"""


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
        await message.reply_photo(ALIVE_PIC, caption=_force_join_text(), reply_markup=_force_join_keyboard(), parse_mode="html")
    except Exception:
        await message.reply_text(_force_join_text(), reply_markup=_force_join_keyboard(), parse_mode="html")


def _group_help_keyboard():
    explicit = ["Autopic", "admin", "afk", "animation", "anime_cf", "antipm", "autoscroll", "banall", "birthday", "broadcast", "carbon", "clone", "create", "destruct", "dictionary", "dmspam", "emoji", "flirt", "globals", "google", "info", "invite", "joinleave", "locks", "memify", "mention", "metrics", "paste", "pats", "ping", "profile", "purge", "quotly", "raid", "replyraid", "restart", "sangmata", "screenshot", "spam", "start", "stats", "sticker", "stickers", "sudos", "tag", "tagalert", "tagall", "text", "tiny", "translate", "truth-dare", "update", "upload", "vctools", "vulgar", "waifu", "weather", "promotion", "aichat", "Music", "VcFight", "AutoTextPromo"]
    keys = list(dict.fromkeys(explicit + list(CMD_HELP.keys())))
    rows = []
    for i in range(0, len(keys), 2):
        row = [InlineKeyboardButton(keys[i], callback_data=f"grouphelp:{keys[i]}")]
        if i + 1 < len(keys):
            row.append(InlineKeyboardButton(keys[i + 1], callback_data=f"grouphelp:{keys[i + 1]}"))
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def _find_help_key(name: str):
    name = (name or "").strip().lower()
    aliases = {"music": "Music", "song": "Music", "play": "Music", "autotextpromo": "AutoTextPromo", "autotext": "AutoTextPromo", "vcfight": "VcFight", "recordings": "VcFight", "record": "VcFight"}
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
            return f"<blockquote><b>❌ {key}</b>\n\nNo command details are registered for this module yet.</blockquote>"
    lines = [f"<blockquote><b>❖ {key.upper()} COMMANDS</b></blockquote>", ""]
    for command, desc in commands.items():
        lines.append(f"<blockquote>• <code>.{command}</code>  |  <code>/{command}</code>\n  {desc}</blockquote>")
    return "\n".join(lines)


@Client.on_message(filters.command("force", [".", "/"]) & (filters.me | filters.user(SUDO_USER)))
async def force_command(client, message):
    if not await _joined(client, message.from_user.id if message.from_user else (await client.get_me()).id):
        return await _send_force_join(client, message)
    try:
        return await message.reply_photo(ALIVE_PIC, caption=FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="html")
    except Exception:
        return await message.reply_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="html")


@Client.on_message(filters.command(["help", "helpme"], [".", "/"]) & (filters.me | filters.user(SUDO_USER)))
async def module_help(client: Client, message: Message):
    help_arg = " ".join(message.command[1:]).strip() if len(message.command) > 1 else ""
    is_private = bool(message.chat and getattr(message.chat.type, "value", message.chat.type) == "private")

    if is_private:
        if not await _joined(client, message.from_user.id if message.from_user else (await client.get_me()).id):
            return await _send_force_join(client, message)
        if not help_arg:
            try:
                return await message.reply_photo(ALIVE_PIC, caption=FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="html")
            except Exception:
                return await message.reply_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="html")

    if not help_arg:
        return await message.reply_text(
            HELP_MENU,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=_group_help_keyboard(),
        )

    key = _find_help_key(help_arg)
    if key:
        return await message.reply_text(_module_text(key), parse_mode="html")
    await message.reply_text(f"`{help_arg}` **Not a Valid Module Name.**")


@Client.on_callback_query(filters.regex(r"^grouphelp:"))
async def group_help_callback(client, query):
    await query.answer()
    key = query.data.split(":", 1)[1]
    if key == "menu":
        await query.message.edit_text(HELP_MENU, reply_markup=_group_help_keyboard(), parse_mode=enums.ParseMode.HTML)
        return
    text = _module_text(key)
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ALL COMMANDS", callback_data="grouphelp:menu")]]), parse_mode="html")

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
            await query.message.edit_text(FORCE_TEXT, reply_markup=_force_keyboard(), parse_mode="html")
        return
    if query.data == "force_help":
        await query.answer()
        try:
            await query.message.edit_caption(HELP_MENU, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ FORCE COMMANDS", callback_data="force_menu")]]), parse_mode="html")
        except Exception:
            await query.message.edit_text(HELP_MENU, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ FORCE COMMANDS", callback_data="force_menu")]]), parse_mode="html")
        return
    if query.data == "force_menu":
        await query.answer()
        try:
            await query.message.edit_caption(HELP_MENU, reply_markup=_force_keyboard(), parse_mode="html")
        except Exception:
            await query.message.edit_text(HELP_MENU, reply_markup=_force_keyboard(), parse_mode="html")
        return
    if query.data.startswith("force_mod:"):
        key = query.data.split(":", 1)[1]
        await query.answer()
        await query.message.edit_caption(_module_text(key), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="force_menu")]]), parse_mode="html") if getattr(query.message, "photo", None) else await query.message.edit_text(_module_text(key), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 FORCE COMMANDS", callback_data="force_menu")]]), parse_mode="html")
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
                    await query.message.edit_caption(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 RECORDINGS", callback_data="force_recordings")]]), parse_mode="html") if getattr(query.message, "photo", None) else await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 RECORDINGS", callback_data="force_recordings")]]), parse_mode="html")
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
        await query.message.edit_caption(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 RECORDINGS", callback_data="force_recordings")]]), parse_mode="html") if getattr(query.message, "photo", None) else await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 RECORDINGS", callback_data="force_recordings")]]), parse_mode="html")
        return
    if query.data == "force_recordings":
        await query.answer()
        text = "<blockquote><b>🎙️ VCFIGHT RECORDINGS</b>\n\nManage your saved recordings below.</blockquote>"
        await query.message.edit_caption(text, reply_markup=_recordings_keyboard(), parse_mode="html") if getattr(query.message, "photo", None) else await query.message.edit_text(text, reply_markup=_recordings_keyboard(), parse_mode="html")


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
        return await message.reply_text(_module_text(key), parse_mode="html")
    await message.reply_text(f"`{help_arg}` **Not a Valid Module Name.**")


def add_command_help(module_name, commands):
    command_dict = CMD_HELP.get(module_name, {})
    for item in commands:
        if not item:
            continue
        command_dict[item[0]] = item[1]
    CMD_HELP[module_name] = command_dict
