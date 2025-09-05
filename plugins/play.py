from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from urllib.parse import quote_plus

from config import MINI_APP_URL, LOG_GROUP_ID, YT_THUMBNAIL
from database.database import save_song_play
from client import app
from utils.youtube import YouTubeAPI

yt_api = YouTubeAPI()

@app.on_message(filters.command("play"))
async def play_command(client, message: Message):
    user = message.from_user
    query = message.text.split(" ", 1)

    if len(query) < 2 or not query[1].strip():
        return await message.reply(
            "❌ Please provide a song name or YouTube URL.\n\nExample: `/play aadat sucha yaar`",
            quote=True
        )

    song_query = query[1].strip()
    status_msg = await message.reply("🔍 Searching for the song...")

    try:
        # Get song info
        title, duration, duration_sec, thumb, vidid = await yt_api.details(song_query)

        # Get audio streamable URL
        success, audio_url = await yt_api.video_url(f"https://www.youtube.com/watch?v={vidid}")
        if not success:
            raise Exception(f"Failed to get audio URL.\n\n{audio_url}")

    except Exception as e:
        error_text = f"❌ Failed to fetch song.\n\nError: <code>{str(e)}</code>"
        try:
            return await status_msg.edit_text(error_text, parse_mode=ParseMode.HTML)
        except:
            await status_msg.delete()
            return await message.reply(error_text, parse_mode=ParseMode.HTML, quote=True)

    # Save play info
    await save_song_play(user.id, user.first_name, title, duration or "Unknown")

    # Log to group
    try:
        await client.send_message(
            chat_id=LOG_GROUP_ID,
            text=(
                f"🎶 <b>New Song Played</b>\n\n"
                f"👤 <b>User:</b> {user.first_name} (ID: <code>{user.id}</code>)\n"
                f"🎧 <b>Song:</b> {title}\n"
                f"⏱️ <b>Duration:</b> {duration or 'Unknown'}\n"
                f"💬 <b>Chat ID:</b> <code>{message.chat.id}</code>"
            ),
            parse_mode=ParseMode.HTML
        )
    except Exception as log_error:
        print(f"[LOG ERROR]: {log_error}")

    # Build WebApp URL
    audio_url_encoded = quote_plus(audio_url)
    title_encoded = quote_plus(title)
    thumb_encoded = quote_plus(thumb or YT_THUMBNAIL)

    webapp_url = f"{MINI_APP_URL}?audio={audio_url_encoded}&title={title_encoded}&thumb={thumb_encoded}"

    # Final music player response
    await status_msg.delete()
    await message.reply_photo(
        photo=thumb or YT_THUMBNAIL,
        caption=(
            f"🎵 <b>{title}</b>\n"
            f"⏱️ <b>Duration:</b> {duration or 'Unknown'}\n\n"
            f"▶️ Tap the button below to open the Web Music Player!"
        ),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                text="🎧 Play in WebApp",
                web_app=WebAppInfo(url=webapp_url)
            )
        ]]),
        parse_mode=ParseMode.HTML
    )
