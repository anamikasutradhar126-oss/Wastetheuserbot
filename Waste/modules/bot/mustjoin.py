from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from Waste import app

MUST_JOIN1 = "wasteBotz"
MUST_JOIN2 = "wasteuserbotUpdates"

FORCE_CAPTION = (
    "<blockquote>🔒 <b>FORCE JOIN REQUIRED</b>\n\n"
    "🔴 Join the Support channel\n"
    "🔵 Join the Update channel\n\n"
    "After joining both, tap <b>I Have Joined ✅</b>.</blockquote>"
)


def force_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 WASTE BOTZ", url=f"https://t.me/{MUST_JOIN1}")],
        [InlineKeyboardButton("🔵 WASTE UPDATES", url=f"https://t.me/{MUST_JOIN2}")],
        [InlineKeyboardButton("✅ I HAVE JOINED", callback_data="force_check")],
    ])

@app.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(client: Client, msg):
    if not msg.from_user or msg.from_user.is_bot:
        return
    try:
        await client.get_chat_member(MUST_JOIN1, msg.from_user.id)
        await client.get_chat_member(MUST_JOIN2, msg.from_user.id)
    except UserNotParticipant:
        try:
            await msg.reply_photo(
                photo="https://kommodo.ai/i/Jfqgjb0eSsMXylBiUn3c",
                caption=FORCE_CAPTION,
                reply_markup=force_keyboard(),
            )
            await msg.stop_propagation()
        except ChatWriteForbidden:
            pass
    except ChatAdminRequired:
        print(f"⚠️ Please promote me as admin in both {MUST_JOIN1} and {MUST_JOIN2}!")
    except Exception:
        pass

@app.on_callback_query(filters.regex("^force_check$"))
async def force_check(client: Client, query):
    try:
        await client.get_chat_member(MUST_JOIN1, query.from_user.id)
        await client.get_chat_member(MUST_JOIN2, query.from_user.id)
        await query.answer("🟢 Verified!", show_alert=True)
        await query.message.edit_caption(
            "<blockquote>✅ <b>VERIFIED</b>\n\n"
            "Welcome to Waste Userbot. Tap <b>HELP 📚</b> to view the available commands.</blockquote>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 HELP", callback_data="force_help")]]),
        )
    except UserNotParticipant:
        await query.answer("🔴 Please join both channels first.", show_alert=True)
    except Exception as exc:
        await query.answer(f"⚠️ {type(exc).__name__}", show_alert=True)

@app.on_callback_query(filters.regex("^force_help$"))
async def force_help(client: Client, query):
    from Waste.modules.bot.help_ui import help_markup, HELP_TEXT
    await query.answer()
    await query.message.edit_caption(HELP_TEXT, reply_markup=help_markup())
