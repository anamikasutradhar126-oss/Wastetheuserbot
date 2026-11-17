import re
_SMALL_CAPS = str.maketrans({"a":"ᴀ","b":"ʙ","c":"ᴄ","d":"ᴅ","e":"ᴇ","f":"ғ","g":"ɢ","h":"ʜ","i":"ɪ","j":"ᴊ","k":"ᴋ","l":"ʟ","m":"ᴍ","n":"ɴ","o":"ᴏ","p":"ᴘ","q":"ǫ","r":"ʀ","s":"s","t":"ᴛ","u":"ᴜ","v":"ᴠ","w":"ᴡ","x":"х","y":"ʏ","z":"ᴢ","A":"ᴀ","B":"ʙ","C":"ᴄ","D":"ᴅ","E":"ᴇ","F":"ғ","G":"ɢ","H":"ʜ","I":"ɪ","J":"ᴊ","K":"ᴋ","L":"ʟ","M":"ᴍ","N":"ɴ","O":"ᴏ","P":"ᴘ","Q":"ǫ","R":"ʀ","S":"s","T":"ᴛ","U":"ᴜ","V":"ᴠ","W":"ᴡ","X":"х","Y":"ʏ","Z":"ᴢ"})
def stylish_text(value): return str(value).translate(_SMALL_CAPS)
def stylish_html(value):
    parts=re.split(r"(<[^>]+>)",str(value)); in_code=False; out=[]
    for part in parts:
        if part.startswith("<"):
            out.append(part)
            if re.match(r"</?(code|pre)\b",part,re.I): in_code=not part.lower().startswith("</")
        else: out.append(part if in_code else stylish_text(part))
    return "".join(out)
