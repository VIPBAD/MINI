from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from urllib.parse import quote_plus

from config import MINI_APP_URL, LOG_GROUP_ID, YT_THUMBNAIL
from database.database import save_song_play
from client import app
from utils.youtube import YouTubeAPI
from utils.buttons import music_player_buttons, no_more_songs_button
from utils.strings import STRINGS

# Local queue dict
queue = {}

yt_api = YouTubeAPI()

@app.on_message(filters.command("play"))
async def play_command(client, message: Message):
    user = message.from_user
    chat_id = message.chat.id
    query = message.text.split(" ", 1)

    if len(query) < 2 or not query[1].strip():
        return await message.reply(STRINGS["no_query"], quote=True)

    song_query = query[1].strip()
    status_msg = await message.reply(STRINGS["searching"])

    try:
        # Song info
        title, duration, duration_sec, thumb, vidid = await yt_api.details(song_query)

        # Audio stream URL
        success, audio_url = await yt_api.video_url(f"https://www.youtube.com/watch?v={vidid}")
        if not success:
            raise Exception(audio_url)

    except Exception as e:
        error_text = STRINGS["error"].format(error=str(e))
        await status_msg.delete()
        return await message.reply(error_text, parse_mode=ParseMode.HTML, quote=True)

    # Save play info
    await save_song_play(user.id, user.first_name, title, duration or "Unknown")

    # Add to queue
    if chat_id not in queue:
        queue[chat_id] = []
    queue[chat_id].append({
        "title": title,
        "duration": duration or "Unknown",
        "thumb": thumb or YT_THUMBNAIL,
        "url": audio_url,
        "user": user.id
    })

    # If song already playing, just queue it
    if len(queue[chat_id]) > 1:
        await status_msg.delete()
        return await message.reply(
            f"➕ Added to queue: <b>{title}</b> ({duration})",
            parse_mode=ParseMode.HTML
        )

    # First song → play it
    await status_msg.delete()
    await message.reply_photo(
        photo=thumb or YT_THUMBNAIL,
        caption=STRINGS["now_playing"].format(title=title, duration=duration or "Unknown"),
        reply_markup=music_player_buttons(audio_url, title, thumb, chat_id, user.id),
        parse_mode=ParseMode.HTML
    )

# Skip button handler
@app.on_callback_query(filters.regex(r"^skip_"))
async def skip_song(client, callback_query):
    chat_id = int(callback_query.data.split("_")[1])
    if chat_id in queue and len(queue[chat_id]) > 1:
        queue[chat_id].pop(0)
        next_song = queue[chat_id][0]
        await callback_query.message.edit_caption(
            STRINGS["now_playing"].format(
                title=next_song["title"],
                duration=next_song["duration"]
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=music_player_buttons(
                next_song["url"], next_song["title"], next_song["thumb"], chat_id, next_song["user"]
            )
        )
    else:
        queue.pop(chat_id, None)
        await callback_query.message.edit_caption(
            STRINGS["queue_ended"],
            parse_mode=ParseMode.HTML,
            reply_markup=no_more_songs_button()
        )

# Pause/Resume/Close → dummy handlers
@app.on_callback_query(filters.regex(r"^pause_"))
async def pause_song(client, callback_query):
    await callback_query.answer("⏸️ Song paused (dummy).", show_alert=True)

@app.on_callback_query(filters.regex(r"^resume_"))
async def resume_song(client, callback_query):
    await callback_query.answer("▶️ Song resumed (dummy).", show_alert=True)

@app.on_callback_query(filters.regex(r"^close_"))
async def close_player(client, callback_query):
    await callback_query.message.delete()
