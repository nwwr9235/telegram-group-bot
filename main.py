# main.py
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.config.settings import settings
from bot.database.connection import init_db, close_db
from bot.handlers import (
    commands_router,
    admin_text_router,
    captcha_router,
    owner_router,
    group_events_router
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# تسجيل الـ Routers
dp.include_router(commands_router)
dp.include_router(admin_text_router)
dp.include_router(captcha_router)
dp.include_router(group_events_router)
dp.include_router(owner_router)


async def init_database():
    """تهيئة قاعدة البيانات في الخلفية"""
    try:
        await init_db()
        logger.info("✅ Database connected")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")


async def on_startup():
    """تشغيل عند بدء البوت"""
    logger.info("🚀 Starting bot...")
    
    # ✅ بدء DB في الخلفية (لا تنتظرها)
    asyncio.create_task(init_database())
    
    if settings.IS_WEBHOOK_MODE:
        await bot.set_webhook(settings.WEBHOOK_URL)
        logger.info(f"✅ Webhook set: {settings.WEBHOOK_URL}")
    
    # إشعار المطور (اختياري)
    try:
        await bot.send_message(
            settings.ADMIN_ID,
            f"🤖 <b>Bot Started!</b>\nMode: Webhook",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Could not notify admin: {e}")


async def on_shutdown():
    """تشغيل عند الإيقاف"""
    logger.info("🛑 Shutting down...")
    try:
        await close_db()
    except:
        pass
    await bot.delete_webhook()


def main():
    # ✅ إنشاء تطبيق aiohttp أولاً
    app = web.Application()
    
    # ✅ Health check endpoint (يجب أن يكون متاحاً فوراً!)
    async def health_check(request):
        return web.Response(text="OK", status=200)
    
    app.router.add_get("/health", health_check)
    
    # ✅ تسجيل Webhook handler
    if settings.IS_WEBHOOK_MODE:
        webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_handler.register(app, path=settings.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        logger.info(f"🌐 Starting server on port {settings.PORT}")
        logger.info(f"🔗 Health check: http://localhost:{settings.PORT}/health")
        logger.info(f"🔗 Webhook: {settings.WEBHOOK_URL}")
        
        # ✅ تشغيل السيرفر فوراً
        web.run_app(app, host="0.0.0.0", port=settings.PORT)
    else:
        # Polling mode
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
