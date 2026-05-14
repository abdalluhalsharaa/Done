# ==============================
# config.py
# Central Configuration Loader (with validation)
# ==============================

import os
from dotenv import load_dotenv

load_dotenv()


# ==========================================
# Telegram Credentials
# ==========================================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION_STRING:
    raise ValueError("Missing API_ID, API_HASH, or SESSION_STRING in environment")


# ==========================================
# Target Settings
# ==========================================

TARGET_GROUP_ID = int(os.getenv("TARGET_GROUP_ID", "0"))
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

if not TARGET_GROUP_ID or not OWNER_ID:
    raise ValueError("Missing TARGET_GROUP_ID or OWNER_ID in environment")


# ==========================================
# AI Settings
# ==========================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gemini-1.5-flash")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in environment")


# ==========================================
# Mention Keywords (customizable)
# ==========================================

MENTION_KEYWORDS = [
    "عبدالله",
    "عبدالله الشرع",
    "Abdullah"
]


# ==========================================
# Scheduler Settings
# ==========================================

DAILY_DIGEST_HOUR = int(os.getenv("DAILY_DIGEST_HOUR", "6"))
DAILY_DIGEST_MINUTE = int(os.getenv("DAILY_DIGEST_MINUTE", "0"))
MICRO_SUMMARY_INTERVAL_MINUTES = int(os.getenv("MICRO_SUMMARY_INTERVAL_MINUTES", "30"))


# ==========================================
# Limits & Defaults
# ==========================================

RECENT_MESSAGES_LIMIT = 1000
MICRO_MESSAGES_LIMIT = 50
SUMMARY_CHUNK_SIZE = 30
