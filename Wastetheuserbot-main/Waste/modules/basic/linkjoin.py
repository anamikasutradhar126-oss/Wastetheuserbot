"""Scan a source Telegram chat for group/channel links and join eligible chats.
Processes the source's accessible history, deduplicates links, and respects Telegram FloodWait.
"""
import asyncio
import re
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserAlreadyParticipant
from Waste.modules.help import add_command_help

URL_RE = re.compile(r"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/(?:\+([A-Za-z0-9_-]{8,})|joinchat/([A-Za-z0-9_-]{8,})|([A-Za-z0-9_]{5,}))/?", re.I)
SKIP_NAMES = {"joinchat", "c", "s", "addstickers", "share", "proxy", "iv", "boost"}
DELAY_BETWEEN_JOINS = 3


def _extract_links(message):
    texts = [message.text or "", message.caption or ""]
    # Include URLs hidden behind clickable text entities.
    for entities in (getattr(message, "entities", None), getattr(message, "caption_entities", None)):
        for entity in entities or []:
            url = getattr(entity, "url", None)
            if url:
                texts.append(url)
    found = []
    for text in texts:
        for m in URL_RE.finditer(text):
            if m.group(1):
                link = "https://t.me/+" + m.group(1)
            elif m.group(2):
                link = "https://t.me/joinchat/" + m.group(2)
            else:
                username = m.group(3)
                if username.lower() in SKIP_NAMES:
                    continue
                link = "https://t.me/" + username
            if link not in found:
                found.append(link)
    return found


async def _source_chat(client, message, arg):
    if arg:
        return await client.get_chat(arg.strip())
    if message.chat and message.chat.type in (enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP):
        return message.chat
    if message.reply_to_message:
        return message.reply_to_message.chat
    raise ValueError("Source channel/group link do ya command ko usi channel mein chalao.")


async def _run_join(client, message, kind):
    source_arg = " ".join(message.command[2:]).strip()
    status = await message.reply_text("🔎 Source ke accessible messages scan kar raha hoon…")
    joined, skipped, errors = [], [], []
    try:
        source = await _source_chat(client, message, source_arg)
        links, seen = [], set()
        # limit=0 means iterate all history available to this account.
        async for item in client.get_chat_history(source.id, limit=0):
            for link in _extract_links(item):
                if link not in seen:
                    seen.add(link)
                    links.append(link)
        if not links:
            await status.edit("⚠️ Accessible message history mein Telegram group/channel links nahi mile.")
            return
        await status.edit(f"🔗 {len(links)} unique links mile. Eligible {kind}s join kar raha hoon; Telegram limits apply hongi…")
        for index, link in enumerate(links, 1):
            try:
                invite = bool(re.search(r"t\.me/(?:\+|joinchat/)", link, re.I))
                if invite:
                    # Resolve invite preview first, so we don't join a chat of the wrong type.
                    invite_hash = link.rsplit("/", 1)[-1].lstrip("+")
                    preview = await client.check_chat_invite(invite_hash)
                    target = getattr(preview, "chat", None)
                    target_type = getattr(target, "type", None)
                    if target_type is None:
                        skipped.append(f"{link} (type not visible in invite preview)")
                        continue
                    is_group = target_type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP)
                    is_channel = target_type == enums.ChatType.CHANNEL
                    if (kind == "group" and not is_group) or (kind == "channel" and not is_channel):
                        skipped.append(f"{link} (not a {kind})")
                        continue
                    await client.join_chat(link)
                    joined.append(link)
                else:
                    username = link.rstrip("/").split("/")[-1]
                    target = await client.get_chat(username)
                    is_group = target.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP)
                    is_channel = target.type == enums.ChatType.CHANNEL
                    if (kind == "group" and not is_group) or (kind == "channel" and not is_channel):
                        skipped.append(f"{link} (not a {kind})")
                        continue
                    await client.join_chat(username)
                    joined.append(link)
            except UserAlreadyParticipant:
                skipped.append(f"{link} (already joined)")
            except FloodWait as exc:
                await status.edit(
                    f"⏳ Telegram ne flood-wait {exc.value}s lagaya, isliye safely ruk gaya.\n"
                    f"Processed: {index-1}/{len(links)} | Joined: {len(joined)} | Skipped: {len(skipped)} | Failed: {len(errors)}\n"
                    "Command baad mein dobara chala kar baaki links process kar sakte ho."
                )
                return
            except Exception as exc:
                errors.append(f"{link} ({type(exc).__name__})")
            if index % 10 == 0:
                try:
                    await status.edit(f"⏳ Progress: {index}/{len(links)} | Joined: {len(joined)} | Skipped: {len(skipped)} | Failed: {len(errors)}")
                except Exception:
                    pass
            await asyncio.sleep(DELAY_BETWEEN_JOINS)
        lines = [f"✅ Scan complete: {source.title or source.username or source.id}", f"Total unique links: {len(links)}", f"Joined successfully: {len(joined)}", f"Already joined/wrong type: {len(skipped)}", f"Failed: {len(errors)}"]
        if errors:
            lines.append("\nFailed links (first 15):\n" + "\n".join(errors[:15]))
        await status.edit("\n".join(lines))
    except Exception as exc:
        await status.edit(f"❌ {type(exc).__name__}: {str(exc)[:250]}\nUsage: `.all{kind} join <source_channel_link>`")


@Client.on_message(filters.command(["allgroup"], [".", "/"]) & filters.me)
async def allgroup_join(client, message):
    if len(message.command) < 2 or message.command[1].lower() != "join":
        return await message.reply_text("Usage: `.allgroup join <source_channel_link>` (or run inside the source chat)")
    await _run_join(client, message, "group")


@Client.on_message(filters.command(["allchannel"], [".", "/"]) & filters.me)
async def allchannel_join(client, message):
    if len(message.command) < 2 or message.command[1].lower() != "join":
        return await message.reply_text("Usage: `.allchannel join <source_channel_link>` (or run inside the source chat)")
    await _run_join(client, message, "channel")


# Also show these commands under `.help promotion`, as requested.
add_command_help("promotion", [
    ["allgroup join <channel_link>", "Scan all accessible source messages and join eligible linked groups, with Telegram rate limits."],
    ["allchannel join <channel_link>", "Scan all accessible source messages and join eligible linked channels, with Telegram rate limits."],
])
add_command_help("linkjoin", [
    ["allgroup", "Join eligible linked groups from a source chat: .allgroup join <channel_link>"],
    ["allchannel", "Join eligible linked channels from a source chat: .allchannel join <channel_link>"],
])
