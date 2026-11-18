from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo
from Waste import app

START_VIDEO_URL = "https://www.image2url.com/r2/default/videos/1795028137883-50dbfe05-30ea-4fdd-bee6-9918b92c79db.mp4"
PE_HOST = "5471952986970267163"
PE_COMMAND = "5445284980978621387"
PE_PAGE = "5226512880362332956"
PE_MAIN = "5989975649740134220"
PE_NEXT = "5992269308305084799"

def pe(eid, fallback="✦"):
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'

def ser(name):
    lower = "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯"
    upper = "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"
    return str(name).translate(str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", lower + upper))

HELP_TEXT = f"<blockquote>{pe(PE_HOST)} <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ʜᴇʟᴘ</b>\n\n{pe(PE_HOST)} <b>ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ.</b></blockquote>"
CATEGORIES=[("music","music"),("vcfight","vcfight"),("welcome","welcome"),("ai chat","aichat"),("tools","tools"),("fun","fun"),("promotion","promotion"),("info","info")]
COMMANDS={
"music":f"<blockquote>{pe(PE_HOST)} <b>𝙢𝙪𝙨𝙞𝙘</b>\n\n{pe(PE_HOST)} <b>/play song name</b>\n{pe(PE_HOST)} <b>.play song name</b></blockquote>",
"vcfight":f"<blockquote>{pe(PE_HOST)} <b>𝙫𝙘𝙛𝙞𝙜𝙝𝙩</b>\n\n{pe(PE_HOST)} <b>/join &lt;group_id&gt;</b>\n{pe(PE_HOST)} <b>.join &lt;group_id&gt;</b>\n{pe(PE_HOST)} <b>/allvc join|leave</b>\n{pe(PE_HOST)} <b>/fight</b>\n{pe(PE_HOST)} <b>/fightstop</b>\n{pe(PE_HOST)} <b>/recordings</b>\n{pe(PE_HOST)} <b>/addrc</b>\n{pe(PE_HOST)} <b>/removerc</b>\n{pe(PE_HOST)} <b>/myrc</b>\n{pe(PE_HOST)} <b>/rcinfo</b></blockquote>",
"welcome":f"<blockquote>{pe(PE_HOST)} <b>𝙬𝙚𝙡𝙘𝙤𝙢𝙚</b>\n\n{pe(PE_HOST)} <b>/welcome on</b>\n{pe(PE_HOST)} <b>/welcome off</b></blockquote>",
"aichat":f"<blockquote>{pe(PE_HOST)} <b>𝙖𝙞 𝙘𝙝𝙖𝙩</b>\n\n{pe(PE_HOST)} <b>ᴀɪ ᴄʜᴀᴛ ᴄᴏᴍᴍᴀɴᴅs ʀᴇᴍᴀɪɴ ᴀᴠᴀɪʟᴀʙʟᴇ.</b></blockquote>",
"tools":f"<blockquote>{pe(PE_HOST)} <b>𝙩𝙤𝙤𝙡𝙨</b>\n\n{pe(PE_HOST)} <b>ᴀʟʟ ᴇxɪsᴛɪɴɢ ᴛᴏᴏʟ ᴄᴏᴍᴍᴀɴᴅs ʀᴇᴍᴀɪɴ ᴀᴠᴀɪʟᴀʙʟᴇ.</b></blockquote>",
"fun":f"<blockquote>{pe(PE_HOST)} <b>𝙛𝙪𝙣</b>\n\n{pe(PE_HOST)} <b>ᴀʟʟ ᴇxɪsᴛɪɴɢ ғᴜɴ ᴄᴏᴍᴍᴀɴᴅs ʀᴇᴍᴀɪɴ ᴀᴠᴀɪʟᴀʙʟᴇ.</b></blockquote>",
"promotion":f"<blockquote>{pe(PE_HOST)} <b>𝙥𝙧𝙤𝙢𝙤𝙩𝙞𝙤𝙣</b>\n\n{pe(PE_HOST)} <b>.autotextpromo on</b>\n{pe(PE_HOST)} <b>.autotextpromo off</b>\n{pe(PE_HOST)} <b>.promotion &lt;text&gt;</b></blockquote>",
"info":f"<blockquote>{pe(PE_HOST)} <b>𝙞𝙣𝙛𝙤</b>\n\n{pe(PE_HOST)} <b>ᴜsᴇ ᴛʜᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴜsᴇʀʙᴏᴛ's .help ғᴏʀ ᴛʜᴇ ᴄᴏᴍᴘʟᴇᴛᴇ ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ.</b></blockquote>",
}
try:
    from Waste.modules.help.help import CMD_HELP, _find_help_key, _module_text
    FORCE_COMMANDS=sorted(dict.fromkeys([cmd for module in CMD_HELP.values() for cmd in module]),key=str.lower)
except Exception:
    CMD_HELP={}; FORCE_COMMANDS=[]
    _find_help_key=lambda x:None
    _module_text=lambda x:HELP_TEXT
PAGE_SIZE=11
TOTAL_PAGES=6

def force_page_text(page=0):
    page=max(0,min(int(page),TOTAL_PAGES-1))
    items=FORCE_COMMANDS[page*PAGE_SIZE:(page+1)*PAGE_SIZE]
    lines=["<blockquote>✦ <b>ＷＡＳＴＥ Ｘ ＵＢＯＴ — ꜰᴏʀᴄᴇ ᴄᴏᴍᴍᴀɴᴅs</b>"]
    for name in items: lines.append(f"{pe(PE_COMMAND)} <b>{ser(name)}</b>")
    lines.append(f"{pe(PE_PAGE)} <b>ᴘᴀɢᴇ {page+1}/{TOTAL_PAGES}</b>")
    if page<TOTAL_PAGES-1: lines.append(f"{pe(PE_NEXT)} <b>ɴᴇxᴛ</b>")
    lines.append(f"{pe(PE_MAIN)} <b>ᴍᴀɪɴ ᴍᴇɴᴜ</b>")
    lines.append("</blockquote>")
    return "\n".join(lines)

def force_markup(page=0):
    page=max(0,min(int(page),TOTAL_PAGES-1)); items=FORCE_COMMANDS[page*PAGE_SIZE:(page+1)*PAGE_SIZE]
    rows=[]
    for i in range(0,len(items),2):
        row=[InlineKeyboardButton(ser(items[i]),callback_data=f"force_cmd:{items[i]}")]
        if i+1<len(items): row.append(InlineKeyboardButton(ser(items[i+1]),callback_data=f"force_cmd:{items[i+1]}"))
        rows.append(row)
    nav=[]
    if page>0: nav.append(InlineKeyboardButton(ser("prev"),callback_data=f"force_page:{page-1}"))
    nav.append(InlineKeyboardButton(ser(f"page {page+1}/{TOTAL_PAGES}"),callback_data="force_noop"))
    if page<TOTAL_PAGES-1: nav.append(InlineKeyboardButton(ser("next"),callback_data=f"force_page:{page+1}"))
    rows.append(nav); rows.append([InlineKeyboardButton(ser("main menu"),callback_data="help_main")])
    return InlineKeyboardMarkup(rows)

def help_markup():
    rows=[]
    for i in range(0,len(CATEGORIES),2):
        rows.append([InlineKeyboardButton(ser(CATEGORIES[i][0]),callback_data=f"help_cat:{CATEGORIES[i][1]}"),InlineKeyboardButton(ser(CATEGORIES[i+1][0]),callback_data=f"help_cat:{CATEGORIES[i+1][1]}")])
    rows.append([InlineKeyboardButton(ser("force commands"),callback_data="help_force")])
    rows.append([InlineKeyboardButton(ser("main menu"),callback_data="help_main")])
    return InlineKeyboardMarkup(rows)

@app.on_callback_query(filters.regex(r"^help_cat:"))
async def help_category(client,query):
    await query.answer(); key=query.data.split(":",1)[1]
    await query.message.edit_media(InputMediaVideo(START_VIDEO_URL,caption=COMMANDS.get(key,HELP_TEXT),parse_mode=enums.ParseMode.HTML),reply_markup=help_markup())

@app.on_callback_query(filters.regex(r"^help_force$"))
async def help_force(client,query):
    await query.answer(); await query.message.edit_media(InputMediaVideo(START_VIDEO_URL,caption=force_page_text(0),parse_mode=enums.ParseMode.HTML),reply_markup=force_markup(0))

@app.on_callback_query(filters.regex(r"^force_page:"))
async def force_page_callback(client,query):
    await query.answer(); page=int(query.data.split(":",1)[1])
    await query.message.edit_media(InputMediaVideo(START_VIDEO_URL,caption=force_page_text(page),parse_mode=enums.ParseMode.HTML),reply_markup=force_markup(page))

@app.on_callback_query(filters.regex(r"^force_cmd:"))
async def force_cmd_callback(client,query):
    await query.answer(); raw=query.data.split(":",1)[1]; key=_find_help_key(raw) or raw
    await query.message.edit_media(InputMediaVideo(START_VIDEO_URL,caption=_module_text(key),parse_mode=enums.ParseMode.HTML),reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(ser("back to force commands"),callback_data="help_force")]]))

@app.on_callback_query(filters.regex(r"^force_noop$"))
async def force_noop(client,query): await query.answer()

@app.on_callback_query(filters.regex(r"^help_main$"))
async def help_main(client,query):
    await query.answer(); from Waste.modules.bot.start import _start_caption,START_BUTTONS
    await query.message.edit_media(InputMediaVideo(START_VIDEO_URL,caption=_start_caption(query.from_user),parse_mode=enums.ParseMode.HTML),reply_markup=InlineKeyboardMarkup(START_BUTTONS))
