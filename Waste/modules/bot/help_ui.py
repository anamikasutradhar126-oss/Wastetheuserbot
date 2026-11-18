from html import escape

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Waste import app, CMD_HELP
from Waste.modules.bot.premium import PE_COMMAND, PE_PAGE, PE_MAIN, PE_NEXT, pe, serendipity

FORCE_TITLE = f"{pe(PE_COMMAND)} <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ꜰᴏʀᴄᴇ ᴄᴏᴍᴍᴀɴᴅs</b>"
PAGE_SIZE = 11


def _command_names():
    names = []
    for module, commands in CMD_HELP.items():
        for command in commands:
            if command not in names:
                names.append(command)
    return sorted(names, key=str.lower)


def _page_count():
    names = _command_names()
    return max(1, (len(names) + PAGE_SIZE - 1) // PAGE_SIZE)


def _page_text(page: int) -> str:
    names = _command_names()
    total = _page_count()
    page = max(0, min(page, total - 1))
    start = page * PAGE_SIZE
    current = names[start:start + PAGE_SIZE]
    rows = [FORCE_TITLE]
    rows.extend(f"{pe(PE_COMMAND)} <b>{escape(serendipity(name))}</b>" for name in current)
    rows.append("")
    rows.append(f"{pe(PE_PAGE)} <b>ᴘᴀɢᴇ {page + 1}/{total}</b>")
    if page + 1 < total:
        rows.append(f"{pe(PE_NEXT)} <b>ɴᴇxᴛ</b>")
    else:
        rows.append(f"{pe(PE_MAIN)} <b>ᴍᴀɪɴ ᴍᴇɴᴜ</b>")
    return "\n".join(rows)


def _markup(page: int) -> InlineKeyboardMarkup:
    total = _page_count()
    rows = []
    if page > 0:
        rows.append([InlineKeyboardButton("Ｐʀᴇᴠ", callback_data=f"force_page:{page - 1}"), InlineKeyboardButton("ＮＥＸＴ", callback_data=f"force_page:{page + 1}")])
    elif total > 1:
        rows.append([InlineKeyboardButton("Ｐᴀɢᴇ 1/" + str(total), callback_data="force_page:0"), InlineKeyboardButton("ＮＥＸＴ", callback_data="force_page:1")])
    else:
        rows.append([InlineKeyboardButton("Ｐᴀɢᴇ 1/1", callback_data="force_page:0")])
    rows.append([InlineKeyboardButton("ＭＡＩＮ ＭＥＮＵ", callback_data="home")])
    return InlineKeyboardMarkup(rows)


HELP_TEXT = "\n".join([
    f"{pe(PE_MAIN)} <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ꜰᴏʀᴄᴇ ᴄᴏᴍᴍᴀɴᴅs</b>",
    f"{pe(PE_COMMAND)} <b>ᴛᴀᴘ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ᴛᴏ ᴠɪᴇᴡ ᴄᴏᴍᴍᴀɴᴅs.</b>",
])


@app.on_callback_query(filters.regex(r"^force_help$"))
async def force_help(client, query):
    await query.answer()
    await query.message.edit_caption(
        _page_text(0),
        parse_mode=enums.ParseMode.HTML,
        reply_markup=_markup(0),
    )


@app.on_callback_query(filters.regex(r"^force_page:(\d+)$"))
async def force_page(client, query):
    await query.answer()
    page = int(query.matches[0].group(1))
    await query.message.edit_caption(
        _page_text(page),
        parse_mode=enums.ParseMode.HTML,
        reply_markup=_markup(page),
    )
