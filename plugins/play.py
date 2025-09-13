# play.py
import logging
from urllib.parse import quote_plus

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from client import app
from config import MINI_APP_URL, LOG_GROUP_ID, YT_THUMBNAIL
from database.database import save_song_play
from utils.youtube import YouTubeAPI

yt_api = YouTubeAPI()
log = logging.getLogger(__name__)


@app.on_message(filters.command("play"))
async def play_command(client, message: Message):
    user = message.from_user
    if not user:
        return await message.reply_text("❌ Unable to get user info.", quote=True)

    # Parse query
    parts = message.text.split(" ", 1)
    if len(parts) < 2 or not parts[1].strip():
        return await message.reply(
            "❌ Please provide a song name or YouTube URL.\n\nExample: `/play aadat sucha yaar`",
            quote=True,
        )

    song_query = parts[1].strip()
    status_msg = await message.reply_text("🔍 Searching for the song...", quote=True)

    try:
        # Get song info from your YouTubeAPI wrapper
        title, duration, duration_sec, thumb, vidid = await yt_api.details(song_query)

        # Fallbacks
        thumb = thumb or YT_THUMBNAIL
        title = title or "Unknown Title"
        duration = duration or "Unknown"

        # Get audio streamable URL (your function should return (success_bool, url_or_error))
        success, audio_url_or_error = await yt_api.video_url(f"https://www.youtube.com/watch?v={vidid}")
        if not success or not audio_url_or_error:
            raise RuntimeError(f"Failed to get audio URL. Detail: {audio_url_or_error}")

        audio_url = audio_url_or_error

    except Exception as e:
        err_text = f"❌ Failed to fetch song.\n\nError: <code>{str(e)}</code>"
        try:
            return await status_msg.edit_text(err_text, parse_mode=ParseMode.HTML)
        except Exception:
            await status_msg.delete()
            return await message.reply(err_text, parse_mode=ParseMode.HTML, quote=True)

    # Save play info to DB (non-blocking)
    try:
        await save_song_play(user.id, user.first_name or "", title, duration)
    except Exception as db_err:
        log.warning("Failed to save song play: %s", db_err)

    # Log to group (best-effort)
    try:
        await client.send_message(
            chat_id=LOG_GROUP_ID,
            text=(
                f"🎶 <b>New Song Played</b>\n\n"
                f"👤 <b>User:</b> {user.first_name or 'Unknown'} (ID: <code>{user.id}</code>)\n"
                f"🎧 <b>Song:</b> {title}\n"
                f"⏱️ <b>Duration:</b> {duration}\n"
                f"💬 <b>Chat ID:</b> <code>{message.chat.id}</code>"
            ),
            parse_mode=ParseMode.HTML,
        )
    except Exception as log_error:
        log.warning("Log group message failed: %s", log_error)

    # Build WebApp URL and encode params
    try:
        audio_url_encoded = quote_plus(audio_url)
        title_encoded = quote_plus(title)
        thumb_encoded = quote_plus(thumb)
        webapp_url = f"{MINI_APP_URL}?audio={audio_url_encoded}&title={title_encoded}&thumb={thumb_encoded}"
    except Exception as e:
        await status_msg.delete()
        return await message.reply_text(f"❌ Failed to prepare webapp URL.\n\nError: {e}", quote=True)

    # Reply with photo + WebApp button
    try:
        await status_msg.delete()
    except Exception:
        pass

    try:
        await message.reply_photo(
            photo=thumb,
            caption=(
                f"🎵 <b>{title}</b>\n"
                f"⏱️ <b>Duration:</b> {duration}\n\n"
                f"▶️ Tap the button below to open the Web Music Player!"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🎧 Play in WebApp",
                            web_app=WebAppInfo(url=webapp_url),
                        )
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
            quote=True,
        )
    except Exception as e:
        # final fallback: send plain text with URL
        log.exception("Failed to send photo + webapp button: %s", e)
        await message.reply_text(
            f"🎵 {title}\nDuration: {duration}\n\nOpen player: {webapp_url}",
            disable_web_page_preview=True,
            quote=True,
        )   
