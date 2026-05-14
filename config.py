# ==============================
# config.py
# تحميل وإدارة الإعدادات المركزية
# ==============================

import os
import logging
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env (إذا كان موجوداً)
load_dotenv()

logger = logging.getLogger(__name__)


# ==========================================
# بيانات اعتماد Telegram
# ==========================================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")

if not API_ID or not API_HASH or not SESSION_STRING:
    raise ValueError("API_ID, API_HASH, أو SESSION_STRING مفقودة من متغيرات البيئة")


# ==========================================
# إعدادات المجموعة المستهدفة والمالك
# ==========================================

TARGET_GROUP_ID = int(os.getenv("TARGET_GROUP_ID", "0"))
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

if not TARGET_GROUP_ID or not OWNER_ID:
    raise ValueError("TARGET_GROUP_ID أو OWNER_ID مفقودة من متغيرات البيئة")


# ==========================================
# إعدادات الذكاء الاصطناعي (Gemini)
# ==========================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gemini-1.5-flash")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY مفقودة من متغيرات البيئة")


# ==========================================
# الكلمات المفتاحية للإشارات (Mentions)
# ==========================================

MENTION_KEYWORDS = [
    "عبدالله",
    "عبدالله الشرع",
    "Abdullah"
]


# ==========================================
# إعدادات المجدول (Scheduler)
# ==========================================

DAILY_DIGEST_HOUR = int(os.getenv("DAILY_DIGEST_HOUR", "6"))
DAILY_DIGEST_MINUTE = int(os.getenv("DAILY_DIGEST_MINUTE", "0"))
MICRO_SUMMARY_INTERVAL_MINUTES = int(os.getenv("MICRO_SUMMARY_INTERVAL_MINUTES", "30"))


# ==========================================
# إعدادات إضافية
# ==========================================

RECENT_MESSAGES_LIMIT = 1000
MICRO_MESSAGES_LIMIT = 50
SUMMARY_CHUNK_SIZE = 30

# رسالة تأكيد تحميل الإعدادات
logger.info("تم تحميل إعدادات config.py بنجاح")
