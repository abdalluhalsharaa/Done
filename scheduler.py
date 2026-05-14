# ==============================
# scheduler.py
# Background Scheduling (Daily Digest + Micro Summaries)
# ==============================

import os
import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import get_recent_messages
from summarizer import build_daily_structure, build_micro_summary

logger = logging.getLogger(__name__)

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

scheduler = AsyncIOScheduler()


# ==========================================
# Daily Digest Job (6 AM)
# ==========================================

async def daily_digest_job(client):

    try:
        logger.info("Running daily digest job...")

        messages = get_recent_messages(limit=1000)

        if not messages:
            return

        summary = await build_daily_structure(messages)

        await client.send_message(
            OWNER_ID,
            f"📊 Daily Digest (24h)\n\n{summary}"
        )

        logger.info("Daily digest sent")

    except Exception as e:
        logger.exception(f"Daily digest failed: {e}")


# ==========================================
# Micro Summary Job
# ==========================================

async def micro_summary_job(client):

    try:
        logger.info("Running micro-summary job...")

        messages = get_recent_messages(limit=50)

        if not messages:
            return

        await build_micro_summary(messages)

        logger.info("Micro-summary created")

    except Exception as e:
        logger.exception(f"Micro summary failed: {e}")


# ==========================================
# Start Scheduler
# ==========================================

def start_scheduler(client):

    # 6 AM daily digest
    scheduler.add_job(
        lambda: asyncio.create_task(daily_digest_job(client)),
        "cron",
        hour=6,
        minute=0
    )

    # every 30 minutes micro summary
    scheduler.add_job(
        lambda: asyncio.create_task(micro_summary_job(client)),
        "interval",
        minutes=30
    )

    scheduler.start()

    logger.info("Scheduler started successfully")
