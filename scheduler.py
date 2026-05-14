# ==============================
# scheduler.py
# APScheduler for Daily Digest + Micro Summaries
# ==============================

import os
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import OWNER_ID, DAILY_DIGEST_HOUR, DAILY_DIGEST_MINUTE, MICRO_SUMMARY_INTERVAL_MINUTES
from database import get_messages_since, get_recent_messages
from summarizer import build_daily_structure, build_micro_summary

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def daily_digest_job(client):
    """Send a daily summary of the last 24 hours to the owner."""
    try:
        logger.info("Running daily digest job...")
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(hours=24)
        messages = get_messages_since(cutoff)

        if not messages:
            logger.info("No messages in the last 24h, skipping digest.")
            return

        summary = await build_daily_structure(messages)
        await client.send_message(OWNER_ID, f"📊 **Daily Digest (last 24h)**\n\n{summary}")
        logger.info("Daily digest sent.")
    except Exception as e:
        logger.exception(f"Daily digest failed: {e}")


async def micro_summary_job(client):
    """Generate a micro summary from last ~50 messages and store it."""
    try:
        logger.info("Running micro-summary job...")
        messages = get_recent_messages(limit=50)
        if not messages:
            return

        await build_micro_summary(messages)
        logger.info("Micro-summary created and saved.")
    except Exception as e:
        logger.exception(f"Micro summary failed: {e}")


def start_scheduler(client):
    """Add jobs and start the scheduler."""
    # Daily digest at configured time
    scheduler.add_job(
        lambda: asyncio.create_task(daily_digest_job(client)),
        "cron",
        hour=DAILY_DIGEST_HOUR,
        minute=DAILY_DIGEST_MINUTE,
        id="daily_digest"
    )

    # Micro summary every N minutes
    scheduler.add_job(
        lambda: asyncio.create_task(micro_summary_job(client)),
        "interval",
        minutes=MICRO_SUMMARY_INTERVAL_MINUTES,
        id="micro_summary"
    )

    scheduler.start()
    logger.info(f"Scheduler started. Daily digest at {DAILY_DIGEST_HOUR}:{DAILY_DIGEST_MINUTE}, "
                f"micro summary every {MICRO_SUMMARY_INTERVAL_MINUTES} min.")
