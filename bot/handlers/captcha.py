"""
نظام CAPTCHA للأعضاء الجدد
"""
import random
import asyncio
from aiogram import Router, Bot, F
from aiogram.types import (
    Message, CallbackQuery, ChatMemberUpdated,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.exceptions import TelegramAPIError

from bot.config.settings import settings

router = Router()

# تخزين مؤقت للـ CAPTCHA (في الإنتاج استخدم Redis)
captcha_data = {}


def generate_math_captcha():
    """توليد مسألة رياضية"""
    ops = ['+', '-', '*']
    op = random.choice(ops)
    
    if op == '+':
        a, b = random.randint(1, 20), random.randint(1, 20)
        answer = a + b
        question = f"{a} + {b} = ?"
    elif op == '-':
        a, b = random.randint(10, 30), random.randint(1, 10)
        answer = a - b
        question = f"{a} - {b} = ?"
    else:
        a, b = random.randint(2, 9), random.randint(2, 9)
        answer = a * b
        question = f"{a} × {b} = ?"
    
    # توليد خيارات خاطئة
    wrong = set()
    while len(wrong) < 3:
        fake = answer + random.randint(-10, 10)
        if fake != answer and fake > 0:
            wrong.add(fake)
    
    options = list(wrong) + [answer]
    random.shuffle(options)
    
    return {
        "question": question,
        "answer": answer,
        "options": options
    }


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated, bot: Bot):
    """عند انضمام عضو جديد"""
    user = event.new_chat_member.user
    chat = event.chat
    
    # تخطي البوتات
    if user.is_bot:
        return
    
    # توليد CAPTCHA
    captcha = generate_math_captcha()
    captcha_id = f"{chat.id}:{user.id}"
    captcha_data[captcha_id] = captcha["answer"]
    
    # إنشاء أزرار
    buttons = []
    for opt in captcha["options"]:
        buttons.append([
            InlineKeyboardButton(
                text=str(opt),
                callback_data=f"captcha:{chat.id}:{user.id}:{opt}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # إرسال رسالة CAPTCHA
    try:
        msg = await bot.send_message(
            chat_id=chat.id,
            text=(
                f"👋 أهلاً <b>{user.full_name}</b>!\n\n"
                f"🔐 <b>للتحقق أنك لست روبوت، أجب على:</b>\n\n"
                f"<code>{captcha['question']}</code>\n\n"
                f"⏱️ لديك {settings.CAPTCHA_TIMEOUT // 60} دقيقة"
            ),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        # جدولة الحذف التلقائي
        asyncio.create_task(
            check_captcha_timeout(bot, chat.id, user.id, msg.message_id, captcha_id)
        )
        
    except TelegramAPIError as e:
        print(f"Error sending captcha: {e}")


async def check_captcha_timeout(bot: Bot, chat_id: int, user_id: int, msg_id: int, captcha_id: str):
    """التحقق من انتهاء المهلة"""
    await asyncio.sleep(settings.CAPTCHA_TIMEOUT)
    
    # إذا لم يُجب بعد
    if captcha_id in captcha_data:
        try:
            # حظر ثم فك الحظر (طرد)
            await bot.ban_chat_member(chat_id, user_id)
            await asyncio.sleep(0.5)
            await bot.unban_chat_member(chat_id, user_id)
            
            # حذف رسالة CAPTCHA
            await bot.delete_message(chat_id, msg_id)
            
            # إشعار
            await bot.send_message(
                chat_id=chat_id,
                text=f"⛔ تم طرد المستخدم لعدم إكمال التحقق في الوقت المحدد."
            )
            
        except TelegramAPIError:
            pass
        
        # تنظيف
        captcha_data.pop(captcha_id, None)


@router.callback_query(F.data.startswith("captcha:"))
async def on_captcha_answer(callback: CallbackQuery, bot: Bot):
    """معالجة إجابة CAPTCHA"""
    parts = callback.data.split(":")
    chat_id = int(parts[1])
    user_id = int(parts[2])
    answer = int(parts[3])
    
    captcha_id = f"{chat_id}:{user_id}"
    
    # التحقق من المستخدم
    if callback.from_user.id != user_id:
        await callback.answer("هذا ليس لك!", show_alert=True)
        return
    
    # التحقق من الإجابة
    correct = captcha_data.get(captcha_id)
    
    if correct is None:
        await callback.answer("انتهت صلاحية التحقق!", show_alert=True)
        return
    
    if answer == correct:
        # إجابة صحيحة
        captcha_data.pop(captcha_id, None)
        
        # حذف رسالة CAPTCHA
        await callback.message.delete()
        
        # رسالة ترحيب
        await bot.send_message(
            chat_id=chat_id,
            text=(
                f"✅ <b>تم التحقق بنجاح!</b>\n\n"
                f"🎉 أهلاً وسهلاً بك <a href='tg://user?id={user_id}'>{callback.from_user.full_name}</a> "
                f"في المجموعة!"
            ),
            parse_mode="HTML"
        )
        
        await callback.answer("تم التحقق!", show_alert=False)
    else:
        # إجابة خاطئة
        await callback.answer("❌ إجابة خاطئة! حاول مرة أخرى.", show_alert=True)
