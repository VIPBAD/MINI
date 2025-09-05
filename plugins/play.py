from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from urllib.parse import quote_plus

from config import MINI_APP_URL, LOG_GROUP_ID, YT_THUMBNAIL
from database.database import save_song_play
from client import app
from utils.youtube import YouTubeAPI
from utils.buttons import get_play_buttons
import utils.strings as strings

yt_api = YouTubeAPI()
queue = []

@app.on_message(filters.command("play"))
async def play_command(client, message: Message):
    user = message.from_user
    query = message.text.split(" ", 1)

    if len(query) < 2 or not query[1].strip():
        return await message.reply(
            strings.NO_QUERY,
            quote=True
        )

    song_query = query[1].strip()
    status_msg = await message.reply(strings.SEARCHING)

    try:
        title, duration, duration_sec, thumb, vidid = await yt_api.details(song_query)
        success, audio_url = await yt_api.video_url(f"https://www.youtube.com/watch?v={vidid}")
        if not success:
            raise Exception(f"Failed to get audio URL.\n\n{audio_url}")

    except Exception as e:
        error_text = strings.FETCH_ERROR.format(error=str(e))
        try:
            return await status_msg.edit_text(error_text, parse_mode=ParseMode.HTML)
        except:
            await status_msg.delete()
            return await message.reply(error_text, parse_mode=ParseMode.HTML, quote=True)

    await save_song_play(user.id, user.first_name, title, duration or "Unknown")

    try:
        await client.send_message(
            chat_id=LOG_GROUP_ID,
            text=(
                f"🎶 <b>{strings.NEW_SONG}</b>\n\n"
                f"👤 <b>{strings.USER}:</b> {user.first_name} (ID: <code>{user.id}</code>)\n"
                f"🎧 <b>{strings.SONG}:</b> {title}\n"
                f"⏱️ <b>{strings.DURATION}:</b> {duration or 'Unknown'}\n"
                f"💬 <b>{strings.CHAT_ID}:</b> <code>{message.chat.id}</code>"
            ),
            parse_mode=ParseMode.HTML
        )
    except Exception as log_error:
        print(f"[LOG ERROR]: {log_error}")

    audio_url_encoded = quote_plus(audio_url)
    title_encoded = quote_plus(title)
    thumb_encoded = quote_plus(thumb or YT_THUMBNAIL)

    # Fetch bot username
    me = await client.get_me()
    deep_link = f"https://t.me/{me.username}?startapp={user.id}"

    webapp_url = f"{MINI_APP_URL}?audio={audio_url_encoded}&title={title_encoded}&thumb={thumb_encoded}"
    queue.append({"title": title, "duration": duration, "url": webapp_url})

    await status_msg.delete()
    await message.reply_photo(
        photo=thumb or YT_THUMBNAIL,
        caption=(
            f"🎵 <b>{title}</b>\n"
            f"⏱️ <b>{strings.DURATION}:</b> {duration or 'Unknown'}\n\n"
            f"▶️ {strings.PLAY_BUTTON_TEXT}"
        ),
        reply_markup=get_play_buttons(webapp_url),
        parse_mode=ParseMode.HTML
    )

@app.on_message(filters.command("skip"))
async def skip_command(client, message: Message):
    if queue:
        queue.pop(0)
        if queue:
            await message.reply(strings.SONG_SKIPPED, quote=True)
        else:
            await message.reply(strings.NO_MORE_SONGS, quote=True)
    else:
        await message.reply(strings.NO_SONS_QUEUE, quote=True)

@app.on_message(filters.command("pause"))
async def pause_command(client, message: Message):
    await message.reply(strings.SONG_PAUSED, quote=True)

@app.on_message(filters.command("resume"))
async def resume_command(client, message: Message):
    await message.reply(strings.SONG_RESUMED, quote=True)

# Check queue and notify when empty
async def check_queue(client):
    while True:
        if not queue:
            await client.send_message(message.chat.id, strings.NO_MORE_SONGS)
            break
        await asyncio.sleep(1)
