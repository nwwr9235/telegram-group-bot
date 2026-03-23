#!/usr/bin/env python3
"""
بوت تيليجرام - النسخة النهائية
"""
import asyncio
import logging
import sys
import os

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
from bot.config.settings import settings
logger.info(f"✅ Settings loaded")
logger.info(f"   WEBHOOK_HOST: {settings.WEBHOOK_HOST}")

# ✅ استيراد aiogram (مُحدّث)
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
logger.info("✅ Aiogram imported")

# ✅ إنشاء البوت (بدون تحذير)
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# ✅ Handlers
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

# ✅ Webhook setup
async def on_startup():
    logger.info("🔄 on_startup called")
    if settings.IS_WEBHOOK_MODE:
        await bot.set_webhook(settings.WEBHOOK_URL)
        logger.info(f"✅ Webhook set: {settings.WEBHOOK_URL}")

async def on_shutdown():
    logger.info("🛑 on_shutdown called")
    await bot.delete_webhook()

def main():
    logger.info("🎯 main() started")
    
    app = web.Application()
    
    # Health check
    async def health(request):
        return web.Response(text="OK", status=200)
    
    app.router.add_get("/health", health)
    
    if settings.IS_WEBHOOK_MODE:
        logger.info("🔧 Webhook mode")
        webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_handler.register(app, path=settings.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        web.run_app(app, host="0.0.0.0", port=settings.PORT)
    else:
        logger.info("🔧 Polling mode")
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()
