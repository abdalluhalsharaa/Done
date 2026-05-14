# ==========================================
# telegram_client.py
# Telegram Events + Dynamic Summary Commands
# ==========================================

import os
import logging
from datetime import datetime, timedelta

from telethon import events
from telethon.tl.types import PeerChannel

from database import (
    save_message,
    get_recent_messages
)

from summarizer import (
    generate_summary,
    generate_catchup_summary
)

from ai_engine import generate_context_explanation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TARGET_GROUP_ID = int(os.getenv("TARGET_GROUP_ID"))
OWNER_ID = int(os.getenv("OWNER_ID"))

MENTION_KEYWORDS = ["عبدالله", "عبدالله الشرع", "Abdullah"]


# ==========================================
# Helper: Parse summary input
# ==========================================

def parse_summary_argument(arg: str):
    """
    Supports:
    - 4h  -> last 4 hours
    - 200 -> last 200 messages
    - None -> default
    """

    if not arg:
        return {"type": "count", "value": 150}

    arg = arg.strip().lower()

    # Hours mode
    if arg.endswith("h"):
        try:
            hours = int(arg.replace("h", ""))
            return {"type": "hours", "value": hours}
        except:
            return {"type": "count", "value": 150}

    # Messages mode
    try:
        count = int(arg)
        return {"type": "count", "value": count}
    except:
        return {"type": "count", "value": 150}


# ==========================================
# Handler registration
# ==========================================

def register_handlers(client):

    @client.on(events.NewMessage())
    async def handler(event):

        try:
            if event.is_private:
                return

            if event.chat_id != TARGET_GROUP_ID:
                return

            text = event.raw_text or ""
            if not text:
                return

            sender = await event.get_sender()
            sender_name = (sender.first_name or "") + " " + (sender.last_name or "")

            # Save message
            save_message(
                sender_name=sender_name.strip(),
                sender_username=sender.username or "",
                message_text=text,
                timestamp=str(event.message.date)
            )

            # Mention detection
            lowered = text.lower()
            for k in MENTION_KEYWORDS:
                if k.lower() in lowered:

                    context = await generate_context_explanation(text)

                    await client.send_message(
                        OWNER_ID,
                        f"🚨 Mention\n\n{sender_name}\n{text}\n\nContext:\n{context}"
                    )
                    break


            # ==========================================
            # COMMAND: /summary dynamic
            # ==========================================

            if text.startswith("/summary"):

                parts = text.split(" ", 1)
                arg = parts[1] if len(parts) > 1 else None

                parsed = parse_summary_argument(arg)

                if parsed["type"] == "hours":

                    hours = parsed["value"]
                    cutoff = datetime.now() - timedelta(hours=hours)

                    messages = get_recent_messages(limit=2000)

                    filtered = [
                        m for m in messages
                        if datetime.fromisoformat(m["timestamp"]) >= cutoff
                    ]

                    summary = await generate_summary(filtered)

                else:

                    limit = parsed["value"]
                    messages = get_recent_messages(limit=limit)

                    summary = await generate_summary(messages)

                await event.reply(f"🧠 Summary\n\n{summary}")


            # ==========================================
            # COMMAND: /catchup
            # ==========================================

            elif text.startswith("/catchup"):

                messages = get_recent_messages(limit=300)
                summary = await generate_catchup_summary(messages)

                await event.reply(f"📌 Catch-up\n\n{summary}")


            # ==========================================
            # HELP
            # ==========================================

            elif text.startswith("/help"):

                await event.reply(
                    "/summary 4h\n"
                    "/summary 200\n"
                    "/catchup"
                )

        except Exception as e:
            logger.exception(f"Error: {e}")
