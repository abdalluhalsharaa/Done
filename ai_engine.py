# ==============================
# ai_engine.py
# Gemini / LLM Integration Layer
# ==============================

import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ==========================================
# API Key Setup
# ==========================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-1.5-flash"

model = genai.GenerativeModel(MODEL_NAME)


# ==========================================
# Core AI Call
# ==========================================

async def call_ai(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        logger.exception(f"AI call failed: {e}")
        return "AI service temporarily unavailable."


# ==========================================
# Context Explanation (Mentions)
# ==========================================

async def generate_context_explanation(message_text: str) -> str:
    prompt = f"""
Explain briefly the context of this Telegram message in 1-2 lines.

Message:
{message_text}

Keep it short and factual.
"""
    return await call_ai(prompt)


# ==========================================
# Summary Generator
# ==========================================

async def generate_summary(messages: list) -> str:
    text_block = "\n".join(
        f"{m['sender_name']}: {m['message_text']}"
        for m in messages[::-1]
    )

    prompt = f"""
Summarize this Telegram group conversation.

Rules:
- concise
- extract key ideas
- ignore spam
- focus on important information

Messages:
{text_block}
"""

    return await call_ai(prompt)


# ==========================================
# Catch-up Summary
# ==========================================

async def generate_catchup_summary(messages: list) -> str:
    text_block = "\n".join(
        f"{m['sender_name']}: {m['message_text']}"
        for m in messages[::-1]
    )

    prompt = f"""
Create a clean catch-up report:

- main topics
- important updates
- questions
- decisions

Messages:
{text_block}
"""

    return await call_ai(prompt)
