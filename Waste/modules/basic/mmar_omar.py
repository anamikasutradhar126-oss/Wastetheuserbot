import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from Waste.modules.help import add_command_help

log = logging.getLogger(__name__)
DEFAULT_EMOJIS = ["😂", "😭", "😑", "🤣", "💔", "🖕", "🍌"]


def _target_map(client):
    value = getattr(client, "_omar_targets", None)
    if not isinstance(value, set):
        value = set()
        setattr(client, "_omar_targets", value)
    return value


def _react_emoji():
    return random.choice(DEFAULT_EMOJIS)


async def _react(message: Message):
    """Use Telegram's normal reaction API; it is much more reliable than
    sending a custom-emoji document id as a reaction on older Pyrogram builds."""
    try:
        await message.react(_react_emoji())
        return True
    except Exception as exc:
        log.debug("Reaction failed for %s: %s", getattr(message, "id", "?"), type(exc).__name__)
        return False


@Client.on_message(filters.command("mmar", [".", "/"]) & (filters.incoming | filters.me))
async def mmar_command(client, message: Message):
    args = [x.lower() for x in message.command[1:]]
    if not args or args[0] not in {"on", "off", "status"}:
        return await message.reply("Usage: `.mmar on` / `.mmar off` / `.mmar status`")
    if args[0] == "on":
        client._mmar_enabled = True
        return await message.reply("😂 **MMAR ON**\nYour own messages will be auto-reacted.")
    if args[0] == "off":
        client._mmar_enabled = False
        return await message.reply("🔴 **MMAR OFF**")
    return await message.reply(f"MMAR: {'ON' if getattr(client, '_mmar_enabled', False) else 'OFF'}")


@Client.on_message(filters.command("omar", [".", "/"]) & (filters.incoming | filters.me))
async def omar_command(client, message: Message):
    args = message.command[1:]
    if not args or args[0].lower() not in {"on", "off", "status"}:
        return await message.reply(
            "Usage: `.omar on @username`, `.omar on <userid>`, `.omar off`, "
            "or reply to a message with `.omar on`"
        )

    action = args[0].lower()
    targets = _target_map(client)
    if action == "off":
        targets.clear()
        return await message.reply("🔴 **OMAR OFF**")
    if action == "status":
        return await message.reply(
            f"OMAR targets: {', '.join(map(str, targets)) if targets else 'none'}"
        )

    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = int(message.reply_to_message.from_user.id)
    elif len(args) > 1:
        raw = args[1].lstrip("@")
        try:
            target = int(raw)
        except ValueError:
            try:
                user = await client.get_users(raw)
                target = int(user.id)
            except Exception:
                return await message.reply(
                    "❌ User not found. Use a username/user ID or reply to their message."
                )
    else:
        return await message.reply(
            "❌ Give a username/user ID or reply to the target user's message."
        )

    targets.add(target)
    return await message.reply(f"😂 **OMAR ON**\nTarget: `{target}`")


@Client.on_message(filters.group & (filters.incoming | filters.me))
async def mmar_outgoing_watcher(client, message: Message):
    if not getattr(client, "_mmar_enabled", False):
        return
    text = (message.text or message.caption or "").lstrip()
    if text.startswith((".mmar", "/mmar", ".omar", "/omar")):
        return
    await _react(message)


@Client.on_message(filters.incoming & filters.group & ~filters.bot)
async def omar_incoming_watcher(client, message: Message):
    user = message.from_user
    if not user or user.is_bot:
        return
    if int(user.id) not in _target_map(client):
        return
    await _react(message)


add_command_help("Reactions", [
    ["mmar on/off", "Auto-react your own group messages with 😂😭😑🤣💔🖕🍌."],
    ["omar on <username/userid>", "Auto-react a selected user's messages."],
    ["omar on (reply)", "Reply to a user's message and enable reactions for that user."],
    ["omar off", "Disable target-user reactions and clear the target list."],
    ["omar status", "Show active OMAR target IDs."],
])
