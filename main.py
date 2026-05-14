# ==============================
# main.py
# Personal Telegram AI Userbot
# ==============================

import asyncio
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from dotenv import load_dotenv
import os

from telegram_client import register_handlers
from scheduler import start_scheduler
from database import init_db


# ==============================
# Load Environment Variables
# ==============================

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")


# ==============================
# Logging
# ==============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==============================
# Telegram Client
# ==============================

client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH
)


# ==============================
# Main App
# ==============================

async def main():
    logger.info("Initializing database...")

    init_db()

    logger.info("Starting Telegram client...")

    await client.start()

    me = await client.get_me()

    logger.info(f"Logged in as : {me.first_name}")

    logger.info("Registering handlers...")

    register_handlers(client)

    logger.info("Starting scheduler...")

    start_scheduler(client)

    logger.info("Userbot is now running...")

    await client.run_until_disconnected()


# ==============================
# Safe Runner
# ==============================

if __name__ == "__main__":

    while True:

        try:
            asyncio.run(main())

        except FloodWaitError as e:
            logger.warning(
                f"FloodWait detected : sleeping for {e.seconds} seconds"
            )

            asyncio.sleep(e.seconds)

        except Exception as e:
            logger.exception(f"Fatal Error : {e}")

            logger.info("Restarting in 10 seconds...")

            asyncio.sleep(10)
