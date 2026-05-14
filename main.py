# main.py - مسؤول فقط عن تشغيل بوت Telethon
import asyncio
import logging
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from config import API_ID, API_HASH, SESSION_STRING
from telegram_client import register_handlers
from scheduler import start_scheduler
from database import init_db

logging.basicConfig(
    level=logging.DEBUG,  # مستوى DEBUG لتفاصيل أكثر
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def main():
    logger.info("بدء تشغيل بوت Telegram...")
    init_db()
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    me = await client.get_me()
    logger.info(f"تم تسجيل الدخول باسم: {me.first_name} (@{me.username})")
    register_handlers(client)
    start_scheduler(client)
    logger.info("البوت يعمل الآن.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except FloodWaitError as e:
            logger.warning(f"تم فرض انتظار من Telegram لمدة {e.seconds} ثانية.")
            asyncio.run(asyncio.sleep(e.seconds))
        except Exception as e:
            logger.exception(f"حدث خطأ غير متوقع: {e}. إعادة التشغيل بعد 10 ثوانٍ...")
            asyncio.run(asyncio.sleep(10))
