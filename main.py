#!/usr/bin/env python3
# main.py - نسخة مُصحّحة ومنظمة
import asyncio
import logging
import sys
import os

# إعداد Logging أولاً
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ✅ طباعة أولية للتشخيص (قبل أي استيراد)
logger.info("=" * 60)
logger.info("🚀 BOT STARTING...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Files in directory: {os.listdir('.')}")
logger.info("=" * 60)

# ✅ استيراد الإعدادات مع معالجة الأخطاء
try:
    from bot.config.settings import settings
    logger.info(f"✅ Settings loaded")
    logger.info(f"   BOT_TOKEN exists: {bool(settings.BOT_TOKEN)}")
    logger.info(f"   ADMIN_ID: {settings.ADMIN_ID}")
    logger.info(f"   WEBHOOK_HOST: {settings.WEBHOOK_HOST}")
except Exception as e:
    logger.error(f"❌ Failed to load settings: {e}")
    sys.exit(1)

# ✅ استيراد aiogram
try:
    from aiogram import Bot, Dispatcher
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from aiohttp import web
    logger.info("✅ Aiogram loaded")
except Exception as e:
    logger.error(f"❌ Failed to import aiogram: {e}")
    sys.exit(1)

# ✅ استيراد Handlers
try:
    from bot.handlers import (
        commands_router,
        admin_text_router,
        captcha_router,
        owner_router,
        group_events_router
    )
    logger.info("✅ Handlers loaded")
except Exception as e:
    logger.error(f"❌ Failed to import handlers: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ✅ استيراد Database (اختياري - لا يوقف البوت)
try:
    from bot.database.connection import init_db, close_db
    logger.info("✅ Database module loaded")
    DB_AVAILABLE = True
except Exception as e:
    logger.warning(f"⚠️ Database module failed: {e}")
    DB_AVAILABLE = False

# إنشاء البوت والـ Dispatcher
bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# تسجيل الـ Routers
dp.include_router(commands_router)
dp.include_router(admin_text_router)
dp.include_router(captcha_router)
dp.include_router(group_events_router)
dp.include_router(owner_router)
logger.info("✅ Routers registered")


async def init_database():
    """تهيئة قاعدة البيانات في الخلفية"""
    if not DB_AVAILABLE:
        logger.warning("⚠️ Database not available, skipping")
        return
    
    try:
        await init_db()
        logger.info("✅ Database connected")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")


async def on_startup():
    """تشغيل عند بدء البوت"""
    logger.info("🔄 on_startup called...")
    
    # بدء DB في الخلفية
    asyncio.create_task(init_database())
    
    if settings.IS_WEBHOOK_MODE:
        try:
            await bot.set_webhook(settings.WEBHOOK_URL)
            logger.info(f"✅ Webhook set: {settings.WEBHOOK_URL}")
        except Exception as e:
            logger.error(f"❌ Failed to set webhook: {e}")
    
    # إشعار المطور
    try:
        await bot.send_message(
            settings.ADMIN_ID,
            "🤖 <b>Bot Started!</b>\nMode: " + ("Webhook" if settings.IS_WEBHOOK_MODE else "Polling"),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Could not notify admin: {e}")


async def on_shutdown():
    """تشغيل عند الإيقاف"""
    logger.info("🛑 Shutting down...")
    if DB_AVAILABLE:
        try:
            await close_db()
        except:
            pass
    await bot.delete_webhook()


def main():
    """الدالة الرئيسية"""
    logger.info("🎯 main() called")
    
    # إنشاء تطبيق aiohttp
    app = web.Application()
    
    # Health check endpoint (الأهم!)
    async def health_check(request):
        logger.info(f"Health check requested from {request.remote}")
        return web.Response(text="OK", status=200)
    
    app.router.add_get("/health", health_check)
    logger.info("✅ Health check endpoint registered at /health")
    
    # Webhook mode
    if settings.IS_WEBHOOK_MODE:
        logger.info("🔧 Configuring Webhook mode...")
        
        webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_handler.register(app, path=settings.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        logger.info(f"🌐 Starting server on 0.0.0.0:{settings.PORT}")
        logger.info(f"   Health: http://localhost:{settings.PORT}/health")
        logger.info(f"   Webhook: {settings.WEBHOOK_URL}")
        
        # تشغيل السيرفر
        web.run_app(app, host="0.0.0.0", port=settings.PORT)
    
    else:
        # Polling mode (للتطوير)
        logger.info("🔧 Starting in Polling mode...")
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()

