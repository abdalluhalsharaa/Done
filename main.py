# ==============================
# main.py
# Personal Telegram AI Userbot
# ==============================

import asyncio
import logging
import threading
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

from config import API_ID, API_HASH, SESSION_STRING
from telegram_client import register_handlers
from scheduler import start_scheduler
from database import init_db


# ==============================
# Logging
# ==============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ==============================
# Flask keep-alive server (for Render)
# ==============================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Telegram AI Userbot is running", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000, debug=False, use_reloader=False)


# ==============================
# Telegram Client
# ==============================

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)


# ==============================
# Main Async Entry Point
# ==============================

async def main():
    logger.info("Initializing database...")
    init_db()

    logger.info("Starting Telegram client...")
    await client.start()

    me = await client.get_me()
    logger.info(f"Logged in as: {me.first_name} (@{me.username})")

    logger.info("Registering message handlers...")
    register_handlers(client)

    logger.info("Starting APScheduler...")
    start_scheduler(client)

    logger.info("Userbot is now running and listening...")
    await client.run_until_disconnected()


# ==============================
# Safe Runner with Auto-Restart
# ==============================

if __name__ == "__main__":
    # Start Flask keep-alive in a background thread (for Render)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask keep-alive server started on port 10000")

    while True:
        try:
            asyncio.run(main())
        except FloodWaitError as e:
            logger.warning(f"Flood wait: sleeping for {e.seconds} seconds")
            asyncio.run(asyncio.sleep(e.seconds))
        except Exception as e:
            logger.exception(f"Fatal error: {e}")
            logger.info("Restarting in 10 seconds...")
            asyncio.run(asyncio.sleep(10))
