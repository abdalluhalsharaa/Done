# ==========================================
# telegram_client.py
# Telegram Events + Commands + Monitoring
# ==========================================

import os
import logging
from telethon import events
from telethon.tl.types import PeerChannel
from dotenv import load_dotenv

from database import (
    save_message,
    get_recent_messages,
    get_mentions
)

from summarizer import (
    generate_summary,
    generate_catchup_summary
)

from ai_engine import (
    generate_context_explanation
)

load_dotenv()

logger = logging.getLogger(__name__)

# ==========================================
# Configuration
# ==========================================

TARGET_GROUP_ID = int(os.getenv("TARGET_GROUP_ID"))

OWNER_ID = int(os.getenv("OWNER_ID"))

MENTION_KEYWORDS = [
    "عبدالله",
    "عبدالله الشرع",
    "Abdullah"
]

# ==========================================
# Register Handlers
# ==========================================

def register_handlers(client):

    # ======================================
    # Group Message Listener
    # ======================================

    @client.on(events.NewMessage())
    async def group_message_handler(event):

        try:

            # Ignore private chats
            if event.is_private:
                return

            # Ignore other groups
            if not isinstance(event.message.peer_id, PeerChannel):
                return

            if event.chat_id != TARGET_GROUP_ID:
                return

            message_text = event.raw_text

            if not message_text:
                return

            sender = await event.get_sender()

            sender_name = (
                f"{sender.first_name or ''} "
                f"{sender.last_name or ''}"
            ).strip()

            sender_username = sender.username or "N/A"

            # ==================================
            # Save Message
            # ==================================

            save_message(
                sender_name=sender_name,
                sender_username=sender_username,
                message_text=message_text,
                timestamp=str(event.message.date)
            )

            logger.info(
                f"Saved message from {sender_name}"
            )

            # ==================================
            # Mention Detection
            # ==================================

            lowered = message_text.lower()

            for keyword in MENTION_KEYWORDS:

                if keyword.lower() in lowered:

                    logger.info(
                        f"Mention detected : {keyword}"
                    )

                    context = await generate_context_explanation(
                        message_text
                    )

                    alert_message = (
                        "🚨 Mention Detected\n\n"
                        f"👤 Sender : {sender_name}\n"
                        f"📝 Message :\n{message_text}\n\n"
                        f"🧠 Context :\n{context}"
                    )

                    await client.send_message(
                        OWNER_ID,
                        alert_message
                    )

                    break

        except Exception as e:
            logger.exception(
                f"Group Handler Error : {e}"
            )

    # ======================================
    # Private Commands
    # ======================================

    @client.on(events.NewMessage(
        from_users=OWNER_ID
    ))
    async def private_commands(event):

        try:

            if not event.is_private:
                return

            text = event.raw_text.strip()

            # ==================================
            # /summary
            # ==================================

            if text.startswith("/summary"):

                messages = get_recent_messages(
                    limit=150
                )

                summary = await generate_summary(
                    messages
                )

                await event.reply(
                    f"🧠 Summary :\n\n{summary}"
                )

            # ==================================
            # /catchup
            # ==================================

            elif text.startswith("/catchup"):

                messages = get_recent_messages(
                    limit=300
                )

                catchup = await generate_catchup_summary(
                    messages
                )

                await event.reply(
                    f"📌 Catch-up Report :\n\n{catchup}"
                )

            # ==================================
            # /mentions
            # ==================================

            elif text.startswith("/mentions"):

                mentions = get_mentions()

                if not mentions:

                    await event.reply(
                        "No mentions found recently."
                    )

                    return

                formatted = ""

                for item in mentions[-10:]:

                    formatted += (
                        f"👤 {item['sender_name']}\n"
                        f"📝 {item['message_text']}\n"
                        f"⏰ {item['timestamp']}\n\n"
                    )

                await event.reply(
                    f"🚨 Recent Mentions :\n\n{formatted}"
                )

            # ==================================
            # /help
            # ==================================

            elif text.startswith("/help"):

                help_text = (
                    "📚 Available Commands\n\n"
                    "/summary\n"
                    "/catchup\n"
                    "/mentions\n"
                    "/help"
                )

                await event.reply(help_text)

        except Exception as e:
            logger.exception(
                f"Private Command Error : {e}"
            )
