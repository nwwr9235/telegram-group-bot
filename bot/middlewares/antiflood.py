"""
حماية من التكرار (Anti-Flood) باستخدام Redis
"""
import time
from typing import Callable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.dispatcher.flags import get_flag

from bot.config.settings import settings

# في الإنتاج استخدم Redis، هنا نستخدم dict مؤقت
flood_cache = {}


class AntiFloodMiddleware(BaseMiddleware):
    """منع المستخدم من إرسال رسائل كثيرة"""
    
    async def __call__(
        self,
        handler: Callable,
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # تخطي إذا كان الأمر مُعفى
        if get_flag(data, "no_flood"):
            return await handler(event, data)
        
        # لا نطبق في الخاص
        if event.chat.type == "private":
            return await handler(event, data)
        
        user_id = event.from_user.id
        chat_id = event.chat.id
        current_time = time.time()
        
        key = f"{chat_id}:{user_id}"
        
        # تنظيف القديم
        if key in flood_cache:
            flood_cache[key] = [
                t for t in flood_cache[key] 
                if current_time - t < settings.FLOOD_PERIOD
            ]
        else:
            flood_cache[key] = []
        
        # التحقق من الحد
        if len(flood_cache[key]) >= settings.FLOOD_LIMIT:
            # حذف الرسالة وتحذير
            try:
                await event.delete()
                warning = await event.answer(
                    f"⚠️ {event.from_user.full_name}: توقف عن الإرسال المتكرر!"
                )
                # حذف التحذير بعد 5 ثوانٍ
                await asyncio.sleep(5)
                await warning.delete()
            except Exception:
                pass
            return None
        
        # إضافة الرسالة الحالية
        flood_cache[key].append(current_time)
        
        return await handler(event, data)


# استيراد asyncio للاستخدام أعلاه
import asyncio

