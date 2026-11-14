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
    explicit_norm = {str(x).strip().lower().replace("_", "-") for x in explicit}
    extra = [k for k in CMD_HELP.keys() if str(k).strip().lower().replace("_", "-") not in explicit_norm]
    keys = list(dict.fromkeys(explicit + extra))
    keys = [k for k in keys if str(k).strip().lower() not in {"music", "vcfight", "autotextpromo", "promotion", "ai chat"}]
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


def _normalise_help_name(value: str) -> str:
    return " ".join((value or "").strip().lower().replace("_", "-").split())


def _find_help_key(name: str):
    """Resolve a displayed module name, alias, or command name to CMD_HELP.

    Resolution is case-insensitive and also matches keys such as ``AI Chat``
    when the user types ``aichat``. This prevents false ``Not a Valid Module``
    errors for modules whose registered help name contains spaces/capitalisation.
    """
    raw = (name or "").strip()
    norm = _normalise_help_name(raw)
    compact = norm.replace(" ", "").replace("-", "")

    aliases = {
        "music": "Music", "song": "Music", "play": "Music",
        "vcfight": "VcFight", "vc-fight": "VcFight", "recordings": "VcFight", "recording": "VcFight",
        "autotextpromo": "Promotion", "autotext-promo": "Promotion", "autotext": "Promotion",
        "aichat": "AI Chat", "ai-chat": "AI Chat", "ai chat": "AI Chat",
        "promotion": "Promotion", "welcome": "Welcome",
        "anime-cf": "anime_cf", "truthdare": "truth-dare",
        "quotly": "quotly", "dictionary": "dictionary",
    }
    target = aliases.get(norm, raw)
    target_norm = _normalise_help_name(target)
    target_compact = target_norm.replace(" ", "").replace("-", "")

    # Exact/canonical match first.
    for key in CMD_HELP:
        k_norm = _normalise_help_name(str(key))
        k_compact = k_norm.replace(" ", "").replace("-", "")
        if k_norm == target_norm or k_compact == target_compact or k_norm == norm or k_compact == compact:
            return key

    # Display-only modules which don't have their own CMD_HELP registration.
    display_aliases = {
        "autotextpromo": "Promotion",
        "music": "Music",
        "vcfight": "VcFight",
    }
    return display_aliases.get(norm)


def _module_text(key):
    """Build a real command-details page from the registered CMD_HELP data."""
    resolved = _find_help_key(str(key)) or key
    commands = CMD_HELP.get(resolved, {})

    # Case-insensitive fallback in case the module was registered under a
    # slightly different spelling/capitalisation.
    if not commands:
        wanted = _normalise_help_name(str(resolved))
        for registered_key, registered_commands in CMD_HELP.items():
            if _normalise_help_name(str(registered_key)) == wanted:
                commands = registered_commands
                resolved = registered_key
                break

    # These are display-only entries in the requested Force Commands menu.
    # They still receive useful usage instructions instead of an invalid-module
    # response.
    if not commands:
        display_commands = {
            "autotextpromo": {
                "autotextpromo on": "Enable AutoTextPromo.",
                "autotextpromo off": "Disable AutoTextPromo.",
                "autotextpromo status": "Show AutoTextPromo status/settings.",
            },
            "music": {
                "play <song name>": "Connected ID only: search and play the song in the current group's Voice Chat.",
                "song <song name>": "Connected ID only: search and play the song in the current group's Voice Chat.",
                "vplay <song name>": "Connected ID only: play audio in the current group's Voice Chat.",
            },
            "vcfight": {
                "vcfight": "Start VC Fight.",
                "vcstop": "Stop VC Fight.",
                "vcjoin": "Join the current Voice Chat.",
                "vcleave": "Leave the current Voice Chat.",
                "vcall": "Call members in the VC workflow.",
                "vcmute": "Mute in VC.",
                "vcunmute": "Unmute in VC.",
                "vclogs": "View VC logs.",
                "addrc": "Save a replied audio/voice recording.",
                "removerc": "Remove a saved recording.",
                "myrc": "List saved recordings.",
                "rcinfo": "Show saved recording information.",
                "bass 100-500": "Boost the latest saved recording using a value from 100 to 500.",
            },
        }
        commands = display_commands.get(_normalise_help_name(str(key)), {})

    if not commands:
        commands = {str(key): "Commands and settings for this module. Use the command shown above with your connected ID."}

    title = str(resolved or key).upper()
    lines = [f"<blockquote><b>❖ {title} COMMANDS</b></blockquote>"]
    for command, desc in commands.items():
        command = str(command).strip()
        # Registered help entries are already the real command syntax. Add
        # both prefixes only for plain command names; don't duplicate them
        # when an entry already contains arguments or a prefix.
        if command.startswith((".", "/")):
            usage = command
        else:
            usage = f".{command}"
        alt = usage[1:] if usage.startswith(".") else usage
        if not alt.startswith("/"):
            alt = f"/{alt}"
        lines.append(
            f"<blockquote>• <code>{usage}</code>  |  <code>{alt}</code>\n"
            f"  {str(desc)}</blockquote>"
        )
    lines.append("<blockquote>💡 Use the command exactly as shown. Arguments such as <code>&lt;group_id&gt;</code> or <code>&lt;text&gt;</code> are replaced with your value.</blockquote>")
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
