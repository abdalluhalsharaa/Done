# ==============================
# main.py
# Personal Telegram AI Userbot
# ==============================

import asyncio
import logging
import threading
import sys
import nest_asyncio
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

from config import API_ID, API_HASH, SESSION_STRING
from telegram_client import register_handlers
from scheduler import start_scheduler
from database import init_db

# تفعيل nest_asyncio للسماح بتشغيل عدة حلقات غير متزامنة
nest_asyncio.apply()

# ==============================
# إعدادات التسجيل (Logging)
# ==============================

logging.basicConfig(
    level=logging.DEBUG,  # تغيير إلى DEBUG للحصول على معلومات أكثر
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# التأكد من أن رسائل السجل تظهر فوراً
sys.stdout.reconfigure(line_buffering=True)

# ==============================
# خادم Flask (للابقاء على قيد الحياة)
# ==============================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Telegram AI Userbot is running", 200

def run_flask():
    """تشغيل خادم Flask في خيط منفصل"""
    try:
        logger.info("بدء تشغيل خادم Flask على المنفذ 10000...")
        flask_app.run(host="0.0.0.0", port=10000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"خطأ في خادم Flask: {e}")

# ==============================
# عميل Telegram
# ==============================

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# ==============================
# الوظيفة الرئيسية غير المتزامنة
# ==============================

async def main():
    """الوظيفة الرئيسية لتشغيل البوت"""
    logger.info("=== بدء تشغيل البوت ===")
    
    # فحص المتغيرات الأساسية
    logger.info(f"API_ID موجود: {'نعم' if API_ID else 'لا'}")
    logger.info(f"API_HASH موجود: {'نعم' if API_HASH else 'لا'}")
    logger.info(f"SESSION_STRING موجود: {'نعم' if SESSION_STRING else 'لا'}")
    logger.info(f"TARGET_GROUP_ID: {TARGET_GROUP_ID}")
    logger.info(f"OWNER_ID: {OWNER_ID}")
    
    # تهيئة قاعدة البيانات
    logger.info("تهيئة قاعدة البيانات...")
    init_db()
    
    # بدء تشغيل عميل Telegram
    logger.info("بدء تشغيل عميل Telegram...")
    await client.start()
    
    # جلب معلومات المستخدم للتحقق من نجاح الاتصال
    me = await client.get_me()
    logger.info(f"تم تسجيل الدخول بنجاح باسم: {me.first_name} (معرف المستخدم: {me.id})")
    
    # تسجيل معالجات الأحداث
    logger.info("تسجيل معالجات الأحداث...")
    register_handlers(client)
    
    # بدء تشغيل المجدول
    logger.info("بدء تشغيل المجدول (scheduler)...")
    start_scheduler(client)
    
    logger.info("✅ البوت يعمل الآن وبانتظار الأحداث...")
    
    # البقاء قيد التشغيل حتى يتم قطع الاتصال
    await client.run_until_disconnected()
    logger.warning("تم قطع اتصال البوت، سيتم إعادة التشغيل...")

# ==============================
# المدخل الرئيسي مع خاصية إعادة التشغيل التلقائي
# ==============================

if __name__ == "__main__":
    # بدء تشغيل خادم Flask في خيط منفصل
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("🚀 تم بدء تشغيل خادم Flask في خيط منفصل")
    
    # حلقة إعادة تشغيل البوت في حال حدوث أي خطأ
    while True:
        try:
            # إنشاء حلقة أحداث جديدة لكل محاولة
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
            loop.close()
        except FloodWaitError as e:
            logger.warning(f"تم اكتشاف FloodWait: الانتظار لمدة {e.seconds} ثانية...")
            time.sleep(e.seconds)
        except KeyboardInterrupt:
            logger.info("تم إيقاف البوت بواسطة المستخدم")
            break
        except Exception as e:
            logger.exception(f"خطأ فادح: {e}")
            logger.info("⚠️ سيتم إعادة تشغيل البوت بعد 10 ثوانٍ...")
            import time
            time.sleep(10)

# ==============================
# نهاية الملف
# ==============================
