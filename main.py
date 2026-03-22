import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.config.settings import settings
from bot.database.connection import init_db, close_db
from bot.handlers import commands_router, admin_text_router, captcha_router, owner_router, group_events_router
from bot.middlewares.antiflood import AntiFloodMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

dp.message.middleware(AntiFloodMiddleware())

dp.include_router(commands_router)
dp.include_router(admin_text_router)
dp.include_router(captcha_router)
dp.include_router(group_events_router)
dp.include_router(owner_router)

async def on_startup():
    logger.info("🚀 Starting bot...")
    await init_db()
    
    if settings.WEBHOOK_HOST:
        await bot.set_webhook(f"{settings.WEBHOOK_HOST}{settings.WEBHOOK_PATH}")
        logger.info(f"✅ Webhook: {settings.WEBHOOK_HOST}")
    
    await bot.send_message(
        settings.ADMIN_ID,
        "🤖 <b>Bot Started!</b>",
        parse_mode="HTML"
    )

async def on_shutdown():
    logger.info("🛑 Shutting down...")
    await close_db()
    await bot.delete_webhook()

def main():
    if settings.WEBHOOK_HOST:
        app = web.Application()
        webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_handler.register(app, path=settings.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        app.router.add_get("/health", lambda r: web.Response(text="OK"))
        
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        
        web.run_app(app, host="0.0.0.0", port=settings.PORT)
    else:
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()
