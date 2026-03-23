#!/usr/bin/env python3
"""
بوت تيليجرام - النسخة المستقرة
"""
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

# ✅ طباعة فورية
logger.info("=" * 60)
logger.info("🚀 BOT IS STARTING...")
logger.info("=" * 60)

# ✅ استيراد الإعدادات
try:
    from bot.config.settings import settings
    logger.info("✅ Settings loaded")
    logger.info(f"   WEBHOOK_HOST: {settings.WEBHOOK_HOST or '❌ EMPTY'}")
except Exception as e:
    logger.error(f"❌ Settings error: {e}")
    sys.exit(1)

# ✅ استيراد aiogram (القديم - يعمل)
try:
    from aiogram import Bot, Dispatcher
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from aiohttp import web
    logger.info("✅ Aiogram imported")
except Exception as e:
    logger.error(f"❌ Aiogram error: {e}")
    sys.exit(1)

# ✅ إنشاء البوت (الطريقة القديمة - تظهر تحذير لكنها تعمل)
bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()
logger.info("✅ Bot created")

# ✅ Handlers
try:
    from bot.handlers import (
        commands_router,
        admin_text_router,
        captcha_router,
        owner_router,
        group_events_router
    )
    
    dp.include_router(commands_router)
    dp.include_router(admin_text_router)
    dp.include_router(captcha_router)
    dp.include_router(group_events_router)
    dp.include_router(owner_router)
    logger.info("✅ Routers registered")
except Exception as e:
    logger.error(f"❌ Routers error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ✅ Webhook setup
async def on_startup():
    logger.info("🔄 on_startup called")
    if settings.IS_WEBHOOK_MODE:
        try:
            await bot.set_webhook(settings.WEBHOOK_URL)
            logger.info(f"✅ Webhook set: {settings.WEBHOOK_URL}")
        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")

async def on_shutdown():
    logger.info("🛑 on_shutdown called")
    await bot.delete_webhook()

def main():
    logger.info("🎯 main() started")
    
    # إنشاء تطبيق aiohttp
    app = web.Application()
    
    # ✅ Health check (الأهم!)
    async def health(request):
        logger.info(f"Health check from {request.remote}")
        return web.Response(text="OK", status=200)
    
    app.router.add_get("/health", health)
    logger.info("✅ Health endpoint added")
    
    # Webhook أو Polling
    if settings.IS_WEBHOOK_MODE:
        logger.info("🔧 Webhook mode")
        
        webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_handler.register(app, path=settings.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        logger.info(f"🌐 Starting server on port {settings.PORT}")
        web.run_app(app, host="0.0.0.0", port=settings.PORT)
    else:
        logger.info("🔧 Polling mode")
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()
