# ==============================
# summarizer.py
# Message Cleaning + Incremental Summaries
# ==============================

import logging
from ai_engine import call_ai
from database import save_summary, get_recent_summaries

logger = logging.getLogger(__name__)


# ==========================================
# Message Cleaning
# ==========================================

def clean_messages(messages: list) -> list:
    cleaned = []

    for m in messages:

        text = (m.get("message_text") or "").strip()

        if not text:
            continue

        if len(text) < 2:
            continue

        if text.lower() in ["sticker", "gif", "image"]:
            continue

        cleaned.append(m)

    return cleaned


# ==========================================
# Micro Summary Builder
# ==========================================

async def build_micro_summary(messages: list) -> str:

    messages = clean_messages(messages)

    text_block = "\n".join(
        f"{m['sender_name']}: {m['message_text']}"
        for m in messages[-30:]
    )

    prompt = f"""
You are a compression engine for Telegram chats.

Task:
- Summarize messages into compact memory
- Remove repetition and noise
- Keep only important points

Output: very short bullet points.

Messages:
{text_block}
"""

    summary = await call_ai(prompt)

    save_summary(summary)

    return summary


# ==========================================
# Daily Summary Builder
# ==========================================

async def build_daily_structure(messages: list) -> str:

    messages = clean_messages(messages)

    text_block = "\n".join(
        f"{m['sender_name']}: {m['message_text']}"
        for m in messages
    )

    prompt = f"""
Create a structured Telegram daily report:

Include:
- Main topics
- Important updates
- Questions
- Decisions
- Useful links

Messages:
{text_block}
"""

    return await call_ai(prompt)


# ==========================================
# Load Previous Memory
# ==========================================

def load_previous_summaries():

    return get_recent_summaries(limit=20)
