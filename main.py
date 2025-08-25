import importlib
import logging
import asyncio
from client import app
from config import LOG_GROUP_ID
from plugins import ALL_MODULES
from pyrogram import filters, idle
from pyrogram.types import Message
import importlib
import asyncio
import logging
import config

from pyrogram.types import (
    Message, 
    User, 
    Chat, 
    CallbackQuery, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove, 
    ForceReply, 
    InlineQuery, 
    InlineQueryResultArticle, 
    InputTextMessageContent, 
    BotCommand
)

from pyrogram import Client, filters
from pyrogram.types import Message
from collections import defaultdict
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.types import CallbackQuery
import random
from motor.motor_asyncio import AsyncIOMotorClient
from client import application, LOGGER, app
from plugins import ALL_MODULES

# Set up logging error handling
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

for module_name in ALL_MODULES:
    try:
        importlib.import_module("plugins." + module_name)
    except Exception as e:
        LOGGER.error(f"Failed to load module {module_name}: {e}", exc_info=True)

def main() -> None:
    """Run bot."""
    try:
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        LOGGER.error(f"Error in bot polling: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        app.start()
        LOGGER.info("Bot started successfully.")
        main()
    except Exception as e:
        LOGGER.critical(f"Bot failed to start: {e}", exc_info=True)