# scheduler.py
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import OWNER_ID, DAILY_DIGEST_HOUR, DAILY_DIGEST_MINUTE
from database import get_messages_since
from summarizer import build_daily_structure

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def daily_digest_job(client):
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(hours=24)
    messages = get_messages_since(cutoff)
    if messages:
        summary = await build_daily_structure(messages)
        await client.send_message(OWNER_ID, f"📊 **تقرير اليوم**\n\n{summary}")

def start_scheduler(client):
    scheduler.add_job(lambda: asyncio.create_task(daily_digest_job(client)), 'cron', hour=DAILY_DIGEST_HOUR, minute=DAILY_DIGEST_MINUTE)
    scheduler.start()
    logger.info(f"تم جدولة التقرير اليومي في {DAILY_DIGEST_HOUR}:{DAILY_DIGEST_MINUTE}")
