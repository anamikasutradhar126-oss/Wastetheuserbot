from html import escape

# Telegram custom-emoji document IDs supplied for the Waste X UBot UI.
PE_HOST = 5471952986970267163
PE_COMMAND = 5445284980978621387
PE_PAGE = 5226512880362332956
PE_MAIN = 5989975649740134220
PE_NEXT = 5992269308305084799


def pe(emoji_id: int, fallback: str = "✦") -> str:
    "<emoji id=\"{emoji_id}\">{fallback}</emoji>"
    return f'<emoji id="{emoji_id}">{escape(fallback)}</emoji>'


def line(text: str, emoji_id: int = PE_HOST) -> str:
    return f"{pe(emoji_id)} {text}"


def serendipity(text: str) -> str:
    # Mathematical Sans Serif Bold Italic: 𝙖 𝙗 𝙘 ...
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    styled = (
        "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯"
        "𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕"
    )
    table = str.maketrans(normal, styled)
    return text.translate(table)


def customize_bot_text(text: str) -> str:
    """Replace only ordinary standalone emoji characters in bot-facing text.

    This is intentionally conservative: URLs, Markdown/HTML syntax and command
    names are left untouched. The main bot UI uses explicit premium emoji IDs.
    """
    return text
