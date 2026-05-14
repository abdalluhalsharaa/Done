# ==============================
# config.py
# Central Configuration Loader
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


# ==========================================
# Target Settings
# ==========================================

TARGET_GROUP_ID = int(os.getenv("TARGET_GROUP_ID", "0"))
OWNER_ID = int(os.getenv("OWNER_ID", "0"))


# ==========================================
# AI Settings
# ==========================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gemini-1.5-flash")


# ==========================================
# Mention Keywords
# ==========================================

MENTION_KEYWORDS = [
    "عبدالله",
    "عبدالله الشرع",
    "Abdullah"
]


# ==========================================
# Scheduler Settings
# ==========================================

DAILY_DIGEST_HOUR = 6
DAILY_DIGEST_MINUTE = 0

MICRO_SUMMARY_INTERVAL_MINUTES = 30


# ==========================================
# Limits
# ==========================================

RECENT_MESSAGES_LIMIT = 1000
MICRO_MESSAGES_LIMIT = 50
SUMMARY_CHUNK_SIZE = 30
