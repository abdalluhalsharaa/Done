# ==============================
# summarizer.py
# Message Cleaning + Structured Summaries
# ==============================

import logging
from ai_engine import call_ai
from database import save_summary, get_recent_summaries

logger = logging.getLogger(__name__)


def clean_messages(messages: list) -> list:
    """Remove empty, too-short, and media-only messages."""
    cleaned = []
    for m in messages:
        text = (m.get("message_text") or "").strip()
        if not text or len(text) < 2:
            continue
        if text.lower() in ("sticker", "gif", "image", "video", "file"):
            continue
        cleaned.append(m)
    return cleaned


async def build_micro_summary(messages: list) -> str:
    """
    Compress a small batch of messages (e.g., last 30) into a micro summary.
    Saves it to the database for future reference.
    """
    messages = clean_messages(messages)
    if not messages:
        return ""

    # Use last 30 or fewer
    recent = messages[-30:]
    text_block = "\n".join(f"{m['sender_name']}: {m['message_text']}" for m in recent)

    prompt = f"""
You are a chat compression engine. Summarize the following messages into very short bullet points (max 5 points).
Remove repetition and noise. Keep only important information.

Messages:
{text_block}
"""
    summary = await call_ai(prompt)
    if summary and "unavailable" not in summary.lower():
        save_summary(summary)
    return summary


async def build_daily_structure(messages: list) -> str:
    """
    Generate a structured daily report for the last 24h.
    """
    messages = clean_messages(messages)
    if not messages:
        return "No meaningful messages in the last 24 hours."

    text_block = "\n".join(f"{m['sender_name']}: {m['message_text']}" for m in messages)

    prompt = f"""
Create a structured daily report from this Telegram chat.

Include sections:
- Main Topics
- Important Updates / Announcements
- Questions Asked
- Decisions Made
- Useful Links (if any)

Messages:
{text_block}

Output in clear markdown with headings and bullet points.
"""
    return await call_ai(prompt)


def load_previous_summaries(limit=20):
    """Load past summaries for context (if needed)."""
    return get_recent_summaries(limit=limit)
