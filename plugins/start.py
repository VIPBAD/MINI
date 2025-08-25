from pyrogram import filters
from pyrogram.types import Message
from client import app
from config import LOG_GROUP_ID
from database.database import save_user

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    user = message.from_user
    user_id = user.id
    first_name = user.first_name
    username = f"@{user.username}" if user.username else "None"

    await save_user(user_id, first_name, username)

    try:
        await client.send_message(
            chat_id=LOG_GROUP_ID,
            text=(
                f"📥 <b>New User Started the Bot</b>\n\n"
                f"👤 <b>Name:</b> {first_name}\n"
                f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
                f"🔗 <b>Username:</b> {username}"
            )
        )
    except Exception as e:
        print(f"Logging error: {e}")

    await message.reply_text(
        f"👋 Hello {first_name}!\n\n"
        "I'm your Music Bot with Mini App support. Use /play <song name or YouTube URL> to begin!",
        disable_web_page_preview=True
    )