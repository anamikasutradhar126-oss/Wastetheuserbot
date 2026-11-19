from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Waste import app

PE_LINE = 5471952986970267163

def pe(eid=PE_LINE, fallback="✦"):
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'

def stylize(text):
    mapping = str.maketrans({
        'a':'𝙖','b':'𝙗','c':'𝙘','d':'𝙙','e':'𝙚','f':'𝙛','g':'𝙜','h':'𝙝','i':'𝙞','j':'𝙟','k':'𝙠','l':'𝙡','m':'𝙢',
        'n':'𝙣','o':'𝙤','p':'𝙥','q':'𝙦','r':'𝙧','s':'𝙨','t':'𝙩','u':'𝙪','v':'𝙫','w':'𝙬','x':'𝙭','y':'𝙮','z':'𝙯'
    })
    return str(text).lower().translate(mapping)

HELP_TEXT = f"""<blockquote>{pe()} <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ʜᴇʟᴘ ᴍᴇɴᴜ</b>\n\n{pe()} <b>𝙘𝙝𝙤𝙤𝙨𝙚 𝙖 𝙘𝙖𝙩𝙚𝙜𝙤𝙧𝙮 𝙗𝙚𝙡𝙤𝙬.</b>\n{pe()} <b>𝙘𝙤𝙢𝙢𝙖𝙣𝙙𝙨 𝙖𝙣𝙙 𝙚𝙭𝙞𝙨𝙩𝙞𝙣𝙜 𝙛𝙚𝙖𝙩𝙪𝙧𝙚𝙨 𝙧𝙚𝙢𝙖𝙞𝙣 𝙪𝙣𝙘𝙝𝙖𝙣𝙜𝙚𝙙.</b></blockquote>"""

CATEGORIES = [
    (stylize("music"), "music"), (stylize("vcfight"), "vcfight"),
    (stylize("welcome"), "welcome"), (stylize("ai chat"), "aichat"),
    (stylize("tools"), "tools"), (stylize("fun"), "fun"),
    (stylize("promotion"), "promotion"), (stylize("info"), "info"),
]

COMMANDS = {
    "music": f"<blockquote>{pe()} <b>𝙢𝙪𝙨𝙞𝙘</b>\n\n{pe()} <b>/play song name</b>\n{pe()} <b>.play song name</b>\n\n{pe()} <b>𝙥𝙡𝙖𝙮 𝙩𝙝𝙚 𝙧𝙚𝙦𝙪𝙚𝙨𝙩𝙚𝙙 𝙨𝙤𝙣𝙜 𝙞𝙣 𝙩𝙝𝙚 𝙘𝙤𝙣𝙣𝙚𝙘𝙩𝙚𝙙 𝙖𝙘𝙘𝙤𝙪𝙣𝙩'𝙨 𝙖𝙘𝙩𝙞𝙫𝙚 𝙜𝙧𝙤𝙪𝙥 𝙫𝙘.</b></blockquote>",
    "vcfight": f"<blockquote>{pe()} <b>𝙫𝙘𝙛𝙞𝙜𝙝𝙩</b>\n\n{pe()} <b>/join &lt;group_id&gt;</b>\n{pe()} <b>.join &lt;group_id&gt;</b>\n{pe()} <b>/allvc join|leave</b>\n{pe()} <b>.allvc join|leave</b>\n{pe()} <b>/fight</b>\n{pe()} <b>.fight</b>\n{pe()} <b>/fightstop</b>\n{pe()} <b>.fightstop</b>\n{pe()} <b>/vcleave</b>\n{pe()} <b>.vcleave</b>\n{pe()} <b>/vcstatus</b>\n{pe()} <b>.vcstatus</b>\n{pe()} <b>/recordings</b>\n{pe()} <b>.recordings</b>\n{pe()} <b>/addrc</b>\n{pe()} <b>.addrc</b>\n{pe()} <b>/removerc</b>\n{pe()} <b>.removerc</b>\n{pe()} <b>/myrc</b>\n{pe()} <b>.myrc</b>\n{pe()} <b>/rcinfo</b>\n{pe()} <b>.rcinfo</b></blockquote>",
    "welcome": f"<blockquote>{pe()} <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚</b>\n\n{pe()} <b>/welcome on</b>\n{pe()} <b>.welcome on</b>\n{pe()} <b>/welcome off</b>\n{pe()} <b>.welcome off</b>\n\n{pe()} <b>𝙘𝙤𝙣𝙣𝙚𝙘𝙩𝙚𝙙 𝙖𝙘𝙘𝙤𝙪𝙣𝙩 𝙬𝙚𝙡𝙘𝙤𝙢𝙚𝙨 𝙣𝙚𝙬 𝙢𝙚𝙢𝙗𝙚𝙧𝙨 𝙬𝙝𝙚𝙣 𝙚𝙣𝙖𝙗𝙡𝙚𝙙.</b></blockquote>",
    "aichat": f"<blockquote>{pe()} <b>𝙖𝙞 𝙘𝙝𝙖𝙩</b>\n\n{pe()} <b>𝙪𝙨𝙚 𝙩𝙝𝙚 𝙚𝙭𝙞𝙨𝙩𝙞𝙣𝙜 𝙖𝙞 𝙘𝙝𝙖𝙩 𝙘𝙤𝙢𝙢𝙖𝙣𝙙𝙨 𝙛𝙧𝙤𝙢 𝙩𝙝𝙚 𝙘𝙤𝙣𝙣𝙚𝙘𝙩𝙚𝙙 𝙪𝙨𝙚𝙧𝙗𝙤𝙩.</b></blockquote>",
    "tools": f"<blockquote>{pe()} <b>𝙩𝙤𝙤𝙡𝙨</b>\n\n{pe()} <b>𝙖𝙡𝙡 𝙚𝙭𝙞𝙨𝙩𝙞𝙣𝙜 𝙩𝙤𝙤𝙡 𝙘𝙤𝙢𝙢𝙖𝙣𝙙𝙨 𝙧𝙚𝙢𝙖𝙞𝙣 𝙖𝙫𝙖𝙞𝙡𝙖𝙗𝙡𝙚.</b></blockquote>",
    "fun": f"<blockquote>{pe()} <b>𝙛𝙪𝙣</b>\n\n{pe()} <b>𝙖𝙡𝙡 𝙚𝙭𝙞𝙨𝙩𝙞𝙣𝙜 𝙛𝙪𝙣 𝙘𝙤𝙢𝙢𝙖𝙣𝙙𝙨 𝙧𝙚𝙢𝙖𝙞𝙣 𝙖𝙫𝙖𝙞𝙡𝙖𝙗𝙡𝙚.</b></blockquote>",
    "promotion": f"<blockquote>{pe()} <b>𝙥𝙧𝙤𝙢𝙤𝙩𝙞𝙤𝙣</b>\n\n{pe()} <b>.autotextpromo on</b>\n{pe()} <b>.autotextpromo off</b>\n{pe()} <b>.promotion &lt;text&gt;</b>\n\n{pe()} <b>𝙚𝙭𝙞𝙨𝙩𝙞𝙣𝙜 𝙖𝙪𝙩𝙤𝙩𝙚𝙭𝙩𝙥𝙧𝙤𝙢𝙤 𝙗𝙚𝙝𝙖𝙫𝙞𝙤𝙧 𝙞𝙨 𝙥𝙧𝙚𝙨𝙚𝙧𝙫𝙚𝙙.</b></blockquote>",
    "info": f"<blockquote>{pe()} <b>𝙞𝙣𝙛𝙤</b>\n\n{pe()} <b>𝙪𝙨𝙚 𝙩𝙝𝙚 𝙘𝙤𝙣𝙣𝙚𝙘𝙩𝙚𝙙 𝙪𝙨𝙚𝙧𝙗𝙤𝙩'𝙨 𝙚𝙭𝙞𝙨𝙩𝙞𝙣𝙜 .help 𝙛𝙤𝙧 𝙩𝙝𝙚 𝙘𝙤𝙢𝙥𝙡𝙚𝙩𝙚 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙡𝙞𝙨𝙩.</b></blockquote>",
}

def help_markup():
    rows = []
    for i in range(0, len(CATEGORIES), 2):
        rows.append([
            InlineKeyboardButton(CATEGORIES[i][0], callback_data=f"help_cat:{CATEGORIES[i][1]}"),
            InlineKeyboardButton(CATEGORIES[i+1][0], callback_data=f"help_cat:{CATEGORIES[i+1][1]}")
        ])
    rows.append([InlineKeyboardButton("𝙗𝙖𝙘𝙠", callback_data="force_help")])
    return InlineKeyboardMarkup(rows)

@app.on_callback_query(filters.regex(r"^help_cat:"))
async def help_category(client, query):
    key = query.data.split(":", 1)[1]
    await query.answer()
    await query.message.edit_caption(COMMANDS.get(key, HELP_TEXT), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("𝙝𝙚𝙡𝙥 𝙢𝙚𝙣𝙪", callback_data="force_help")]]), parse_mode="html")
