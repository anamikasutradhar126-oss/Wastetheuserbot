from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Waste import app

HELP_TEXT = """<blockquote>❁ <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ - ＨＥＬＰ ＭＥＮＵ</b> ❁\n\nChoose a category below. Commands and existing features stay unchanged.\n\n🔴 Tap a command category to view its commands.\n🔵 Use either <code>.</code> or <code>/</code> where supported.</blockquote>"""

CATEGORIES = [
    ("🎵 MUSIC", "music"), ("🎙️ VCFIGHT", "vcfight"),
    ("🏠 WELCOME", "welcome"), ("🤖 AI CHAT", "aichat"),
    ("🛠️ TOOLS", "tools"), ("🎨 FUN", "fun"),
    ("📢 PROMOTION", "promotion"), ("ℹ️ INFO", "info"),
]

COMMANDS = {
    "music": "<blockquote><b>🎵 MUSIC</b>\n\n/play song name\n.play song name\n\nPlay the requested song in the connected account's active group VC.</blockquote>",
    "vcfight": "<blockquote><b>🎙️ VCFIGHT</b>\n\n/join &lt;group_id&gt;\n.join &lt;group_id&gt;\n/allvc join|leave\n.allvc join|leave\n/fight\n.fight\n/fightstop\n.fightstop\n/vcleave\n.vcleave\n/vcstatus\n.vcstatus\n/recordings\n.recordings\n/addrc\n.addrc\n/removerc\n.removerc\n/myrc\n.myrc\n/rcinfo\n.rcinfo</blockquote>",
    "welcome": "<blockquote><b>🏠 WELCOME</b>\n\n/welcome on\n.welcome on\n/welcome off\n.welcome off\n\nConnected account welcomes new members in its groups when enabled.</blockquote>",
    "aichat": "<blockquote><b>🤖 AI CHAT</b>\n\nUse the existing AI Chat commands from the connected userbot.</blockquote>",
    "tools": "<blockquote><b>🛠️ TOOLS</b>\n\nAll existing tool commands remain available from the userbot's .help menu.</blockquote>",
    "fun": "<blockquote><b>🎨 FUN</b>\n\nAll existing fun commands remain available from the userbot's .help menu.</blockquote>",
    "promotion": "<blockquote><b>📢 PROMOTION</b>\n\n.autotextpromo on\n.autotextpromo off\n.promotion &lt;text&gt;\n\nExisting AutoTextPromo behavior is preserved with more varied text.</blockquote>",
    "info": "<blockquote><b>ℹ️ INFO</b>\n\nUse the connected userbot's existing .help command for the complete command list.</blockquote>",
}

def help_markup():
    rows=[]
    for i in range(0,len(CATEGORIES),2):
        rows.append([InlineKeyboardButton(CATEGORIES[i][0], callback_data=f"help_cat:{CATEGORIES[i][1]}"), InlineKeyboardButton(CATEGORIES[i+1][0], callback_data=f"help_cat:{CATEGORIES[i+1][1]}")])
    return InlineKeyboardMarkup(rows + [[InlineKeyboardButton("🔙 BACK", callback_data="force_help")]])

@app.on_callback_query(filters.regex(r"^help_cat:"))
async def help_category(client, query):
    key=query.data.split(":",1)[1]
    await query.answer()
    await query.message.edit_caption(COMMANDS.get(key, HELP_TEXT), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 HELP MENU", callback_data="force_help")]]))
