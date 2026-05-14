# ==============================
# ai_engine.py
# Gemini Async Wrapper (non-blocking)
# ==============================

import asyncio
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY, AI_MODEL

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(AI_MODEL)


async def call_ai(prompt: str) -> str:
    """
    Non-blocking AI call using asyncio.to_thread.
    """
    try:
        # Run the synchronous Gemini call in a separate thread
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text.strip()
    except Exception as e:
        logger.exception(f"AI call failed: {e}")
        return "⚠️ AI service temporarily unavailable."


async def generate_context_explanation(message_text: str) -> str:
    prompt = f"""
Explain briefly the context of this Telegram message in 1-2 sentences.

Message:
{message_text}

Keep it short and factual, no extra commentary.
"""
    return await call_ai(prompt)


async def generate_summary(messages: list) -> str:
    if not messages:
        return "No messages to summarize."

    # Build conversation in chronological order (oldest first)
    text_block = "\n".join(
        f"{m['sender_name']}: {m['message_text']}"
        for m in messages  # messages are already oldest-first from DB if we use get_messages_since
    )

    prompt = f"""
You are a Telegram conversation summarizer. Summarize the following group chat.

Rules:
- Be concise, extract key ideas and decisions.
- Ignore spam, stickers, and trivial messages.
- Focus on important information, questions, and updates.

Messages:
{text_block}

Output a clean, bullet-point style summary (3-7 points).
"""
    return await call_ai(prompt)


async def generate_catchup_summary(messages: list) -> str:
    if not messages:
        return "No messages to catch up on."

    text_block = "\n".join(
        f"{m['sender_name']}: {m['message_text']}"
        for m in messages
    )

    prompt = f"""
Create a catch-up report from this Telegram conversation.

Include:
- Main topics discussed
- Important updates or announcements
- Any questions asked that remain unanswered
- Decisions made

Messages:
{text_block}

Output as short paragraphs or bullet points, no fluff.
"""
    return await call_ai(prompt)
