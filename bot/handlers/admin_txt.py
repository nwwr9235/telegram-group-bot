import asyncio
import re
from aiogram import Router, Bot
from aiogram.types import Message, ChatPermissions

from bot.filters.text_commands import TextCommand
from bot.filters.admin_filter import IsAdmin
from bot.database import models

router = Router()
router.message.filter(IsAdmin())

@router.message(TextCommand(["حظر", "بان", "block"]))
async def ban_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        user_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.full_name
        
        await bot.ban_chat_member(message.chat.id, user_id)
        await message.reply(f"🚫 تم حظر {name}")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

@router.message(TextCommand(["فك حظر", "فك بان", "unban"]))
async def unban_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        user_id = message.reply_to_message.from_user.id
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.reply("✅ تم فك الحظر")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

@router.message(TextCommand(["كتم", "اسكات", "mute"]))
async def mute_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        user_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.full_name
        
        duration = 3600
        if "ساعة" in message.text:
            match = re.search(r'(\d+)\s*ساعة', message.text)
            if match:
                duration = int(match.group(1)) * 3600
        elif "دقيقة" in message.text:
            match = re.search(r'(\d+)\s*دقيقة', message.text)
            if match:
                duration = int(match.group(1)) * 60
        
        until = int(asyncio.get_event_loop().time()) + duration
        
        await bot.restrict_chat_member(
            message.chat.id, user_id,
            until_date=until,
            permissions=ChatPermissions(can_send_messages=False)
        )
        
        time_str = f"{duration//3600} ساعة" if duration >= 3600 else f"{duration//60} دقيقة"
        await message.reply(f"🔇 تم كتم {name} لمدة {time_str}")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

@router.message(TextCommand(["فك كتم", "الغاء كتم", "unmute"]))
async def unmute_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        user_id = message.reply_to_message.from_user.id
        await bot.restrict_chat_member(
            message.chat.id, user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True
            )
        )
        await message.reply("🔊 تم فك الكتم")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

@router.message(TextCommand(["انذار", "تحذير", "warn"]))
async def warn_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        target = message.reply_to_message.from_user
        parts = message.text.split(maxsplit=1)
        reason = parts[1] if len(parts) > 1 else "لم يُذكر"
        
        count = await models.add_warning(target.id, message.chat.id, reason)
        settings = await models.get_group_settings(message.chat.id)
        max_warn = settings['max_warnings'] if settings else 3
        
        await message.reply(
            f"⚠️ إنذار جديد\nالمستخدم: {target.full_name}\nالسبب: {reason}\nالعدد: {count}/{max_warn}"
        )
        
        if count >= max_warn:
            await bot.ban_chat_member(message.chat.id, target.id)
            await message.reply(f"🚫 حظر تلقائي")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

@router.message(TextCommand(["حذف انذار", "الغاء انذار", "unwarn"]))
async def unwarn_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        target = message.reply_to_message.from_user
        await models.remove_warnings(target.id, message.chat.id)
        await message.reply(f"✅ تم حذف إنذارات {target.full_name}")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

@router.message(TextCommand(["تثبيت", "pin", "ثبت"]))
async def pin_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على الرسالة للتثبيت")
    
    try:
        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        await message.reply("📌 تم التثبيت")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

@router.message(TextCommand(["الغاء تثبيت", "فك تثبيت", "unpin"]))
async def unpin_cmd(message: Message, bot: Bot):
    try:
        await bot.unpin_all_chat_messages(message.chat.id)
        await message.reply("📌 تم إلغاء التثبيت")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

@router.message(TextCommand(["حذف", "delete", "del"]))
async def delete_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على الرسالة للحذف")
    
    try:
        await bot.delete_message(message.chat.id, message.reply_to_message.message_id)
        await message.delete()
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

@router.message(TextCommand(["تنظيف", "purge", "مسح"]))
async def purge_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على أول رسالة")
    
    try:
        match = re.search(r'(\d+)', message.text)
        count = int(match.group(1)) if match else 10
        count = min(count, 100)
        
        start = message.reply_to_message.message_id
        end = message.message_id
        deleted = 0
        
        for msg_id in range(start, end + 1):
            try:
                await bot.delete_message(message.chat.id, msg_id)
                deleted += 1
            except:
                pass
        
        confirm = await message.reply(f"🗑️ تم حذف {deleted} رسالة")
        await asyncio.sleep(3)
        await confirm.delete()
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

@router.message(TextCommand(["مشرف", "رفع مشرف", "promote"]))
async def promote_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        user_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.full_name
        
        await bot.promote_chat_member(
            message.chat.id, user_id,
            can_delete_messages=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_invite_users=True
        )
        await message.reply(f"⬆️ تم رفع {name} مشرفاً")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

@router.message(TextCommand(["تنزيل", "تنزيل مشرف", "demote"]))
async def demote_cmd(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("⚠️ رد على رسالة المستخدم")
    
    try:
        user_id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.full_name
        
        await bot.promote_chat_member(
            message.chat.id, user_id,
            can_delete_messages=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_invite_users=False,
            can_manage_chat=False
        )
        await message.reply(f"⬇️ تم تنزيل {name}")
    except Exception as e:
        await message.reply(f"❌ فشل: {str(e)}")

