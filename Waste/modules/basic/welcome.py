from pyrogram import Client, filters
from pyrogram.types import Message
from Waste.modules.bot.start import settings_col
from Waste.modules.help import add_command_help


def _uid(client):
    return int(getattr(client, "_waste_owner_uid", 0) or getattr(getattr(client, "me", None), "id", 0))

def _enabled(client):
    uid=_uid(client)
    if not uid: return False
    doc=settings_col.find_one({"_id": uid}) or {}
    return bool(doc.get("welcome_enabled", True))

@Client.on_message(filters.command("welcome", [".", "/"]) & filters.me)
async def welcome_toggle(client: Client, message: Message):
    uid=_uid(client)
    arg=(message.command[1].lower() if len(message.command)>1 else "status")
    if arg not in {"on","off","status"}:
        return await message.reply_text("<blockquote>Usage: <code>.welcome on</code> / <code>.welcome off</code></blockquote>", parse_mode="html")
    if arg=="status":
        state=_enabled(client)
        return await message.reply_text(f"<blockquote>🏠 Welcome: {'🟢 ON' if state else '🔴 OFF'}</blockquote>", parse_mode="html")
    state=arg=="on"
    settings_col.update_one({"_id": uid},{"$set":{"welcome_enabled":state}},upsert=True)
    await message.reply_text(f"<blockquote>{'🟢 Welcome enabled' if state else '🔴 Welcome disabled'}</blockquote>", parse_mode="html")

@Client.on_message(filters.new_chat_members)
async def welcome_new_member(client: Client, message: Message):
    if not _enabled(client): return
    for user in message.new_chat_members or []:
        if user.is_bot: continue
        name=user.first_name or user.username or "New Member"
        mention=user.mention(name)
        text=(f"<blockquote>👋 <b>Welcome {mention}!</b>\n\n"
              f"🎉 Glad to have you in <b>{message.chat.title or 'the group'}</b>.\n"
              f"✨ Enjoy your stay!</blockquote>")
        try:
            await message.reply_text(text, parse_mode="html", disable_web_page_preview=True)
        except Exception:
            pass

add_command_help("Welcome", [
    ["welcome", "Enable, disable or check the automatic new-member welcome."],
])
