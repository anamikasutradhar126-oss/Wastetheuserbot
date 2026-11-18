from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from Waste import app
from Waste.modules.bot.premium import PE_HOST, PE_COMMAND, pe

MUST_JOIN1 = "wasteBotz"
MUST_JOIN2 = "wasteuserbotUpdates"

FORCE_CAPTION = "\n".join([
    f"{pe(PE_HOST)} <b>ＦＯＲＣＥ ＪＯＩＮ ＲＥＱＵＩＲＥＤ</b>",
    f"{pe(PE_HOST)} <b>ᴊᴏɪɴ ᴛʜᴇ sᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ</b>",
    f"{pe(PE_HOST)} <b>ᴊᴏɪɴ ᴛʜᴇ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ</b>",
    f"{pe(PE_HOST)} <b>ᴀғᴛᴇʀ ᴊᴏɪɴɪɴɢ ʙᴏᴛʜ, ᴛᴀᴘ ᴠᴇʀɪғɪᴇᴅ.</b>",
])


def force_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ＷＡＳＴＥ ＢＯＴＺ ↗", url=f"https://t.me/{MUST_JOIN1}")],
        [InlineKeyboardButton("ＷＡＳＴＥ ＵＰＤＡＴＥＳ ↗", url=f"https://t.me/{MUST_JOIN2}")],
        [InlineKeyboardButton("ＶＥＲＩＦＩＥＤ", callback_data="force_check")],
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
                parse_mode=enums.ParseMode.HTML,
                reply_markup=force_keyboard(),
            )
            await msg.stop_propagation()
        except ChatWriteForbidden:
            pass
    except ChatAdminRequired:
        print(f"Please promote me as admin in both {MUST_JOIN1} and {MUST_JOIN2}.")
    except Exception:
        pass


@app.on_callback_query(filters.regex("^force_check$"))
async def force_check(client, query):
    try:
        await client.get_chat_member(MUST_JOIN1, query.from_user.id)
        await client.get_chat_member(MUST_JOIN2, query.from_user.id)
        await query.answer("Verified", show_alert=True)
        await query.message.edit_caption(
            "\n".join([
                f"{pe(PE_HOST)} <b>ᴠᴇʀɪғɪᴇᴅ</b>",
                f"{pe(PE_COMMAND)} <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ＷＡＳＴＥ Ｘ ＵＢＯＴ.</b>",
            ]),
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ＨＥＬＰ", callback_data="force_help")]]),
        )
    except UserNotParticipant:
        await query.answer("Please join both channels first.", show_alert=True)
    except Exception as exc:
        await query.answer(type(exc).__name__, show_alert=True)
