#!/usr/bin/env python3
import logging
import os
from aiohttp import web

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🚀 STARTING")

app = web.Application()

async def health(request):
    logger.info("Health check!")
    return web.Response(text="OK")

app.router.add_get("/health", health)

port = int(os.getenv("PORT", "8080"))
logger.info(f"Port: {port}")

web.run_app(app, host="0.0.0.0", port=port)
