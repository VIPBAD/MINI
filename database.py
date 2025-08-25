
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import config

# Logger Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("database.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)

logger = logging.getLogger(__name__)

try:
    # Ensure MongoDB URL is provided
    if not config.MONGO_URI:
        raise ValueError("MongoDB URL is missing in config.")

    # Initialize MongoDB Connection
    MAINDB = AsyncIOMotorClient(config.MONGO_URI)
    db = MAINDB.MINIAPP

    # Define Collections
    collection = db.anime_character
    user_totals_collection = db.user_totals
    user_collection = db.user_collection
    group_user_totals_collection = db.group_user_totals
    top_global_groups_collection = db.htop_global_groups
    DM_USERS = db.DM_USERS
    GROUPS = db.GROUPS
    sudoersdb = db.sudoersdb
    sudoersdb_del = db.sudoersdb_del
    developer = db.developer
    givedeveloper = db.givedeveloper
    song_collection = db.song_collection
    users_col = db.users
    plays_col = db.plays

    logger.info("Connected to MongoDB successfully.")  # Corrected position

except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")

# Async Database Functions

# Save or update user on /start
async def save_user(user_id, name, username):
    users_col.update_one(
        {"user_id": user_id},
        {"$set": {
            "name": name,
            "username": username,
        }},
        upsert=True
    )

# Save song play
async def save_song_play(user_id, name, song_title, duration):
    plays_col.insert_one({
        "user_id": user_id,
        "name": name,
        "song_title": song_title,
        "duration": duration
    })

async def save_song_play(user_id: int, user_name: str, song_title: str, duration: str):
    try:
        await song_collection.insert_one({
            "user_id": user_id,
            "user_name": user_name,
            "song_title": song_title,
            "duration": duration
        })
    except Exception as e:
        print(f"[DB Error] Failed to save song play: {e}")

async def get_user_song_history(user_id: int):
    try:
        return await song_collection.find({"user_id": user_id}).to_list(length=50)
    except Exception as e:
        print(f"[DB Error] Failed to retrieve history: {e}")
        return []