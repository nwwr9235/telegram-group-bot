# bot/handlers/__init__.py
from bot.handlers.commands import router as commands_router
from bot.handlers.admin_text import router as admin_text_router
from bot.handlers.captcha import router as captcha_router
from bot.handlers.owner import router as owner_router
from bot.handlers.group_events import router as group_events_router

__all__ = [
    'commands_router',
    'admin_text_router',
    'captcha_router',
    'owner_router',
    'group_events_router'
]
