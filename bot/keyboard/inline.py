"""
الأزرار المضمنة (Inline Keyboards)
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def captcha_keyboard(options: list, captcha_id: str):
    """أزرار CAPTCHA"""
    buttons = []
    for opt in options:
        buttons.append([
            InlineKeyboardButton(
                text=str(opt),
                callback_data=f"captcha:{captcha_id}:{opt}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_keyboard(action: str, user_id: int):
    """أزرار تأكيد (نعم/لا)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ نعم",
                callback_data=f"confirm:{action}:{user_id}:yes"
            ),
            InlineKeyboardButton(
                text="❌ لا",
                callback_data=f"confirm:{action}:{user_id}:no"
            )
        ]
    ])


def admin_panel_keyboard():
    """أزرار لوحة التحكم"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 إحصائيات", callback_data="stats")],
        [InlineKeyboardButton(text="📢 بث رسالة", callback_data="broadcast")],
        [InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="settings")],
    ])

