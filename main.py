#!/usr/bin/env python3
"""
بوت تيليجرام - نسخة متوسطة
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
try:
    from bot.config.settings import settings
    logger.info(f"✅ Settings loaded")
    logger.info(f"   BOT_TOKEN: {'✅' if settings.BOT_TOKEN else '❌'}")
    logger.info(f"   ADMIN_ID: {settings.ADMIN_ID}")
    logger.info(f"   WEBHOOK_HOST: {settings.WEBHOOK_HOST or '❌ EMPTY'}")
except Exception as e:
    logger.error(f"❌ Settings error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ✅ استيراد aiogram
try:
    from aiogram import Bot, Dispatcher
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from aiohttp import web
    logger.info("✅ Aiogram imported")
except Exception as e:
    logger.error(f"❌ Aiogram error: {e}")
    sys.exit(1)

# ✅ إنشاء البوت
bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# ✅ Handler بسيط
@dp.message()
async def echo(message):
    await message.reply(f"Received: {message.text}")

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
