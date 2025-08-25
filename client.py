import logging
import os
from pyrogram import Client
from telegram.ext import Application
import config

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

try:
    application = Application.builder().token(config.BOT_TOKEN).build()
    LOGGER.info("Telegram Application initialized successfully.")
except Exception as e:
    LOGGER.critical(f"Failed to initialize Telegram Application: {e}", exc_info=True)
    raise  # Ensures the script stops if critical initialization fails

try:
    app = Client("miniapp", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
    LOGGER.info("Pyrogram Client initialized successfully.")
except Exception as e:
    LOGGER.critical(f"Failed to initialize Pyrogram Client: {e}", exc_info=True)
    raise  # Ensures the script stops if critical initialization fails