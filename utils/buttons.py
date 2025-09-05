from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_play_buttons(deep_link, webapp_url):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="🎧 Join Room",
                url=deep_link  # Changed to URL for deep link
            )
        ],
        [
            InlineKeyboardButton(
                text="Close",
                callback_data="close"
            )
        ]
    ])
