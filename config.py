import os

# Telegram Bot Credentials
API_ID = int(os.getenv("API_ID", 17609888))  # Replace with your API ID
API_HASH = os.getenv("API_HASH", "6538740296c179c5f5a2c52f911864d1")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8482046560:AAHDHQAgtnWNp7gQr7c5E6MKLtxnvyytyDI")

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://mongodbflex:L3GxCeWU3UcgFZZX-hwjiwjve@cluster0.czbo8.mongodb.net/?retryWrites=true&w=majority")

# Log group to receive logs when users start the bot or play songs
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", -1002093247039))

# Default YouTube thumbnail if not found
YT_THUMBNAIL = os.getenv("YT_THUMBNAIL", "https://i.ibb.co/JFr2D1nZ/photo-2025-06-04-08-20-01-7512006038174826500.jpg")

# Mini App Base URL (e.g., Render or Vercel deployed web app)
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://api-ojh9.onrender.com/")

BOT_USERNAME = "ANONMUSIC11_BOT"
