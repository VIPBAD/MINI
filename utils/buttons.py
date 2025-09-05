from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

def get_play_buttons(webapp_url):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="🎧 Join Room",
                web_app=WebAppInfo(url=webapp_url)
            )
        ],
        [
            InlineKeyboardButton(
                text="Close",
                callback_data="close"
            )
        ]
    ])
