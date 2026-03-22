"""
تسجيل كل الأحداث في قاعدة البيانات
"""
from typing import Callable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from bot.database.connection import get_pool


class LoggingMiddleware(BaseMiddleware):
    """تسجيل كل الرسائل والأوامر"""
    
    async def __call__(
        self,
        handler: Callable,
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # تسجيل في الخلفية
        if event.text:
            asyncio.create_task(self.log_message(event))
        
        return await handler(event, data)
    
    async def log_message(self, message: Message):
        """تسجيل الرسالة"""
        try:
            pool = await get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO logs (event_type, user_id, chat_id, text)
                    VALUES ($1, $2, $3, $4)
                    """,
                    "message",
                    message.from_user.id,
                    message.chat.id,
                    message.text[:100] if message.text else None
                )
        except Exception:
            pass  # لا نوقف البوت إذا فشل التسجيل


import asyncio

