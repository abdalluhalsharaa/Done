# ==========================================
# telegram_client.py
# معالج الأحداث والأوامر
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
# دالة تحليل وسيط الأمر /summary
# ==========================================

def parse_summary_argument(arg: str):
    """
    تدعم الصيغ التالية:
    - 4h  -> آخر 4 ساعات
    - 200 -> آخر 200 رسالة
    - None -> الوضع الافتراضي (150 رسالة)
    """
    if not arg:
        return {"type": "count", "value": 150}

    arg = arg.strip().lower()

    if arg.endswith("h"):
        try:
            hours = int(arg[:-1])
            return {"type": "hours", "value": hours}
        except ValueError:
            return {"type": "count", "value": 150}

    try:
        count = int(arg)
        return {"type": "count", "value": count}
    except ValueError:
        return {"type": "count", "value": 150}

# ==========================================
# تسجيل معالجات الأحداث
# ==========================================

def register_handlers(client):
    """تسجيل جميع معالجات الأحداث في العميل"""
    
    @client.on(events.NewMessage)
    async def handler(event):
        """معالج الرسائل الجديدة"""
        try:
            # تجاهل المحادثات الخاصة والمجموعات الأخرى
            if event.is_private:
                return
            if event.chat_id != TARGET_GROUP_ID:
                return

            text = event.raw_text or ""
            if not text:
                return

            # تسجيل استلام الأمر للتحقق
            if text.startswith("/"):
                logger.info(f"تم استلام أمر: {text}")

            # الحصول على معلومات المرسل
            sender = await event.get_sender()
            sender_name = (sender.first_name or "") + " " + (sender.last_name or "")
            sender_name = sender_name.strip() or "Unknown"

            # حفظ الرسالة في قاعدة البيانات
            save_message(
                sender_name=sender_name,
                sender_username=sender.username or "",
                message_text=text,
                timestamp=event.message.date.isoformat()
            )

            # التحقق من ذكر اسم المالك
            lowered = text.lower()
            for keyword in MENTION_KEYWORDS:
                if keyword.lower() in lowered:
                    context = await generate_context_explanation(text)
                    await client.send_message(
                        OWNER_ID,
                        f"🚨 **تم ذكر اسمك**\n\n"
                        f"**المرسل:** {sender_name}\n"
                        f"**الرسالة:** {text}\n\n"
                        f"**السياق:** {context}"
                    )
                    break

            # ------------------------------------------
            # الأمر: /summary [عدد|ساعات]
            # ------------------------------------------
            if text.startswith("/summary"):
                parts = text.split(maxsplit=1)
                arg = parts[1] if len(parts) > 1 else None
                parsed = parse_summary_argument(arg)

                logger.info(f"تنفيذ الأمر /summary بنوع: {parsed['type']} بقيمة: {parsed['value']}")

                if parsed["type"] == "hours":
                    hours = parsed["value"]
                    cutoff = datetime.now() - timedelta(hours=hours)
                    messages = get_messages_since(cutoff)
                    if not messages:
                        await event.reply(f"📭 لا توجد رسائل في آخر {hours} ساعة.")
                        return
                    summary = await generate_summary(messages)
                else:
                    limit = parsed["value"]
                    messages = get_recent_messages(limit=limit)
                    if not messages:
                        await event.reply(f"📭 لم يتم العثور على رسائل (العدد المطلوب: {limit}).")
                        return
                    summary = await generate_summary(messages)

                await event.reply(f"🧠 **الملخص**\n\n{summary}")
                logger.info("تم إرسال الرد على الأمر /summary بنجاح")

            # ------------------------------------------
            # الأمر: /catchup
            # ------------------------------------------
            elif text.startswith("/catchup"):
                logger.info("تنفيذ الأمر /catchup")
                messages = get_recent_messages(limit=300)
                if not messages:
                    await event.reply("📭 لا توجد رسائل كافية للتعويض.")
                    return
                summary = await generate_catchup_summary(messages)
                await event.reply(f"📌 **تعويق**\n\n{summary}")
                logger.info("تم إرسال الرد على الأمر /catchup بنجاح")

            # ------------------------------------------
            # الأمر: /help
            # ------------------------------------------
            elif text.startswith("/help"):
                await event.reply(
                    "📖 **الأوامر المتاحة**\n\n"
                    "/summary         → آخر 150 رسالة\n"
                    "/summary 200     → آخر 200 رسالة\n"
                    "/summary 4h      → آخر 4 ساعات\n"
                    "/catchup         → ملخص آخر 300 رسالة تقريباً\n"
                    "/help            → هذه الرسالة"
                )

        except Exception as e:
            logger.exception(f"خطأ في معالج الرسائل: {e}")
            try:
                await event.reply("⚠️ حدث خطأ أثناء معالجة طلبك.")
            except:
                pass
