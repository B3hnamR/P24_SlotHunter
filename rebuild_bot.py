#!/usr/bin/env python3
"""
بازسازی کامل ربات تلگرام با معماری صحیح
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent))

def create_new_bot_architecture():
    """ایجاد معماری جدید ربات"""
    print("🏗️ Creating New Bot Architecture")
    print("=" * 40)
    
    # 1. ایجاد handlers جدید
    create_unified_handlers()
    
    # 2. ایجاد bot جدید
    create_new_bot()
    
    # 3. ایجاد menu handlers جدید
    create_menu_handlers()
    
    print("✅ New bot architecture created!")

def create_unified_handlers():
    """ایجاد handlers یکپارچه"""
    print("📝 Creating unified handlers...")
    
    handlers_content = '''"""
Unified Telegram Handlers - معماری جدید و ریشه‌ای
"""
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select
from typing import List
from datetime import datetime

from src.database.models import User, Doctor, Subscription
from src.telegram_bot.messages import MessageFormatter
from src.utils.logger import get_logger

logger = get_logger("UnifiedHandlers")


class UnifiedTelegramHandlers:
    """کلاس یکپارچه handlers تلگرام"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    # ==================== Command Handlers ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /start"""
        try:
            user = update.effective_user
            
            # ثبت/به‌روزرسانی کاربر
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(User).filter(User.telegram_id == user.id)
                )
                db_user = result.scalar_one_or_none()
                
                if not db_user:
                    db_user = User(
                        telegram_id=user.id,
                        username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name
                    )
                    session.add(db_user)
                    logger.info(f"👤 کاربر جدید: {user.first_name}")
                else:
                    db_user.username = user.username
                    db_user.first_name = user.first_name
                    db_user.last_name = user.last_name
                    db_user.is_active = True
                    db_user.last_activity = datetime.utcnow()
            
            # ارسال پیام خوش‌آمدگویی
            welcome_text = MessageFormatter.welcome_message(user.first_name)
            
            # منوی اصلی
            keyboard = [
                [InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors")],
                [InlineKeyboardButton("📝 اشتراک‌های من", callback_data="show_subscriptions")],
                [InlineKeyboardButton("🔔 اشتراک جدید", callback_data="new_subscription")],
                [InlineKeyboardButton("📊 وضعیت من", callback_data="my_status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                welcome_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ خطا در start: {e}")
            await self._send_error_message(update.message, str(e))
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /help"""
        try:
            help_text = MessageFormatter.help_message()
            await update.message.reply_text(help_text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"❌ خطا در help: {e}")
            await self._send_error_message(update.message, str(e))
    
    async def doctors_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /doctors"""
        try:
            await self._show_doctors_list(update.message)
        except Exception as e:
            logger.error(f"❌ خطا در doctors: {e}")
            await self._send_error_message(update.message, str(e))
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /admin"""
        try:
            user_id = update.effective_user.id
            
            # بررسی دسترسی ادمین
            if not await self._is_admin(user_id):
                await update.message.reply_text("❌ ��ما دسترسی ادمین ندارید.")
                return
            
            await self._show_admin_panel(update.message)
            
        except Exception as e:
            logger.error(f"❌ خطا در admin: {e}")
            await self._send_error_message(update.message, str(e))
    
    # ==================== Callback Handlers ====================
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کلی callback ها"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            
            # مسیریابی callback ها
            if data == "show_doctors":
                await self._callback_show_doctors(query)
            elif data == "show_subscriptions":
                await self._callback_show_subscriptions(query, user_id)
            elif data == "new_subscription":
                await self._callback_new_subscription(query, user_id)
            elif data == "my_status":
                await self._callback_my_status(query, user_id)
            elif data.startswith("doctor_info_"):
                await self._callback_doctor_info(query, data, user_id)
            elif data.startswith("subscribe_"):
                await self._callback_subscribe(query, data, user_id)
            elif data.startswith("unsubscribe_"):
                await self._callback_unsubscribe(query, data, user_id)
            elif data == "back_to_main":
                await self._callback_back_to_main(query)
            elif data.startswith("admin_"):
                await self._callback_admin(query, data, user_id)
            else:
                await query.edit_message_text(
                    "❌ دستور نامشخص",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
            
        except Exception as e:
            logger.error(f"❌ خطا در callback: {e}")
            try:
                await query.edit_message_text(
                    f"❌ خطا: {str(e)}",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
            except:
                pass
    
    # ==================== Helper Methods ====================
    
    async def _show_doctors_list(self, message):
        """نمایش لیست دکترها"""
        async with self.db_manager.session_scope() as session:
            result = await session.execute(
                select(Doctor).filter(Doctor.is_active == True)
            )
            doctors = result.scalars().all()
            
            if not doctors:
                await message.reply_text("❌ هیچ دکتری موجود نیست.")
                return
            
            text = f"👨‍⚕️ **لیست دکترها ({len(doctors)} دکتر):**\\n\\n"
            
            keyboard = []
            for doctor in doctors:
                keyboard.append([
                    InlineKeyboardButton(
                        f"👨‍⚕️ {doctor.name}",
                        callback_data=f"doctor_info_{doctor.id}"
                    )
                ])
            
            keyboard.append([
                InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.reply_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def _show_admin_panel(self, message):
        """نمایش پنل ادمین"""
        text = """
🔧 **پنل مدیریت**

از دکمه‌های زیر برای مدیریت سیستم استفاده کنید:
        """
        
        keyboard = [
            [InlineKeyboardButton("👨‍⚕️ مدیریت دکترها", callback_data="admin_doctors")],
            [InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_users")],
            [InlineKeyboardButton("📊 آمار سیستم", callback_data="admin_stats")],
            [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _is_admin(self, user_id):
        """بررسی ادمین بودن"""
        try:
            from src.utils.config import Config
            config = Config()
            return user_id == config.admin_chat_id
        except:
            return False
    
    async def _send_error_message(self, message, error_text):
        """ارسال پیام خطا"""
        await message.reply_text(
            MessageFormatter.error_message(error_text),
            parse_mode='Markdown'
        )
    
    # ==================== Callback Methods ====================
    
    async def _callback_show_doctors(self, query):
        """callback نمایش دکترها"""
        async with self.db_manager.session_scope() as session:
            result = await session.execute(
                select(Doctor).filter(Doctor.is_active == True)
            )
            doctors = result.scalars().all()
            
            if not doctors:
                await query.edit_message_text(
                    "❌ هیچ دکتری موجود نیست.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
                return
            
            text = f"👨‍⚕️ **لیست دکترها ({len(doctors)} دکتر):**\\n\\n"
            
            keyboard = []
            for doctor in doctors:
                keyboard.append([
                    InlineKeyboardButton(
                        f"👨‍⚕️ {doctor.name}",
                        callback_data=f"doctor_info_{doctor.id}"
                    )
                ])
            
            keyboard.append([
                InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def _callback_show_subscriptions(self, query, user_id):
        """callback نمایش اشتراک‌ها"""
        async with self.db_manager.session_scope() as session:
            result = await session.execute(
                select(User).filter(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await query.edit_message_text("❌ کاربر یافت نشد.")
                return
            
            # دریافت اشتراک‌های فعال
            sub_result = await session.execute(
                select(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.is_active == True
                ).join(Doctor)
            )
            subscriptions = sub_result.scalars().all()
            
            if not subscriptions:
                text = "📝 **اشتراک‌های من**\\n\\n❌ شما در هیچ دکتری مشترک نیستید."
                keyboard = [
                    [InlineKeyboardButton("🔔 اشتراک جدید", callback_data="new_subscription")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
            else:
                text = f"📝 **اشتراک‌های من ({len(subscriptions)} اشتراک):**\\n\\n"
                
                keyboard = []
                for sub in subscriptions:
                    text += f"✅ {sub.doctor.name}\\n"
                    keyboard.append([
                        InlineKeyboardButton(
                            f"🗑️ لغو {sub.doctor.name}",
                            callback_data=f"unsubscribe_{sub.doctor.id}"
                        )
                    ])
                
                keyboard.extend([
                    [InlineKeyboardButton("🔔 اشتراک جدید", callback_data="new_subscription")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def _callback_new_subscription(self, query, user_id):
        """callback اشتراک جدید"""
        async with self.db_manager.session_scope() as session:
            # دریافت دکترهای فعال
            result = await session.execute(
                select(Doctor).filter(Doctor.is_active == True)
            )
            doctors = result.scalars().all()
            
            if not doctors:
                await query.edit_message_text(
                    "❌ هیچ دکتری برای اشتراک موجود نیست.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
                return
            
            # دریافت اشتراک‌های فعلی
            user_result = await session.execute(
                select(User).filter(User.telegram_id == user_id)
            )
            user = user_result.scalar_one_or_none()
            
            if user:
                sub_result = await session.execute(
                    select(Subscription).filter(
                        Subscription.user_id == user.id,
                        Subscription.is_active == True
                    )
                )
                subscribed_doctor_ids = [sub.doctor_id for sub in sub_result.scalars().all()]
                
                available_doctors = [
                    doctor for doctor in doctors 
                    if doctor.id not in subscribed_doctor_ids
                ]
            else:
                available_doctors = doctors
            
            if not available_doctors:
                await query.edit_message_text(
                    "✅ شما در تمام دکترها مشترک هستید!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
                return
            
            text = f"🔔 **اشتراک جدید**\\n\\n{len(available_doctors)} دکتر برای اشتراک موجود:"
            
            keyboard = []
            for doctor in available_doctors:
                keyboard.append([
                    InlineKeyboardButton(
                        f"📝 {doctor.name}",
                        callback_data=f"subscribe_{doctor.id}"
                    )
                ])
            
            keyboard.append([
                InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def _callback_my_status(self, query, user_id):
        """callback وضعیت من"""
        async with self.db_manager.session_scope() as session:
            result = await session.execute(
                select(User).filter(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await query.edit_message_text("❌ کاربر یافت نشد.")
                return
            
            # شمارش اشتراک‌ها
            sub_result = await session.execute(
                select(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.is_active == True
                )
            )
            active_subs = len(sub_result.scalars().all())
            
            text = f"""
📊 **وضعیت من**

👤 **نام:** {user.full_name}
📱 **شناسه:** `{user.telegram_id}`
📝 **اشتراک‌های فعال:** {active_subs}
📅 **عضویت:** {user.created_at.strftime('%Y/%m/%d') if user.created_at else 'نامشخص'}
⏰ **آخرین فعالیت:** {datetime.now().strftime('%Y/%m/%d %H:%M')}
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 بروزرسانی", callback_data="my_status")],
                [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def _callback_doctor_info(self, query, data, user_id):
        """callback اطلاعات دکتر"""
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
                
                # بررسی اشتراک کاربر
                user_result = await session.execute(
                    select(User).filter(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                is_subscribed = False
                if user:
                    sub_result = await session.execute(
                        select(Subscription).filter(
                            Subscription.user_id == user.id,
                            Subscription.doctor_id == doctor.id,
                            Subscription.is_active == True
                        )
                    )
                    is_subscribed = sub_result.scalar_one_or_none() is not None
                
                text = f"""
👨‍⚕️ **{doctor.name}**

🏥 **تخصص:** {doctor.specialty or 'نامشخص'}
🏢 **مرکز:** {doctor.center_name or 'نامشخص'}
📍 **آدرس:** {doctor.center_address or 'نامشخص'}

🔗 **لینک:** https://www.paziresh24.com/dr/{doctor.slug}/

{'✅ شما مشترک هستید' if is_subscribed else '❌ شما مشترک نیستید'}
                """
                
                keyboard = []
                if is_subscribed:
                    keyboard.append([
                        InlineKeyboardButton("🗑️ لغو اشتراک", callback_data=f"unsubscribe_{doctor.id}")
                    ])
                else:
                    keyboard.append([
                        InlineKeyboardButton("📝 اشتراک", callback_data=f"subscribe_{doctor.id}")
                    ])
                
                keyboard.extend([
                    [InlineKeyboardButton("🔙 لیست دکترها", callback_data="show_doctors")],
                    [InlineKeyboardButton("🔙 منوی اص��ی", callback_data="back_to_main")]
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در اطلاعات دکتر: {e}")
            await query.edit_message_text(f"❌ خطا: {str(e)}")
    
    async def _callback_subscribe(self, query, data, user_id):
        """callback اشتراک"""
        try:
            doctor_id = int(data.split("_")[1])
            
            async with self.db_manager.session_scope() as session:
                # دریافت کاربر
                user_result = await session.execute(
                    select(User).filter(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await query.edit_message_text("❌ ابتدا /start کنید.")
                    return
                
                # دریافت دکتر
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
                            f"✅ شما قبلاً در **{doctor.name}** مشترک هستید.",
                            parse_mode='Markdown'
                        )
                        return
                    else:
                        existing_sub.is_active = True
                        existing_sub.created_at = datetime.utcnow()
                else:
                    new_sub = Subscription(
                        user_id=user.id,
                        doctor_id=doctor.id
                    )
                    session.add(new_sub)
                
                text = f"""
✅ **اشتراک موفق!**

شما با موفقیت در دکتر **{doctor.name}** مشترک شدید.

🔔 از این پس نوبت‌های خالی به شما اطلاع داده می‌شود.
                """
                
                keyboard = [
                    [InlineKeyboardButton("👨‍⚕️ اطلاعات دکتر", callback_data=f"doctor_info_{doctor.id}")],
                    [InlineKeyboardButton("📝 اشتراک‌های من", callback_data="show_subscriptions")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
                logger.info(f"📝 اشتراک جدید: {user.full_name} -> {doctor.name}")
                
        except Exception as e:
            logger.error(f"❌ خطا در اشتراک: {e}")
            await query.edit_message_text(f"❌ خطا: {str(e)}")
    
    async def _callback_unsubscribe(self, query, data, user_id):
        """callback لغو اشتراک"""
        try:
            doctor_id = int(data.split("_")[1])
            
            async with self.db_manager.session_scope() as session:
                # دریافت کاربر
                user_result = await session.execute(
                    select(User).filter(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                if not user:
                    await query.edit_message_text("❌ کاربر یافت نشد.")
                    return
                
                # دریافت دکتر
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
                        f"❌ شما در **{doctor.name}** مشترک نیستید.",
                        parse_mode='Markdown'
                    )
                    return
                
                # لغو اشتراک
                subscription.is_active = False
                
                text = f"""
✅ **لغو اشتراک موفق!**

اشتراک شما از دکتر **{doctor.name}** لغو شد.

🔕 دیگر اطلاع‌رسانی دریافت نخواهید کرد.
                """
                
                keyboard = [
                    [InlineKeyboardButton("📝 اشتراک مجدد", callback_data=f"subscribe_{doctor.id}")],
                    [InlineKeyboardButton("📝 اشتراک‌های من", callback_data="show_subscriptions")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
                logger.info(f"🗑️ لغو اشتراک: {user.full_name} -> {doctor.name}")
                
        except Exception as e:
            logger.error(f"❌ خطا در لغو اشتراک: {e}")
            await query.edit_message_text(f"❌ خطا: {str(e)}")
    
    async def _callback_back_to_main(self, query):
        """callback بازگشت به منوی اصلی"""
        text = """
🎯 **منوی اصلی**

از دکمه‌های زیر برای استفاده از ربات استفاده کنید:
        """
        
        keyboard = [
            [InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors")],
            [InlineKeyboardButton("📝 اشتراک‌های من", callback_data="show_subscriptions")],
            [InlineKeyboardButton("🔔 اشتراک جدید", callback_data="new_subscription")],
            [InlineKeyboardButton("📊 وضعیت من", callback_data="my_status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _callback_admin(self, query, data, user_id):
        """callback های ادمین"""
        if not await self._is_admin(user_id):
            await query.edit_message_text("❌ دسترسی ندارید.")
            return
        
        admin_action = data.replace("admin_", "")
        
        if admin_action == "doctors":
            await query.edit_message_text(
                "👨‍⚕️ **مدیریت دکترها**\\n\\n🔧 این قسمت در حال توسعه است.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                ]])
            )
        elif admin_action == "users":
            await query.edit_message_text(
                "👥 **مدیریت کاربران**\\n\\n🔧 این قسمت در حال توسعه است.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                ]])
            )
        elif admin_action == "stats":
            async with self.db_manager.session_scope() as session:
                # آمار کلی
                users_result = await session.execute(select(User))
                total_users = len(users_result.scalars().all())
                
                doctors_result = await session.execute(select(Doctor))
                total_doctors = len(doctors_result.scalars().all())
                
                subs_result = await session.execute(
                    select(Subscription).filter(Subscription.is_active == True)
                )
                total_subs = len(subs_result.scalars().all())
                
                text = f"""
📊 **آمار سیستم**

👥 **کاربران:** {total_users}
👨‍⚕️ **دکترها:** {total_doctors}
📝 **اشتراک‌های فعال:** {total_subs}

⏰ **آخرین بروزرسانی:** {datetime.now().strftime('%Y/%m/%d %H:%M')}
                """
                
                await query.edit_message_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
        else:
            await query.edit_message_text(
                f"🔧 **{admin_action}**\\n\\nدر حال توسعه...",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                ]])
            )
'''
    
    try:
        with open("src/telegram_bot/unified_handlers.py", 'w', encoding='utf-8') as f:
            f.write(handlers_content)
        print("✅ Unified handlers created")
        return True
    except Exception as e:
        print(f"❌ Error creating handlers: {e}")
        return False

def create_new_bot():
    """ایجاد bot جدید"""
    print("🤖 Creating new bot...")
    
    bot_content = '''"""
New Telegram Bot - معماری جدید و ساده
"""
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from typing import Optional

from src.telegram_bot.unified_handlers import UnifiedTelegramHandlers
from src.utils.logger import get_logger

logger = get_logger("NewTelegramBot")


class NewSlotHunterBot:
    """ربات جدید با معماری ساده و قابل اعتماد"""
    
    def __init__(self, token: str, db_manager):
        self.token = token
        self.db_manager = db_manager
        self.application: Optional[Application] = None
        self.handlers = UnifiedTelegramHandlers(db_manager)
    
    async def initialize(self):
        """راه‌اندازی ربات"""
        try:
            # ایجاد Application
            self.application = Application.builder().token(self.token).build()
            
            # اضافه کردن handlers
            self._setup_handlers()
            
            logger.info("✅ ربات جدید راه‌اندازی شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
            raise
    
    def _setup_handlers(self):
        """تنظیم handlers"""
        app = self.application
        
        # Command handlers
        app.add_handler(CommandHandler("start", self.handlers.start_command))
        app.add_handler(CommandHandler("help", self.handlers.help_command))
        app.add_handler(CommandHandler("doctors", self.handlers.doctors_command))
        app.add_handler(CommandHandler("admin", self.handlers.admin_command))
        
        # Callback handler
        app.add_handler(CallbackQueryHandler(self.handlers.handle_callback))
        
        logger.info("✅ Handlers تنظیم شدند")
    
    async def start_polling(self):
        """شروع polling"""
        try:
            logger.info("🔄 شروع polling...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # نگه داشتن ربات زنده
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"❌ خطا در polling: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """توقف ربات"""
        try:
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            logger.info("🛑 ربات متوقف شد")
        except Exception as e:
            logger.error(f"❌ خطا در توقف ربات: {e}")
    
    async def send_appointment_alert(self, doctor, appointments):
        """ارسال اطلاع‌رسانی نوبت"""
        try:
            from src.telegram_bot.messages import MessageFormatter
            from src.database.models import Subscription
            from sqlalchemy import select
            
            # دریافت مشترکین این دکتر
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(Subscription).filter(
                        Subscription.doctor_id == doctor.id,
                        Subscription.is_active == True
                    ).join(Subscription.user)
                )
                subscriptions = result.scalars().all()
                
                if not subscriptions:
                    logger.info(f"📭 هیچ مشترکی برای {doctor.name} وجود ندارد")
                    return
                
                # ایجاد پیام
                message_text = MessageFormatter.appointment_alert_message(doctor, appointments)
                
                # ارسال به همه مشترکین
                sent_count = 0
                for subscription in subscriptions:
                    try:
                        await self.application.bot.send_message(
                            chat_id=subscription.user.telegram_id,
                            text=message_text,
                            parse_mode='Markdown'
                        )
                        sent_count += 1
                    except Exception as e:
                        logger.error(f"❌ خطا در ارسال به {subscription.user.telegram_id}: {e}")
                
                logger.info(f"📤 پیام به {sent_count}/{len(subscriptions)} مشترک ارسال شد")
                
        except Exception as e:
            logger.error(f"❌ خطا در ارسال اطلاع‌رسانی: {e}")
'''
    
    try:
        with open("src/telegram_bot/new_bot.py", 'w', encoding='utf-8') as f:
            f.write(bot_content)
        print("✅ New bot created")
        return True
    except Exception as e:
        print(f"❌ Error creating bot: {e}")
        return False

def create_menu_handlers():
    """ایجاد menu handlers ساده"""
    print("📋 Creating menu handlers...")
    
    menu_content = '''"""
Simple Menu Handlers
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class SimpleMenuHandlers:
    """کلاس ساده برای منوها"""
    
    @staticmethod
    def get_main_menu():
        """منوی اصلی"""
        keyboard = [
            [InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors")],
            [InlineKeyboardButton("📝 اشتراک‌های من", callback_data="show_subscriptions")],
            [InlineKeyboardButton("🔔 اشتراک جدید", callback_data="new_subscription")],
            [InlineKeyboardButton("📊 وضعیت من", callback_data="my_status")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_doctors_keyboard(doctors):
        """کیبورد لیست دکترها"""
        keyboard = []
        for doctor in doctors:
            keyboard.append([
                InlineKeyboardButton(
                    f"👨‍⚕️ {doctor.name}",
                    callback_data=f"doctor_info_{doctor.id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_doctor_actions_keyboard(doctor_id, is_subscribed):
        """کیبورد عملیات دکتر"""
        keyboard = []
        
        if is_subscribed:
            keyboard.append([
                InlineKeyboardButton("🗑️ لغو اشتراک", callback_data=f"unsubscribe_{doctor_id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("📝 اشتراک", callback_data=f"subscribe_{doctor_id}")
            ])
        
        keyboard.extend([
            [InlineKeyboardButton("🔙 لیست دکترها", callback_data="show_doctors")],
            [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_back_to_main_keyboard():
        """کیبورد بازگشت به منوی اصلی"""
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
        ]])
'''
    
    try:
        with open("src/telegram_bot/simple_menu.py", 'w', encoding='utf-8') as f:
            f.write(menu_content)
        print("✅ Simple menu handlers created")
        return True
    except Exception as e:
        print(f"❌ Error creating menu handlers: {e}")
        return False

def main():
    print("🏗️ P24_SlotHunter Bot Rebuilder")
    print("=" * 50)
    
    print("این اسکریپت معماری جدید و ساده‌ای برای ربات ایجاد می‌کند.")
    print("پس از اجرا، فایل‌های زیر ایجاد می‌شوند:")
    print("- src/telegram_bot/unified_handlers.py")
    print("- src/telegram_bot/new_bot.py") 
    print("- src/telegram_bot/simple_menu.py")
    print()
    
    if create_new_bot_architecture():
        print("\n🎉 معماری جدید ایجاد شد!")
        print("\n📋 مراحل بعدی:")
        print("1. توقف سرویس: ./server_manager.sh stop")
        print("2. جایگزینی bot.py با new_bot.py")
        print("3. به‌روزرسانی main.py برای استفاده از NewSlotHunterBot")
        print("4. شروع مجدد: ./server_manager.sh start")
    else:
        print("\n❌ خطا در ایجاد معماری جدید")

if __name__ == "__main__":
    main()