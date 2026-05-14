# ==========================================
# telegram_client.py
# Telegram Events + Dynamic Summary Commands
# ==========================================

import logging
from datetime import datetime, timedelta

from telethon import events

from config import TARGET_GROUP_ID, OWNER_ID, MENTION_KEYWORDS
from database import save_message, get_recent_messages, get_messages_since
from summarizer import generate_summary, generate_catchup_summary
from ai_engine import generate_context_explanation

logger = logging.getLogger(__name__)


# ==========================================
# Helper: Parse summary input
# ==========================================

def parse_summary_argument(arg: str):
    """
    Supports:
    - 4h  -> last 4 hours
    - 200 -> last 200 messages
    - None -> default 150 messages
    """
    if not arg:
        return {"type": "count", "value": 150}

    arg = arg.strip().lower()

    if arg.endswith("h"):
        try:
            hours = int(arg[:-1])  # remove 'h'
            return {"type": "hours", "value": hours}
        except ValueError:
            return {"type": "count", "value": 150}

    try:
        count = int(arg)
        return {"type": "count", "value": count}
    except ValueError:
        return {"type": "count", "value": 150}


# ==========================================
# Handler registration
# ==========================================

def register_handlers(client):

    @client.on(events.NewMessage())
    async def handler(event):
        try:
            # Ignore private chats and wrong groups
            if event.is_private:
                return
            if event.chat_id != TARGET_GROUP_ID:
                return

            text = event.raw_text or ""
            if not text:
                return

            sender = await event.get_sender()
            sender_name = (sender.first_name or "") + " " + (sender.last_name or "")
            sender_name = sender_name.strip() or "Unknown"

            # Save message with ISO timestamp
            save_message(
                sender_name=sender_name,
                sender_username=sender.username or "",
                message_text=text,
                timestamp=event.message.date.isoformat()
            )

            # Mention detection
            lowered = text.lower()
            for keyword in MENTION_KEYWORDS:
                if keyword.lower() in lowered:
                    context = await generate_context_explanation(text)
                    await client.send_message(
                        OWNER_ID,
                        f"🚨 **Mention detected**\n\n"
                        f"**From:** {sender_name}\n"
                        f"**Message:** {text}\n\n"
                        f"**Context:** {context}"
                    )
                    break

            # ------------------------------------------
            # COMMAND: /summary [time|count]
            # ------------------------------------------
            if text.startswith("/summary"):
                parts = text.split(maxsplit=1)
                arg = parts[1] if len(parts) > 1 else None
                parsed = parse_summary_argument(arg)

                if parsed["type"] == "hours":
                    hours = parsed["value"]
                    cutoff = datetime.now() - timedelta(hours=hours)
                    messages = get_messages_since(cutoff)
                    if not messages:
                        await event.reply(f"📭 No messages in the last {hours} hour(s).")
                        return
                    summary = await generate_summary(messages)
                else:
                    limit = parsed["value"]
                    messages = get_recent_messages(limit=limit)
                    if not messages:
                        await event.reply(f"📭 No messages found (limit {limit}).")
                        return
                    summary = await generate_summary(messages)

                await event.reply(f"🧠 **Summary**\n\n{summary}")

            # ------------------------------------------
            # COMMAND: /catchup
            # ------------------------------------------
            elif text.startswith("/catchup"):
                messages = get_recent_messages(limit=300)
                if not messages:
                    await event.reply("📭 Not enough messages to catch up.")
                    return
                summary = await generate_catchup_summary(messages)
                await event.reply(f"📌 **Catch-up**\n\n{summary}")

            # ------------------------------------------
            # COMMAND: /help
            # ------------------------------------------
            elif text.startswith("/help"):
                await event.reply(
                    "📖 **Available commands**\n\n"
                    "/summary         → last 150 messages\n"
                    "/summary 200     → last 200 messages\n"
                    "/summary 4h      → last 4 hours\n"
                    "/catchup         → summary of last ~300 messages\n"
                    "/help            → this message"
                )

        except Exception as e:
            logger.exception(f"Error in message handler: {e}")
