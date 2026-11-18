from datetime import datetime, timezone
import random
from pyrogram import Client, filters
from Waste.modules.bot.start import subscriptions_col, OWNER_USERNAME
from Waste.modules.help import add_command_help

# Exact MMAR/OMAR pool requested by the user.
_DEFAULT_POOL = ["😂", "😭", "😑", "🤣", "💔", "🖕", "🍌"]
_ALLOWED = set(_DEFAULT_POOL) | {"👀", "🔥", "😐"}


def _active(uid):
    try:
        doc = subscriptions_col.find_one({"_id": int(uid)})
    except Exception:
        return False
    if not doc:
        return False
    expires = doc.get("expires_at")
    if isinstance(expires, datetime):
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires > datetime.now(timezone.utc):
            return True
        try:
            subscriptions_col.delete_one({"_id": int(uid)})
        except Exception:
            pass
    return False


def _uid(client):
    return getattr(client, "_waste_owner_uid", None) or getattr(
        getattr(client, "me", None), "id", None
    )


def _parse_emojis(raw):
    return [ch for ch in raw if ch in _ALLOWED]


async def _react(message, emoji):
    """React using the high-level API first, then Telegram's raw SendReaction API."""
    try:
        await message.react(emoji)
        return True
    except Exception:
        pass
    try:
        from pyrogram.raw.functions.messages import SendReaction
        from pyrogram.raw.types import ReactionEmoji
        client = message._client
        peer = await client.resolve_peer(message.chat.id)
        await client.invoke(SendReaction(peer=peer, msg_id=message.id, reaction=[ReactionEmoji(emoticon=emoji)]))
        return True
    except Exception:
        return False


# ------------------------- PREMIUM AUTOREACT -------------------------
@Client.on_message(filters.command("autoreact", [".", "/"]) & filters.me)
async def autoreact_command(client, message):
    uid = _uid(client)
    if not uid or not _active(uid):
        return await message.reply(
            "💎 **Subscription Required**\n\nContact owner: @" + OWNER_USERNAME
        )

    args = message.command[1:]
    enabled = bool(getattr(client, "_auto_react_enabled", False))
    emoji = getattr(client, "_auto_react_emoji", "random")

    if not args or args[0].lower() == "status":
        return await message.reply(
            f"⚡ **Auto Reaction:** {'ON' if enabled else 'OFF'}\nReaction: {emoji}"
        )

    action = args[0].lower()
    if action == "off":
        client._auto_react_enabled = False
        return await message.reply("⚡ **Auto Reaction disabled.**")

    if action == "on":
        chosen = args[1] if len(args) > 1 else "random"
        if chosen != "random" and chosen not in _ALLOWED:
            return await message.reply(
                "❌ Allowed: " + " ".join(_DEFAULT_POOL)
                + "\nUse `.autoreact on random` for random reactions."
            )
        client._auto_react_enabled = True
        client._auto_react_emoji = chosen
        return await message.reply(
            f"⚡ **Auto Reaction enabled:** "
            f"{'random pool' if chosen == 'random' else chosen}"
        )

    return await message.reply(
        "Usage: `.autoreact on random`, `.autoreact on 😂`, "
        "`.autoreact off`, `.autoreact status`"
    )


@Client.on_message((filters.group | filters.channel) & filters.incoming & ~filters.bot & ~filters.service)
async def auto_react_watcher(client, message):
    if not getattr(client, "_auto_react_enabled", False):
        return
    if getattr(message, "outgoing", False):
        return

    emoji = getattr(client, "_auto_react_emoji", "random")
    await _react(
        message,
        random.choice(_DEFAULT_POOL) if emoji == "random" else emoji
    )


# ------------------------- MMAR: MY MESSAGE AUTO REACT -------------------------
@Client.on_message(filters.command("mmar", [".", "/"]) & filters.me)
async def mmar_command(client, message):
    args = message.command[1:] if len(message.command) > 1 else []
    action = args[0].lower() if args else "status"

    if action == "off":
        client._mmar_enabled = False
        return await message.reply("🛑 **MMAR OFF**")

    if action == "on":
        # `.mmar on 😂😭😑🤣💔🖕🍌`
        # If no pool is supplied, use exactly the requested default pool.
        raw = "".join(args[1:]) if len(args) > 1 else ""
        pool = _parse_emojis(raw) or list(_DEFAULT_POOL)
        client._mmar_pool = pool
        client._mmar_enabled = True
        return await message.reply("🟢 **MMAR ON**\nPool: " + " ".join(pool))

    return await message.reply(
        f"😂 **MMAR:** {'🟢 ON' if getattr(client, '_mmar_enabled', False) else '🔴 OFF'}\n"
        f"Pool: {' '.join(getattr(client, '_mmar_pool', _DEFAULT_POOL))}"
    )


@Client.on_message((filters.group | filters.channel) & filters.me & ~filters.service)
async def mmar_watcher(client, message):
    """
    React only to the owner's own outgoing messages.
    The command message itself is ignored so `.mmar on ...` does not get
    reacted to.
    """
    if not getattr(client, "_mmar_enabled", False):
        return

    text = message.text or message.caption or ""
    command = text.strip().split(maxsplit=1)[0].lower() if text.strip() else ""
    if command in (".mmar", "/mmar"):
        return

    pool = getattr(client, "_mmar_pool", _DEFAULT_POOL)
    await _react(message, random.choice(pool))


# ------------------------- OMAR: OTHER USER AUTO REACT -------------------------
def _target_id_from_command(client, message, args):
    # Reply target has priority.
    reply = message.reply_to_message
    if reply and reply.from_user:
        return int(reply.from_user.id)

    if len(args) < 2:
        return None

    raw = args[1].strip().lstrip("@")
    if raw.isdigit():
        return int(raw)

    # Resolve @username / username through Telegram.
    return raw


@Client.on_message(filters.command("omar", [".", "/"]) & filters.me)
async def omar_command(client, message):
    args = message.command[1:] if len(message.command) > 1 else []
    action = args[0].lower() if args else "status"

    if action == "off":
        client._omar_enabled = False
        client._omar_target = None
        return await message.reply("🛑 **OMAR OFF**")

    if action == "on":
        target = _target_id_from_command(client, message, args)
        if target is None:
            return await message.reply(
                "Usage: `.omar on @username` / `.omar on <user_id>` "
                "or reply to that user's message."
            )

        if isinstance(target, str):
            try:
                user = await client.get_users(target)
                target = int(user.id)
            except Exception:
                return await message.reply("❌ Username/User ID not found.")

        client._omar_target = int(target)
        client._omar_enabled = True
        return await message.reply(f"🟢 **OMAR ON**\nTarget: `{int(target)}`")

    return await message.reply(
        f"🎯 **OMAR:** {'🟢 ON' if getattr(client, '_omar_enabled', False) else '🔴 OFF'}\n"
        f"Target: `{getattr(client, '_omar_target', None)}`"
    )


@Client.on_message((filters.group | filters.channel) & filters.incoming & ~filters.bot & ~filters.service)
async def omar_watcher(client, message):
    if not getattr(client, "_omar_enabled", False):
        return
    if getattr(message, "outgoing", False):
        return

    target = getattr(client, "_omar_target", None)
    sender = getattr(message, "from_user", None)
    if not target or not sender:
        return

    if int(sender.id) != int(target):
        return

    pool = getattr(client, "_mmar_pool", _DEFAULT_POOL)
    await _react(message, random.choice(pool))


add_command_help("ReactionPlus", [
    ["mmar on 😂😭😑🤣💔🖕🍌", "React to your own messages with the selected emoji pool."],
    ["mmar off", "Disable reactions on your own messages."],
    ["omar on @username", "Target a user and react to their messages."],
    ["omar on <user_id>", "Target a user by ID and react to their messages."],
    ["omar on (reply)", "Reply to a user's message and enable reactions for that user."],
    ["omar off", "Disable target-user reactions."],
])

add_command_help("Promotion", [
    ["autoreact on random", "Premium auto-react for incoming group/channel messages."],
    ["autoreact on 😂", "Premium auto-react with a chosen emoji."],
    ["autoreact off", "Disable incoming auto-reactions."],
    ["autoreact status", "Show auto-reaction status."],
])
