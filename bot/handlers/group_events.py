"""
أحداث المجموعة: ترحيب، مغادرة، تثبيت القوانين
"""
from aiogram import Router, Bot
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER

from bot.database.connection import get_pool

router = Router()


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: ChatMemberUpdated, bot: Bot):
    """عند مغادرة عضو"""
    user = event.old_chat_member.user
    chat = event.chat
    
    # يمكن إضافة رسالة وداع هنا (اختياري)
    # await bot.send_message(chat.id, f"👋 وداعاً {user.full_name}!")
    pass


@router.message()
async def set_welcome_cmd(message: Message):
    """تعيين رسالة ترحيب مخصصة"""
    # هذا يحتاج أمر منفصل، سأضعه هنا مؤقتاً
    pass

