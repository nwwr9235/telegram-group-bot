#!/usr/bin/env python3
"""
بوت تيليجرام - النسخة الكاملة
"""
import logging
import sys
import os
import asyncio

# إعداد Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("🚀 BOT IS STARTING...")
logger.info("=" * 60)

# ✅ استيراد الإعدادات
try:
    from bot.config.settings import settings
    logger.info(f"✅ Settings loaded")
    logger.info(f"   WEBHOOK_HOST: {settings.WEBHOOK_HOST or 'EMPTY'}")
    logger.info(f"   IS_WEBHOOK_MODE: {settings.IS_WEBHOOK_MODE}")
except Exception as e:
    logger.error(f"❌ Settings error: {e}")
    sys.exit(1)

# ✅ استيراد aiogram
try:
    from aiogram import Bot, Dispatcher, F
    from aiogram.types import Message
    from aiogram.filters import Command
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from aiohttp import web
    logger.info("✅ Aiogram imported")
except Exception as e:
    logger.error(f"❌ Aiogram error: {e}")
    sys.exit(1)

# ✅ إنشاء البوت
bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()
logger.info("✅ Bot created")

# ✅ ========== HANDLERS ==========

# /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply(
        "👋 <b>أهلاً بك في بوت إدارة المجموعات!</b>\n\n"
        "🤖 <b>الأوامر المتاحة:</b>\n"
        "• حظر - حظر مستخدم (بالرد)\n"
        "• كتم - كتم مستخدم (بالرد)\n"
        "• انذار - إنذار مستخدم (بالرد)\n"
        "• طرد - طرد مستخدم (بالرد)\n"
        "• تثبيت - تثبيت رسالة (بالرد)\n"
        "• حذف - حذف رسالة (بالرد)\n\n"
        "⚡️ أضفني إلى مجموعتك وارفعني مشرفاً!",
        parse_mode="HTML"
    )

# /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "📖 <b>دليل الاستخدام:</b>\n\n"
        "<b>🛡️ أوامر الإدارة:</b>\n"
        "• حظر (بالرد) - حظر المستخدم\n"
        "• فك حظر (بالرد) - إلغاء الحظر\n"
        "• كتم (بالرد) - كتم المستخدم\n"
        "• فك كتم (بالرد) - إلغاء الكتم\n"
        "• انذار سبب (بالرد) - إنذار\n"
        "• حذف انذار (بالرد) - حذف الإنذارات\n"
        "• طرد (بالرد) - طرد المستخدم\n"
        "• تثبيت (بالرد) - تثبيت رسالة\n"
        "• الغاء تثبيت - إلغاء التثبيت\n"
        "• حذف (بالرد) - حذف رسالة\n"
        "• تنظيف 50 (بالرد) - حذف رسائل\n"
        "• مشرف (بالرد) - رفع مشرف\n"
        "• تنزيل (بالرد) - تنزيل مشرف",
        parse_mode="HTML"
    )

# ✅ أوامر المشرفين (بدون /)
from aiogram.enums import ChatMemberStatus

async def is_admin(message: Message) -> bool:
    """التحقق إذا كان المستخدم مشرفاً"""
    if message.chat.type == "private":
        return message.from_user.id == settings.ADMIN_ID
    
    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]

# حظر
@dp.message(lambda msg: msg.text and msg.text.lower().startswith("حظر"))
async def ban_user(message: Message):
    if not await is_admin(message):
        return await message.reply("⛔ للمشرفين فقط!")
    
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name
        await bot.ban_chat_member(message.chat.id, user_id)
        await message.reply(f"🚫 تم حظر {user_name}")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

# كتم
@dp.message(lambda msg: msg.text and msg.text.lower().startswith("كتم"))
async def mute_user(message: Message):
    if not await is_admin(message):
        return await message.reply("⛔ للمشرفين فقط!")
    
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        from aiogram.types import ChatPermissions
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name
        
        # كتم لمدة ساعة افتراضياً
        until = int(asyncio.get_event_loop().time()) + 3600
        
        await bot.restrict_chat_member(
            message.chat.id, user_id,
            until_date=until,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.reply(f"🔇 تم كتم {user_name} لمدة ساعة")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

# فك كتم
@dp.message(lambda msg: msg.text and msg.text.lower().startswith("فك كتم"))
async def unmute_user(message: Message):
    if not await is_admin(message):
        return await message.reply("⛔ للمشرفين فقط!")
    
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        from aiogram.types import ChatPermissions
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name
        
        await bot.restrict_chat_member(
            message.chat.id, user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True
            )
        )
        await message.reply(f"🔊 تم فك كتم {user_name}")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

# طرد
@dp.message(lambda msg: msg.text and msg.text.lower().startswith("طرد"))
async def kick_user(message: Message):
    if not await is_admin(message):
        return await message.reply("⛔ للمشرفين فقط!")
    
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name
        
        await bot.ban_chat_member(message.chat.id, user_id)
        await asyncio.sleep(0.5)
        await bot.unban_chat_member(message.chat.id, user_id)
        
        await message.reply(f"👢 تم طرد {user_name}")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

# تثبيت
@dp.message(lambda msg: msg.text and msg.text.lower().startswith("تثبيت"))
async def pin_message(message: Message):
    if not await is_admin(message):
        return await message.reply("⛔ للمشرفين فقط!")
    
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على الرسالة للتثبيت")
    
    try:
        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        await message.reply("📌 تم التثبيت")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

# إلغاء تثبيت
@dp.message(lambda msg: msg.text and msg.text.lower().startswith("الغاء تثبيت"))
async def unpin_message(message: Message):
    if not await is_admin(message):
        return await message.reply("⛔ للمشرفين فقط!")
    
    try:
        await bot.unpin_all_chat_messages(message.chat.id)
        await message.reply("📌 تم إلغاء التثبيت")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

# حذف
@dp.message(lambda msg: msg.text and msg.text.lower().startswith("حذف"))
async def delete_message(message: Message):
    if not await is_admin(message):
        return await message.reply("⛔ للمشرفين فقط!")
    
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على الرسالة للحذف")
    
    try:
        await bot.delete_message(message.chat.id, message.reply_to_message.message_id)
        await message.delete()
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

logger.info("✅ Handlers registered")

# ✅ ========== WEB SERVER ==========

app = web.Application()

async def health(request):
    return web.Response(text="OK", status=200)

app.router.add_get("/health", health)
logger.info("✅ Health endpoint added")

# ✅ ========== STARTUP & SHUTDOWN ==========

async def on_startup():
    logger.info("🔄 on_startup")
    if settings.IS_WEBHOOK_MODE:
        try:
            await bot.set_webhook(settings.WEBHOOK_URL)
            logger.info(f"✅ Webhook: {settings.WEBHOOK_URL}")
        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")

async def on_shutdown():
    logger.info("🛑 on_shutdown")
    await bot.delete_webhook()

# ✅ ========== RUN ==========

if settings.IS_WEBHOOK_MODE:
    logger.info("🔧 Webhook mode")
    
    # ← 1. سجل الأحداث أولاً
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # ← 2. ثم أنشئ الـ Handler
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=settings.WEBHOOK_PATH)
    
    # ← 3. أخيراً اربط التطبيق (بعد تسجيل كل شيء)
    setup_application(app, dp, bot=bot)
    
    logger.info(f"🌐 Starting on port {settings.PORT}")
    web.run_app(app, host="0.0.0.0", port=settings.PORT)
else:
    logger.info("🔧 Polling mode")
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    asyncio.run(dp.start_polling(bot))
