from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Waste import app

PE = lambda eid, fallback="·": f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'
PE_COMMAND = 5445284980978621387
PE_MAIN = 5989975649740134220

HELP_TEXT = f"""<blockquote>{PE(PE_MAIN)} <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — 𝙝𝙚𝙡𝙥 𝙢𝙚𝙣𝙪</b>\n\n{PE(PE_COMMAND)} 𝙘𝙝𝙤𝙤𝙨𝙚 𝙖 𝙘𝙖𝙩𝙚𝙜𝙤𝙧𝙮 𝙩𝙤 𝙫𝙞𝙚𝙬 𝙞𝙩𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙𝙨.\n\n{PE(PE_COMMAND)} 𝙪𝙨𝙚 <code>.</code> 𝙤𝙧 <code>/</code> 𝙬𝙝𝙚𝙧𝙚 𝙨𝙪𝙥𝙥𝙤𝙧𝙩𝙚𝙙.</blockquote>"""

CATEGORIES = [
    ("𝙢𝙪𝙨𝙞𝙘", "music"), ("𝙫𝙘𝙛𝙞𝙜𝙝𝙩", "vcfight"),
    ("𝙬𝙚𝙡𝙘𝙤𝙢𝙚", "welcome"), ("𝙖𝙞 𝙘𝙝𝙖𝙩", "aichat"),
    ("𝙩𝙤𝙤𝙡𝙨", "tools"), ("𝙛𝙪𝙣", "fun"),
    ("𝙥𝙧𝙤𝙢𝙤𝙩𝙞𝙤𝙣", "promotion"), ("𝙞𝙣𝙛𝙤", "info"),
]

COMMANDS = {
    "music": "<blockquote><b>𝙢𝙪𝙨𝙞𝙘</b>\n\n/play song name\n.play song name\n\nPlay the requested song in the connected account's active group VC.</blockquote>",
    "vcfight": "<blockquote><b>𝙫𝙘𝙛𝙞𝙜𝙝𝙩</b>\n\n/join &lt;group_id&gt;\n.join &lt;group_id&gt;\n/allvc join|leave\n.allvc join|leave\n/fight\n.fight\n/fightstop\n.fightstop\n/vcleave\n.vcleave\n/vcstatus\n.vcstatus\n/recordings\n.recordings\n/addrc\n.addrc\n/removerc\n.removerc\n/myrc\n.myrc\n/rcinfo\n.rcinfo</blockquote>",
    "welcome": "<blockquote><b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚</b>\n\n/welcome on\n.welcome on\n/welcome off\n.welcome off\n\nConnected account welcomes new members in its groups when enabled.</blockquote>",
    "aichat": "<blockquote><b>𝙖𝙞 𝙘𝙝𝙖𝙩</b>\n\nUse the existing AI Chat commands from the connected userbot.</blockquote>",
    "tools": "<blockquote><b>𝙩𝙤𝙤𝙡𝙨</b>\n\nAll existing tool commands remain available from the userbot's .help menu.</blockquote>",
    "fun": "<blockquote><b>𝙛𝙪𝙣</b>\n\nAll existing fun commands remain available from the userbot's .help menu.</blockquote>",
    "promotion": "<blockquote><b>𝙥𝙧𝙤𝙢𝙤𝙩𝙞𝙤𝙣</b>\n\n.autotextpromo on\n.autotextpromo off\n.promotion &lt;text&gt;\n\nExisting AutoTextPromo behavior is preserved with more varied text.</blockquote>",
    "info": "<blockquote><b>𝙞𝙣𝙛𝙤</b>\n\nUse the connected userbot's existing .help command for the complete command list.</blockquote>",
}

def help_markup():
    rows=[]
    for i in range(0,len(CATEGORIES),2):
        rows.append([InlineKeyboardButton(CATEGORIES[i][0], callback_data=f"help_cat:{CATEGORIES[i][1]}"), InlineKeyboardButton(CATEGORIES[i+1][0], callback_data=f"help_cat:{CATEGORIES[i+1][1]}")])
    return InlineKeyboardMarkup(rows + [[InlineKeyboardButton("𝙗𝙖𝙘𝙠", callback_data="force_help")]])

@app.on_callback_query(filters.regex(r"^help_cat:"))
async def help_category(client, query):
    key=query.data.split(":",1)[1]
    await query.answer()
    await query.message.edit_caption(COMMANDS.get(key, HELP_TEXT), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("𝙝𝙚𝙡𝙥 𝙢𝙚𝙣𝙪", callback_data="force_help")]]))
