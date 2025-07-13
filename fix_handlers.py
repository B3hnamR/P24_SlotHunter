#!/usr/bin/env python3
"""
اصلاح handlers برای استفاده صحیح از database
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent))

def fix_handlers_file():
    """اصلاح فایل handlers"""
    print("🔧 Fixing handlers.py")
    print("=" * 30)
    
    handlers_file = Path("src/telegram_bot/handlers.py")
    
    if not handlers_file.exists():
        print("❌ handlers.py not found")
        return False
    
    try:
        # خواندن فایل
        with open(handlers_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # جایگزینی‌های مورد نیاز
        replacements = [
            # اصلاح import
            ("from src.database.database import db_session", 
             "from src.database.database import db_session"),
            
            # اصلاح استفاده از db_session
            ("with db_session() as session:", 
             "# Database session will be injected by bot"),
        ]
        
        # اعمال تغییرات
        modified = False
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                modified = True
                print(f"✅ Replaced: {old[:50]}...")
        
        if modified:
            # ذخیره فایل
            with open(handlers_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ handlers.py updated")
        else:
            print("ℹ️ No changes needed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing handlers: {e}")
        return False

def create_fixed_handlers():
    """ایجاد نسخه اصلاح شده handlers"""
    print("\n🔧 Creating fixed handlers")
    print("=" * 30)
    
    fixed_content = '''"""
Handler های ربات تلگرام - نسخه اصلاح شده
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select
from typing import List

from src.database.models import User, Doctor, Subscription
from src.telegram_bot.messages import MessageFormatter
from src.utils.logger import get_logger

logger = get_logger("TelegramHandlers")


class TelegramHandlers:
    """کلاس handler های تلگرام"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /start"""
        try:
            user = update.effective_user
            
            # ثبت/به‌روزرسانی کاربر در دیتابیس
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(User).filter(User.telegram_id == user.id)
                )
                db_user = result.scalar_one_or_none()
                
                if not db_user:
                    # کاربر جدید
                    db_user = User(
                        telegram_id=user.id,
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name
                    )
                    session.add(db_user)
                    logger.info(f"👤 کاربر جدید ثبت شد: {user.first_name} (@{user.username})")
                else:
                    # به‌روزرسانی اطلاعات
                    db_user.username = user.username
                    db_user.first_name = user.first_name
                    db_user.last_name = user.last_name
                    db_user.is_active = True
            
            # ارسال پیام خوش‌آمدگویی
            welcome_text = MessageFormatter.welcome_message(user.first_name)
            await update.message.reply_text(welcome_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ خطا در دستور start: {e}")
            await update.message.reply_text(MessageFormatter.error_message(str(e)))
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /help"""
        try:
            help_text = MessageFormatter.help_message()
            await update.message.reply_text(help_text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"❌ خطا در دستور help: {e}")
            await update.message.reply_text(MessageFormatter.error_message(str(e)))
    
    async def doctors_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /doctors"""
        try:
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(Doctor).filter(Doctor.is_active == True)
                )
                doctors = result.scalars().all()
                
                if not doctors:
                    await update.message.reply_text("❌ هیچ دکتری در سیستم ثبت نشده است.")
                    return
                
                # ایجاد keyboard
                keyboard = []
                for doctor in doctors:
                    keyboard.append([
                        InlineKeyboardButton(
                            f"👨‍⚕️ {doctor.name}",
                            callback_data=f"doctor_info_{doctor.id}"
                        )
                    ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                doctors_text = MessageFormatter.doctor_list_message(doctors)
                
                await update.message.reply_text(
                    doctors_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در دستور doctors: {e}")
            await update.message.reply_text(MessageFormatter.error_message(str(e)))
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت callback های دکمه‌ها"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            
            if data.startswith("doctor_info_"):
                await self._handle_doctor_info(query, data)
            elif data.startswith("subscribe_"):
                await self._handle_subscribe(query, data, user_id)
            elif data.startswith("unsubscribe_"):
                await self._handle_unsubscribe(query, data, user_id)
            
        except Exception as e:
            logger.error(f"❌ خطا در callback: {e}")
            try:
                await query.edit_message_text(MessageFormatter.error_message(str(e)))
            except:
                await query.message.reply_text(MessageFormatter.error_message(str(e)))
    
    async def _handle_doctor_info(self, query, data):
        """نمایش اطلاعات دکتر"""
        try:
            doctor_id = int(data.split("_")[2])
            
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(Doctor).filter(Doctor.id == doctor_id)
                )
                doctor = result.scalar_one_or_none()
                
                if not doctor:
                    await query.edit_message_text("❌ دکتر یافت نشد.")
                    return
                
                info_text = MessageFormatter.doctor_info_message(doctor)
                
                # دکمه اشتراک
                keyboard = [[
                    InlineKeyboardButton(
                        "📝 اشتراک در این دکتر",
                        callback_data=f"subscribe_{doctor.id}"
                    )
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    info_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"❌ خطا در نمایش اطلاعات دکتر: {e}")
            await query.edit_message_text(MessageFormatter.error_message(str(e)))
    
    async def _handle_subscribe(self, query, data, user_id):
        """مدیریت اشتراک"""
        try:
            doctor_id = int(data.split("_")[1])
            
            async with self.db_manager.session_scope() as session:
                # بررسی وجود کاربر
                user_result = await session.execute(
                    select(User).filter(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await query.edit_message_text("❌ ابتدا دستور /start را اجرا کنید.")
                    return
                
                # بررسی وجود دکتر
                doctor_result = await session.execute(
                    select(Doctor).filter(Doctor.id == doctor_id)
                )
                doctor = doctor_result.scalar_one_or_none()
                
                if not doctor:
                    await query.edit_message_text("❌ دکتر یافت نشد.")
                    return
                
                # بررسی اشتراک قبلی
                sub_result = await session.execute(
                    select(Subscription).filter(
                        Subscription.user_id == user.id,
                        Subscription.doctor_id == doctor.id
                    )
                )
                existing_sub = sub_result.scalar_one_or_none()
                
                if existing_sub:
                    if existing_sub.is_active:
                        await query.edit_message_text(
                            f"✅ شما قبلاً در دکتر **{doctor.name}** مشترک هستید.",
                            parse_mode='Markdown'
                        )
                        return
                    else:
                        # فعال‌سازی مجدد
                        existing_sub.is_active = True
                else:
                    # اشتراک جدید
                    new_subscription = Subscription(
                        user_id=user.id,
                        doctor_id=doctor.id
                    )
                    session.add(new_subscription)
                
                success_text = MessageFormatter.subscription_success_message(doctor)
                await query.edit_message_text(success_text, parse_mode='Markdown')
                
                logger.info(f"📝 اشتراک جدید: {user.full_name} -> {doctor.name}")
                
        except Exception as e:
            logger.error(f"❌ خطا در اشتراک: {e}")
            await query.edit_message_text(MessageFormatter.error_message(str(e)))
    
    async def _handle_unsubscribe(self, query, data, user_id):
        """مدیریت لغو اشتراک"""
        try:
            doctor_id = int(data.split("_")[1])
            
            async with self.db_manager.session_scope() as session:
                # بررسی وجود کاربر
                user_result = await session.execute(
                    select(User).filter(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await query.edit_message_text("❌ ابتدا دستور /start را اجرا کنید.")
                    return
                
                # بررسی وجود دکتر
                doctor_result = await session.execute(
                    select(Doctor).filter(Doctor.id == doctor_id)
                )
                doctor = doctor_result.scalar_one_or_none()
                
                if not doctor:
                    await query.edit_message_text("❌ دکتر یافت نشد.")
                    return
                
                # پیدا کردن اشتراک
                sub_result = await session.execute(
                    select(Subscription).filter(
                        Subscription.user_id == user.id,
                        Subscription.doctor_id == doctor.id,
                        Subscription.is_active == True
                    )
                )
                subscription = sub_result.scalar_one_or_none()
                
                if not subscription:
                    await query.edit_message_text(
                        f"❌ شما در دکتر **{doctor.name}** مشترک نیستید.",
                        parse_mode='Markdown'
                    )
                    return
                
                # لغو اشتراک
                subscription.is_active = False
                
                success_text = MessageFormatter.unsubscription_success_message(doctor)
                await query.edit_message_text(success_text, parse_mode='Markdown')
                
                logger.info(f"🗑️ لغو اشتراک: {user.full_name} -> {doctor.name}")
                
        except Exception as e:
            logger.error(f"❌ خطا در لغو اشتراک: {e}")
            await query.edit_message_text(MessageFormatter.error_message(str(e)))
'''
    
    try:
        # ذخیره فایل جدید
        with open("src/telegram_bot/handlers_fixed.py", 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("✅ Fixed handlers created: handlers_fixed.py")
        return True
        
    except Exception as e:
        print(f"❌ Error creating fixed handlers: {e}")
        return False

def main():
    print("🔧 P24_SlotHunter Handlers Fixer")
    print("=" * 40)
    
    # ایجاد نسخه اصلاح شده
    if create_fixed_handlers():
        print("\n✅ Fixed handlers created successfully!")
        print("\n📋 Next steps:")
        print("1. Stop the service: ./server_manager.sh stop")
        print("2. Replace handlers.py with handlers_fixed.py")
        print("3. Update bot.py to use the fixed handlers")
        print("4. Restart the service: ./server_manager.sh start")
    else:
        print("\n❌ Failed to create fixed handlers")

if __name__ == "__main__":
    main()