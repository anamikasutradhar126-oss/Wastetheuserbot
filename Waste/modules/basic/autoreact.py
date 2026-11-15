from datetime import datetime, timezone
import random
from pyrogram import Client, filters
from Waste.modules.bot.start import subscriptions_col, OWNER_USERNAME
from Waste.modules.help import add_command_help

_ALLOWED = {"😂", "😭", "😑", "🤣", "💔", "🖕", "🍌", "👀", "🔥", "😐"}
_DEFAULT_POOL = ["😂", "😭", "😑", "🤣", "💔", "🖕", "🍌"]


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
    return getattr(client, "_waste_owner_uid", None) or getattr(getattr(client, "me", None), "id", None)


def _parse_emojis(raw):
    chars = [x for x in raw if x.strip()]
    return [x for x in chars if x in _ALLOWED]


@Client.on_message(filters.command("autoreact", [".", "/"]) & filters.me)
async def autoreact_command(client, message):
    uid = _uid(client)
    if not uid or not _active(uid):
        return await message.reply("💎 **Subscription Required**\n\nContact owner: @" + OWNER_USERNAME)
    args = message.command[1:]
    enabled = bool(getattr(client, "_auto_react_enabled", False))
    emoji = getattr(client, "_auto_react_emoji", "random")
    if not args or args[0].lower() == "status":
        return await message.reply(f"⚡ **Auto Reaction:** {'ON' if enabled else 'OFF'}\nReaction: {emoji}")
    action = args[0].lower()
    if action == "off":
        client._auto_react_enabled = False
        return await message.reply("⚡ **Auto Reaction disabled.**")
    if action == "on":
        chosen = args[1] if len(args) > 1 else "random"
        if chosen != "random" and chosen not in _ALLOWED:
            return await message.reply("❌ Allowed: " + " ".join(_DEFAULT_POOL) + "\nUse `.autoreact on random` for random reactions.")
        client._auto_react_enabled = True
        client._auto_react_emoji = chosen
        return await message.reply(f"⚡ **Auto Reaction enabled:** {'random pool' if chosen == 'random' else chosen}")
    return await message.reply("Usage: `.autoreact on random`, `.autoreact on 😂`, `.autoreact off`, `.autoreact status`")


@Client.on_message((filters.group | filters.channel) & ~filters.bot)
async def auto_react_watcher(client, message):
    if not getattr(client, "_auto_react_enabled", False):
        return
    # Keep this feature on incoming messages only; .mmar handles outgoing ones.
    if getattr(message, "outgoing", False):
        return
    emoji = getattr(client, "_auto_react_emoji", "random")
    try:
        await message.react(random.choice(_DEFAULT_POOL) if emoji == "random" else emoji)
    except Exception:
        pass


# ------------------------- MY-MESSAGE REACTOR -------------------------
@Client.on_message(filters.command("mmar", [".", "/"]) & filters.me)
async def mmar_command(client, message):
    args = message.command[1:] if len(message.command) > 1 else []
    action = args[0].lower() if args else "status"
    if action == "off":
        client._mmar_enabled = False
        return await message.reply("🛑 **MMAR OFF**")
    if action == "on":
        pool = _parse_emojis("".join(args[1:])) if len(args) > 1 else list(_DEFAULT_POOL)
        if not pool:
            pool = list(_DEFAULT_POOL)
        client._mmar_enabled = True
        client._mmar_pool = pool
        return await message.reply("🟢 **MMAR ON**\nPool: " + " ".join(pool))
    return await message.reply(f"😂 **MMAR:** {'🟢 ON' if getattr(client, '_mmar_enabled', False) else '🔴 OFF'}\nPool: {' '.join(getattr(client, '_mmar_pool', _DEFAULT_POOL))}")


@Client.on_message((filters.group | filters.channel) & filters.me)
async def mmar_watcher(client, message):
    if not getattr(client, "_mmar_enabled", False):
        return
    # Don't react to the command message itself.
    text = message.text or message.caption or ""
    if text.startswith((".mmar", "/mmar")):
        return
    try:
        await message.react(random.choice(getattr(client, "_mmar_pool", _DEFAULT_POOL)))
    except Exception:
        pass


# ------------------------- OTHER-MESSAGE REACTOR -------------------------
def _target_id(message):
    reply = message.reply_to_message
    if reply and reply.from_user:
        return int(reply.from_user.id)
    return None


@Client.on_message(filters.command("omar", [".", "/"]) & filters.me)
async def omar_command(client, message):
    args = message.command[1:] if len(message.command) > 1 else []
    action = args[0].lower() if args else "status"
    if action == "off":
        client._omar_enabled = False
        client._omar_target = None
        return await message.reply("🛑 **OMAR OFF**")
    if action == "on":
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
                    return await message.reply("❌ Username/User ID not found.")
        if target is None:
            return await message.reply("Usage: `.omar on @username` / `.omar on <user_id>` or reply to that user's message.")
        client._omar_enabled = True
        client._omar_target = target
        return await message.reply(f"🟢 **OMAR ON**\nTarget: `{target}`")
    return await message.reply(f"🎯 **OMAR:** {'🟢 ON' if getattr(client, '_omar_enabled', False) else '🔴 OFF'}\nTarget: `{getattr(client, '_omar_target', None)}`")


@Client.on_message((filters.group | filters.channel) & ~filters.bot)
async def omar_watcher(client, message):
    if not getattr(client, "_omar_enabled", False) or getattr(message, "outgoing", False):
        return
    target = getattr(client, "_omar_target", None)
    if not target or not message.from_user or int(message.from_user.id) != int(target):
        return
    try:
        await message.react(random.choice(getattr(client, "_mmar_pool", _DEFAULT_POOL)))
    except Exception:
        pass


add_command_help("ReactionPlus", [
    ["mmar on 😂😭😑🤣💔🖕🍌", "React to your own messages with the selected emoji pool."],
    ["mmar off", "Disable reactions on your own messages."],
    ["omar on @username", "React to messages from a selected user."],
    ["omar on <user_id>", "React to messages from a selected user ID."],
    ["omar off", "Disable target-user reactions."],
])

add_command_help("Promotion", [
    ["autoreact on random", "Premium auto-react for incoming group/channel messages."],
    ["autoreact on 😂", "Premium auto-react with a chosen emoji."],
    ["autoreact off", "Disable incoming auto-reactions."],
    ["autoreact status", "Show auto-reaction status."],
])
