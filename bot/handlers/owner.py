"""
أوامر المطور - تظهر فقط في المحادثة الخاصة
"""
import asyncio
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from bot.config.settings import settings
from bot.database.connection import get_pool

router = Router()


def is_owner(message: Message) -> bool:
    """التحقق إذا كان المستخدم هو المطور"""
    return message.from_user.id == settings.ADMIN_ID


@router.message(Command("admin"), lambda msg: msg.chat.type == "private")
async def admin_panel(message: Message):
    """لوحة التحكم الرئيسية"""
    if not is_owner(message):
        return await message.reply("⛔ هذا الأمر للمطور فقط!")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton(text="📋 سجلات الأحداث", callback_data="logs")],
        [InlineKeyboardButton(text="📢 بث رسالة", callback_data="broadcast")],
        [InlineKeyboardButton(text="⚙️ إعدادات البوت", callback_data="settings")],
    ])
    
    await message.reply(
        "🔐 <b>لوحة تحكم المطور</b>\n\n"
        "اختر الإجراء المطلوب:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data == "stats")
async def show_stats(callback: CallbackQuery):
    """عرض الإحصائيات"""
    if callback.from_user.id != settings.ADMIN_ID:
        return await callback.answer("غير مصرح!", show_alert=True)
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        total_groups = await conn.fetchval("SELECT COUNT(*) FROM groups")
        total_warnings = await conn.fetchval("SELECT COUNT(*) FROM warnings")
    
    text = (
        f"📊 <b>إحصائيات البوت</b>\n\n"
        f"👥 إجمالي المستخدمين: <code>{total_users}</code>\n"
        f"💬 إجمالي المجموعات: <code>{total_groups}</code>\n"
        f"⚠️ إجمالي الإنذارات: <code>{total_warnings}</code>\n"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML")


@router.message(Command("broadcast"), lambda msg: msg.chat.type == "private")
async def broadcast_message(message: Message, bot: Bot):
    """بث رسالة لجميع المجموعات"""
    if not is_owner(message):
        return await message.reply("⛔ هذا الأمر للمطور فقط!")
    
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على الرسالة التي تريد بثها")
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        groups = await conn.fetch("SELECT telegram_id FROM groups")
    
    sent = 0
    failed = 0
    
    status = await message.reply(f"⏳ جاري الإرسال... 0/{len(groups)}")
    
    for group in groups:
        try:
            await bot.copy_message(
                chat_id=group['telegram_id'],
                from_chat_id=message.chat.id,
                message_id=message.reply_to_message.message_id
            )
            sent += 1
            await asyncio.sleep(0.1)  # تجنب الحظر
        except Exception:
            failed += 1
        
        if (sent + failed) % 10 == 0:
            await status.edit_text(
                f"⏳ جاري الإرسال... {sent + failed}/{len(groups)}\n"
                f"✅ نجح: {sent} | ❌ فشل: {failed}"
            )
    
    await status.edit_text(
        f"✅ <b>تم الانتهاء!</b>\n\n"
        f"📤 تم الإرسال: {sent}\n"
        f"❌ فشل: {failed}",
        parse_mode="HTML"
    )


@router.message(Command("sql"), lambda msg: msg.chat.type == "private")
async def execute_sql(message: Message):
    """تنفيذ استعلام SQL (بحذر!)"""
    if not is_owner(message):
        return await message.reply("⛔ هذا الأمر للمطور فقط!")
    
    # استخراج الاستعلام بعد الأمر
    query = message.text.replace("/sql", "").strip()
    
    if not query:
        return await message.reply("⚠️ اكتب الاستعلام بعد /sql")
    
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            if query.lower().startswith("select"):
                rows = await conn.fetch(query)
                result = "\n".join([str(dict(row)) for row in rows[:10]])
                await message.reply(f"<pre>{result}</pre>", parse_mode="HTML")
            else:
                await conn.execute(query)
                await message.reply("✅ تم تنفيذ الاستعلام")
    except Exception as e:
        await message.reply(f"❌ خطأ: {str(e)}")

