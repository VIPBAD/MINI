from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import MINI_APP_URL, BOT_USERNAME

def music_player_buttons(audio_url, title, thumb, chat_id, user_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏭️ Skip", callback_data=f"skip_{chat_id}_{user_id}"),
            InlineKeyboardButton("⏸️ Pause", callback_data=f"pause_{chat_id}_{user_id}"),
            InlineKeyboardButton("▶️ Resume", callback_data=f"resume_{chat_id}_{user_id}")
        ],
        [
            InlineKeyboardButton(
                text="🎧 Join Room",
                url=f"https://t.me/{BOT_USERNAME}?startapp={chat_id}"
            ),
            InlineKeyboardButton("❌ Close", callback_data=f"close_{chat_id}_{user_id}")
        ]
    ])

def no_more_songs_button():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🎶 Play New Song", switch_inline_query_current_chat="")
    ]])
