#!/usr/bin/env python3
"""
بوت تيليجرام - النسخة المضمونة
"""
import logging
import sys
import os

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

# استيراد
from bot.config.settings import settings
logger.info(f"✅ Settings: WEBHOOK_HOST={settings.WEBHOOK_HOST or 'EMPTY'}")

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
logger.info("✅ Imports successful")

# بوت بسيط
bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# Handler بسيط
@dp.message()
async def echo(message):
    await message.answer(f"Received: {message.text}")

# Webhook
async def on_startup():
    if settings.IS_WEBHOOK_MODE:
        await bot.set_webhook(settings.WEBHOOK_URL)
        logger.info(f"✅ Webhook: {settings.WEBHOOK_URL}")

# تطبيق
app = web.Application()

@app.router.get("/health")
async def health(request):
    return web.Response(text="OK", status=200)

# تشغيل
if settings.IS_WEBHOOK_MODE:
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=settings.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    dp.startup.register(on_startup)
    logger.info(f"🌐 Starting on port {settings.PORT}")
    web.run_app(app, host="0.0.0.0", port=settings.PORT)
else:
    import asyncio
    dp.startup.register(on_startup)
    asyncio.run(dp.start_polling(bot))
