from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus
from bot.config.settings import settings

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.type == "private":
            return message.from_user.id == settings.ADMIN_ID
        
        member = await message.bot.get_chat_member(
            message.chat.id, message.from_user.id
        )
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
