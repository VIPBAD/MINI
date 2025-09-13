# play.py
import logging
from urllib.parse import quote_plus

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from client import app
from config import LOG_GROUP_ID
from database.database import save_song_play
from utils.youtube import YouTubeAPI

yt_api = YouTubeAPI()
log = logging.getLogger(__name__)

@app.on_message(filters.command("play") & filters.group)
async def play_command(client, message: Message):
    user = message.from_user
    if not user:
        return await message.reply_text("❌ Unable to get user info.", quote=True)

    parts = message.text.split(" ", 1)
    if len(parts) < 2 or not parts[1].strip():
        return await message.reply("❌ Please provide a song name or YouTube URL.\nExample: `/play aadat`", quote=True)

    song_query = parts[1].strip()
    status_msg = await message.reply_text("🔍 Searching for the song...", quote=True)

    try:
        title, duration, duration_sec, thumb, vidid = await yt_api.details(song_query)
        title = title or "Unknown Title"
        duration = duration or "Unknown"
        thumb = thumb or "https://via.placeholder.com/200"

        success, audio_url_or_error = await yt_api.video_url(f"https://www.youtube.com/watch?v={vidid}")
        if not success:
            raise RuntimeError(audio_url_or_error)
        audio_url = audio_url_or_error
    except Exception as e:
        return await status_msg.edit_text(f"❌ Failed: {e}")

    # Save play info
    try:
        await save_song_play(user.id, user.first_name or "", title, duration)
    except Exception as db_err:
        log.warning("DB save error: %s", db_err)

    # Log to group
    try:
        await client.send_message(
            chat_id=LOG_GROUP_ID,
            text=(
                f"🎶 <b>New Song Played</b>\n\n"
                f"👤 <b>User:</b> {user.first_name} (ID: <code>{user.id}</code>)\n"
                f"🎧 <b>Song:</b> {title}\n"
                f"⏱️ <b>Duration:</b> {duration}\n"
                f"💬 <b>From Group:</b> <code>{message.chat.id}</code>"
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception as log_error:
        log.warning("Logger send failed: %s", log_error)

    # Deep Link
    deep_link = f"https://t.me/TGINLINEMUSICBOT/Demo?start=play_{vidid}"

    await status_msg.delete()
    await message.reply_photo(
        photo=thumb,
        caption=f"🎵 <b>{title}</b>\n⏱️ <b>{duration}</b>\n\n▶️ Tap below to open player.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎧 Open in Player", url=deep_link)]]),
        parse_mode=ParseMode.HTML,
        quote=True,
    )
