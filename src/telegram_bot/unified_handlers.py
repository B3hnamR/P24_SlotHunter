"""
Enhanced Telegram Handlers - شامل مدیریت دکترها
"""
import asyncio
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime

from src.database.models import User, Doctor, Subscription, DoctorCenter, DoctorService
from src.telegram_bot.messages import MessageFormatter
from src.telegram_bot.doctor_handlers import DoctorHandlers
from src.api.doctor_manager import DoctorManager
from src.utils.logger import get_logger

logger = get_logger("EnhancedHandlers")


class UnifiedTelegramHandlers:
    """کلاس پیشرفته handlers تلگرام - شامل مدیریت دکترها"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.doctor_handlers = DoctorHandlers(db_manager)
        self.doctor_manager = DoctorManager(db_manager)
    
    # ==================== Command Handlers ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /start ساده"""
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
                    is_new_user = True
                else:
                    db_user.username = user.username
                    db_user.first_name = user.first_name
                    db_user.last_name = user.last_name
                    db_user.is_active = True
                    db_user.last_activity = datetime.utcnow()
                    is_new_user = False
            
            # پیام خوش‌آمدگویی ساده
            if is_new_user:
                welcome_text = f"""
🎯 **سلام {user.first_name}! خوش آمدید** 🎉

به **ربات نوبت‌یاب پذیرش۲۴** خوش آمدید!

🔥 **امکانات:**
• 👨‍⚕️ **مشاهده دکترها** - لیست دکترهای موجود
• 📝 **اشتراک در دکتر** - برای رصد نوبت‌های خالی

💡 **نکته:** ربات ۲۴/۷ نوبت‌های خالی را رصد می‌کند!

⚠️ **توجه:** دکترها توسط ادمین از طریق فایل تنظیمات اضافه می‌شوند.
                """
            else:
                welcome_text = f"""
👋 **سلام مجدد {user.first_name}!**

خوشحالیم که دوباره اینجا هستید! 

📊 **وضعیت سریع:**
• آخرین بازدید: {db_user.last_activity.strftime('%Y/%m/%d %H:%M') if db_user.last_activity else 'اولین بار'}
• حساب کاربری: ✅ فعال

🚀 **آماده برای شروع؟**
                """
            
            # منوی اصلی - فقط ق��بلیت‌های اصلی
            keyboard = [
                [InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors")],
                [InlineKeyboardButton("📝 اشتراک‌های من", callback_data="my_subscriptions")],
                [InlineKeyboardButton("🆕 اضافه کردن دکتر", callback_data="add_doctor")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # ارسال پیام
            await update.message.reply_text(
                welcome_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # تنظیم منوی دائمی ساده
            await self._setup_simple_menu(update)
            
        except Exception as e:
            logger.error(f"❌ خطا در start: {e}")
            await self._send_error_message(update.message, str(e))
    
    async def _setup_simple_menu(self, update):
        """تنظیم منوی دائمی ساده"""
        keyboard = [
            [
                KeyboardButton("👨‍⚕️ دکترها"),
                KeyboardButton("📝 اشتراک‌ها")
            ]
        ]
        
        reply_markup = ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder="انتخاب کنید..."
        )
        
        await update.message.reply_text(
            "📱 **منوی سریع فعال شد!**\n\nاز دکمه‌های پایین صفحه استفاده کنید.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /help ساده"""
        try:
            help_text = """
📚 **راهنمای ربات نوبت‌یاب**

🎯 **قابلیت‌های اصلی:**

👨‍⚕️ **مشاهده دکترها**
• مشاهده لیست دکترهای موجود در سیستم
• اطلاعات کامل هر دکتر

📝 **اشتراک در دکتر**
• اشتراک برای رصد نوبت‌های خالی
• اطلاع‌رسانی فوری نوبت‌های جدید
• مدیریت اشتراک‌ها

🔧 **مدیریت دکترها**
• دکترها توسط ادمین از طریق فایل config/config.yaml اضافه می‌شوند
• هر دکتر نیاز به اطلاعات API دارد (center_id, service_id, etc.)

💡 **نکات:**
• نوبت‌ها سریع تمام می‌شوند، آماده باشید!
• می‌توانید در چندین دکتر همزمان مشترک شوید
• ربات فقط از API پذیرش۲۴ استفاده می‌کند
            """
            
            keyboard = [
                [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                help_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ خطا در help: {e}")
            await self._send_error_message(update.message, str(e))
    
    async def doctors_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /doctors"""
        await self._show_doctors_list(update.message)
    
    # ==================== Message Handlers ====================
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پیام‌های متنی ساده"""
        try:
            text = update.message.text
            user_id = update.effective_user.id
            
            if text == "👨‍⚕️ دکت��ها":
                await self._show_doctors_list(update.message)
            elif text == "📝 اشتراک‌ها":
                await self._show_subscriptions(update.message, user_id)
            elif self._is_doctor_url(text):
                # اگر پیام شبیه URL دکتر است، سعی کن اضافه کنی
                await self._handle_doctor_url(update.message, text, user_id)
            else:
                # پیام پیش‌فرض
                await update.message.reply_text(
                    "🤔 **متوجه نشدم!**\n\nلطفاً از دکمه‌های منو استفاده کنید.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در پیام متنی: {e}")
            await self._send_error_message(update.message, str(e))
    
    # ==================== Callback Handlers ====================
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت callback های ساده"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            
            if data == "show_doctors":
                await self._callback_show_doctors(query)
            elif data == "my_subscriptions":
                await self._callback_show_subscriptions(query, user_id)
            elif data.startswith("doctor_info_"):
                await self._callback_doctor_info(query, data, user_id)
            elif data.startswith("subscribe_"):
                await self._callback_subscribe(query, data, user_id)
            elif data.startswith("unsubscribe_"):
                await self._callback_unsubscribe(query, data, user_id)
            elif data == "add_doctor":
                await self._callback_add_doctor(query)
            elif data.startswith("check_appointments_"):
                await self.doctor_handlers.check_doctor_appointments(update, context)
            elif data.startswith("quick_reserve_"):
                await self.doctor_handlers.quick_reserve_placeholder(update, context)
            elif data.startswith("refresh_doctor_"):
                await self._callback_refresh_doctor(query, data)
            elif data.startswith("delete_doctor_"):
                await self._callback_delete_doctor(query, data)
            elif data == "back_to_main":
                await self._callback_back_to_main(query, user_id)
            else:
                await query.edit_message_text(
                    "❌ **دستور نامشخص**\n\nلطفاً از منوی اصلی استفاده کنید.",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
            
        except Exception as e:
            logger.error(f"❌ خطا در callback: {e}")
            try:
                await query.edit_message_text(
                    f"❌ **خطا در پردازش**\n\n`{str(e)}`",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
            except:
                pass
    
    # ==================== Core Functions ====================
    
    async def _show_doctors_list(self, message):
        """نمایش لیست دکترها از دیتابیس"""
        async with self.db_manager.session_scope() as session:
            result = await session.execute(
                select(Doctor).filter(Doctor.is_active == True)
            )
            doctors = result.scalars().all()
            
            if not doctors:
                text = """
❌ **هیچ دکتری موجود نیست**

هنوز هیچ دکتری در سیستم اضافه نشده است.

🔧 **برای اضافه کردن دکتر:**
• ادمین باید دکتر را در فایل `config/config.yaml` اضافه کند
• اطلاعات API مورد نیاز: center_id, service_id, user_center_id, terminal_id
• بعد از اضافه کردن، ربات را restart کنید

💡 **نکته:** این ربات فقط از API پذیرش۲۴ استفاده می‌کند و نیاز به اطلاعات دقیق API دارد.
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
                
                await message.reply_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            
            text = f"""
👨‍⚕️ **لیست دکترها ({len(doctors)} دکتر)**

✅ **دکترهای فعال در سیستم:**

💡 **راهنما:** روی نام دکتر کلیک کنید تا اطلاعات کامل و گزینه اشتراک را مشاهده کنید.

📋 **دکترهای موجود:**
            """
            
            # ایجاد keyboard
            keyboard = []
            for doctor in doctors:
                specialty_emoji = self._get_specialty_emoji(doctor.specialty)
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"{specialty_emoji} {doctor.name}",
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
    
    async def _show_subscriptions(self, message, user_id):
        """نمایش اشتراک‌ها"""
        async with self.db_manager.session_scope() as session:
            result = await session.execute(
                select(User).filter(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await message.reply_text("❌ کاربر یافت نشد.")
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
                text = """
📝 **اشتراک‌های من**

❌ شما در هیچ دکتری مشترک نیستید.

💡 **برای اشتراک:**
1. از منوی "👨‍⚕️ دکترها" استفاده کنید
2. روی نام دکتر مورد نظر کلیک کنید
3. دکمه "📝 اشتراک" را بزنید

🔔 **اشتراک یعنی:** ربات ۲۴/۷ نوبت‌های خالی آن دکتر را رصد می‌کند و فوراً به شما اطلاع می‌دهد.
                """
                keyboard = [
                    [InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
            else:
                text = f"""
📝 **اشتراک‌های من ({len(subscriptions)} اشتراک فعال)**

✅ **دکترهای مشترک:**

                """
                
                keyboard = []
                for sub in subscriptions:
                    specialty_emoji = self._get_specialty_emoji(sub.doctor.specialty)
                    text += f"• {specialty_emoji} **{sub.doctor.name}**\n"
                    text += f"  🏥 {sub.doctor.specialty or 'عمومی'}\n"
                    text += f"  📅 تاریخ اشتراک: {sub.created_at.strftime('%Y/%m/%d') if sub.created_at else 'نامشخص'}\n\n"
                    
                    keyboard.append([
                        InlineKeyboardButton(
                            f"🗑️ لغو {sub.doctor.name}",
                            callback_data=f"unsubscribe_{sub.doctor.id}"
                        )
                    ])
                
                text += """
🔔 **وضعیت رصد:** ربات در حال رصد نوبت‌های خالی این دکترها است.
                """
                
                keyboard.extend([
                    [InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.reply_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    # ==================== Callback Methods ====================
    
    async def _callback_show_doctors(self, query):
        """callback نمایش دکترها"""
        await self._show_doctors_list(query.message)
    
    async def _callback_show_subscriptions(self, query, user_id):
        """callback نمایش اشتراک‌ها"""
        await self._show_subscriptions(query.message, user_id)
    
    async def _callback_doctor_info(self, query, data, user_id):
        """callback اطلاعات دکتر"""
        try:
            doctor_id = int(data.split("_")[2])
            
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(Doctor)
                    .options(selectinload(Doctor.centers).selectinload(DoctorCenter.services))
                    .filter(Doctor.id == doctor_id)
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
                
                specialty_emoji = self._get_specialty_emoji(doctor.specialty)
                
                # دریافت اطلاعات اول��ن مرکز (اگر وجود دارد)
                center_info = ""
                if doctor.centers:
                    first_center = doctor.centers[0]
                    center_info = f"""
🏢 **مرکز:** {first_center.center_name}
📍 **آدرس:** {first_center.center_address or 'نامشخص'}
📞 **تلفن:** {first_center.center_phone or 'نامشخص'}"""
                    
                    if len(doctor.centers) > 1:
                        center_info += f"\n🏥 **تعداد مراکز:** {len(doctor.centers)} مرکز"
                else:
                    center_info = "\n🏢 **مرکز:** نامشخص"
                
                text = f"""
{specialty_emoji} **{doctor.name}**

🏥 **تخصص:** {doctor.specialty or 'عمومی'}{center_info}

🔗 **لینک صفحه دکتر:**
https://www.paziresh24.com/dr/{doctor.slug}/

📊 **وضعیت اشتراک:**
{'✅ شما مشترک هستید' if is_subscribed else '❌ شما مشترک نیستید'}

🔔 **اشتراک یعنی:** رصد خودکار نوبت‌های خالی و اطلاع‌رسانی فوری

🤖 **نحوه کار:** ربات از API پذیرش۲۴ استفاده می‌کند و هر 30 ثانیه نوبت‌ها را بررسی می‌کند.
                """
                
                keyboard = []
                if is_subscribed:
                    keyboard.append([
                        InlineKeyboardButton("🗑️ لغو اشتراک", callback_data=f"unsubscribe_{doctor.id}")
                    ])
                else:
                    keyboard.append([
                        InlineKeyboardButton("📝 اشتراک در این دکتر", callback_data=f"subscribe_{doctor.id}")
                    ])
                
                keyboard.extend([
                    [InlineKeyboardButton("🔙 لیست دکترها", callback_data="show_doctors")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
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
                
                specialty_emoji = self._get_specialty_emoji(doctor.specialty)
                
                text = f"""
✅ **اشتراک موفق!**

شما با موفقیت در دکتر **{specialty_emoji} {doctor.name}** مشترک شدید.

🔔 **از این پس:**
• ربات ۲۴/۷ نوبت‌های خالی این دکتر را رصد می‌کند
• هر نوبت خالی فوراً به شما اطلاع داده می‌شود
• پیام شامل لینک مستقیم رزرو خواهد بود

🤖 **نح��ه کار:**
• ربات از API پذیرش۲۴ استفاده می‌کند
• هر 30 ثانیه نوبت‌ها بررسی می‌شوند
• اطلاع‌رسانی فوری در صورت پیدا شدن نوبت

💡 **نکته مهم:** نوبت‌ها معمولاً سریع تمام می‌شوند، پس آماده باشید!
                """
                
                keyboard = [
                    [InlineKeyboardButton("👨‍⚕️ اطلاعات دکتر", callback_data=f"doctor_info_{doctor.id}")],
                    [InlineKeyboardButton("📝 اشتراک‌های من", callback_data="my_subscriptions")],
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
                
                specialty_emoji = self._get_specialty_emoji(doctor.specialty)
                
                text = f"""
✅ **لغو اشتراک موفق!**

اشتراک شما از دکتر **{specialty_emoji} {doctor.name}** لغو شد.

🔕 **از این پس:**
• دیگر اطلاع‌رسانی نوبت‌های این دکتر دریافت نخواهید کرد
• رصد خودکار متوقف شد

💡 **در صورت نیاز:** می‌توانید مجدداً مشترک شوید.
                """
                
                keyboard = [
                    [InlineKeyboardButton("📝 اشتراک مجدد", callback_data=f"subscribe_{doctor.id}")],
                    [InlineKeyboardButton("📝 اشتراک‌های من", callback_data="my_subscriptions")],
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
    
    async def _callback_add_doctor(self, query):
        """callback اضافه کردن دکتر"""
        text = """
🆕 **اضافه کردن دکتر جدید**

لطفاً لینک صفحه دکتر در پذیرش۲۴ را ارسال کنید.

📋 **فرمت‌های قابل قبول:**

1️⃣ **لینک کامل:**
`https://www.paziresh24.com/dr/دکتر-نام-خانوادگی-0/`

2️⃣ **لینک کوتاه:**
`dr/دکتر-نام-خانوادگی-0/`

3️⃣ **فقط slug:**
`دکتر-نام-خانوادگی-0`

💡 **نکته:** ربات تمام اطلاعات مورد نیاز را ��ز صفحه دکتر استخراج می‌کند.

🔄 **برای ادامه:** لینک دکتر را در پیام بعدی ارسال کنید
        """
        
        keyboard = [
            [InlineKeyboardButton("❌ لغو", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def _callback_refresh_doctor(self, query, data):
        """callback به‌روزرسانی دکتر"""
        try:
            doctor_id = int(data.split("_")[-1])
            
            await query.edit_message_text(
                "🔄 **در حال به‌روزرسانی اطلاعات دکتر...**\n\nلطفاً صبر کنید...",
                parse_mode='Markdown'
            )
            
            success, message = await self.doctor_manager.refresh_doctor_data(doctor_id)
            
            if success:
                text = f"✅ **به‌روزرسانی موفق!**\n\n{message}"
                keyboard = [
                    [InlineKeyboardButton("👨‍⚕️ مشاهده اطلاعات", callback_data=f"doctor_info_{doctor_id}")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
            else:
                text = f"❌ **خطا در به‌روزرسانی**\n\n{message}"
                keyboard = [
                    [InlineKeyboardButton("🔄 تلاش مجدد", callback_data=f"refresh_doctor_{doctor_id}")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"❌ خطا در به‌روزرسانی دکتر: {e}")
            await query.edit_message_text(f"❌ خطا: {str(e)}")
    
    async def _callback_delete_doctor(self, query, data):
        """callback حذف دکتر"""
        try:
            doctor_id = int(data.split("_")[-1])
            
            # دریافت اطلاعات دکتر
            doctor = await self.doctor_manager.get_doctor_with_details(doctor_id)
            if not doctor:
                await query.edit_message_text("❌ دکتر یافت نشد.")
                return
            
            text = f"""
⚠️ **تأیید حذف دکتر**

آیا مطمئن هستید که می‌خواهید دکتر **{doctor.name}** را حذف کنید؟

🔴 **توجه:**
• این عمل قابل بازگشت نیست
• تمام اشتراک‌های مربوط به این دکتر لغو می‌شود
• اطلاعات دکتر از سیستم حذف می‌شود

👥 **مشترکین فعال:** {doctor.subscription_count} نفر
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ بله، حذف کن", callback_data=f"confirm_delete_{doctor_id}"),
                    InlineKeyboardButton("❌ لغو", callback_data=f"doctor_info_{doctor_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ خطا در حذف دکتر: {e}")
            await query.edit_message_text(f"❌ خطا: {str(e)}")
    
    async def _callback_back_to_main(self, query, user_id):
        """callback بازگشت به منوی اصلی"""
        keyboard = [
            [InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors")],
            [InlineKeyboardButton("📝 اشتراک‌های من", callback_data="my_subscriptions")],
            [InlineKeyboardButton("🆕 اضافه کردن دکتر", callback_data="add_doctor")]
        ]
        
        text = """
🎯 **منوی اصلی**

از دکمه‌های زیر برای استفاده از ربات استفاده کنید:

💡 **نکته:** از منوی پایین صفحه نیز می‌توانید استفاده کنید.

🤖 **ربات فقط از API پذیرش۲۴ استفاده می‌کند.**
        """
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ==================== Utility Methods ====================
    
    def _get_specialty_emoji(self, specialty):
        """دریافت ایموجی مناسب برای تخصص"""
        if not specialty:
            return "👨‍⚕️"
        
        specialty_lower = specialty.lower()
        
        emoji_map = {
            "قلب": "❤️", "کاردیولوژی": "❤️",
            "مغز": "🧠", "نورولوژی": "🧠",
            "چشم": "👁️", "افتالمولوژی": "👁️",
            "دندان": "🦷",
            "کودکان": "👶", "اطفال": "👶",
            "زنان": "👩", "زایمان": "👩",
            "ارتوپدی": "🦴", "استخوان": "🦴",
            "پوست": "🧴", "درمتولوژی": "🧴",
            "گوش": "👂", "حلق": "👂"
        }
        
        for keyword, emoji in emoji_map.items():
            if keyword in specialty_lower:
                return emoji
        
        return "👨‍⚕️"
    
    def _is_doctor_url(self, text: str) -> bool:
        """بررسی اینکه آیا متن شبیه URL دکتر است یا نه"""
        if not text:
            return False
        
        text = text.strip()
        
        # بررسی فرمت‌های مختلف URL دکتر
        patterns = [
            # لینک کامل
            r'https?://(?:www\.)?paziresh24\.com/dr/[^/\s]+/?',
            # لینک کوتاه
            r'^dr/[^/\s]+/?$',
            # فقط slug (شامل دکتر- یا حروف فارسی/انگلیسی و خط تیره)
            r'^[آ-یa-zA-Z0-9\-_]+$'
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    async def _handle_doctor_url(self, message, url: str, user_id: int):
        """پردازش URL دکتر و اضافه کردن به سیستم"""
        try:
            # ارسال پیام در حال پردازش
            processing_message = await message.reply_text(
                "🔄 **در حال پردازش...**\n\n"
                "⏳ دریافت اطلاعات دکتر از پذیرش۲۴\n"
                "📊 استخراج اطلاعات API\n"
                "💾 ذخیره در دیتابیس\n\n"
                "لطفاً صبر کنید...",
                parse_mode='Markdown'
            )
            
            # اعتبارسنجی URL
            is_valid, validation_message = self.doctor_manager.validate_doctor_url(url)
            if not is_valid:
                await processing_message.edit_text(
                    f"❌ **URL نامعتبر**\n\n{validation_message}\n\n"
                    "لطفاً URL معتبری ارسال کنید.",
                    parse_mode='Markdown'
                )
                return
            
            # اضافه کردن دکتر
            success, message_text, doctor = await self.doctor_manager.add_doctor_from_url(url, user_id)
            
            if success:
                # موفقیت
                keyboard = [
                    [InlineKeyboardButton("👨‍⚕️ مشاهده دکتر", callback_data=f"doctor_info_{doctor.id}")],
                    [InlineKeyboardButton("📝 اشتراک در این دکتر", callback_data=f"subscribe_{doctor.id}")],
                    [InlineKeyboardButton("🔍 دریافت نوبت‌های خالی", callback_data=f"check_appointments_{doctor.id}")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await processing_message.edit_text(
                    message_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
                logger.info(f"✅ دکتر جدید اضافه شد: {doctor.name} توسط {message.from_user.first_name}")
                
            else:
                # خطا
                keyboard = [
                    [InlineKeyboardButton("🔄 تلاش مجدد", callback_data="add_doctor")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await processing_message.edit_text(
                    f"❌ **خطا در اضافه کردن دکتر**\n\n{message_text}",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            
        except Exception as e:
            logger.error(f"❌ خطا در پردازش URL دکتر: {e}")
            await message.reply_text(
                f"❌ **خطا در پردازش**\n\n`{str(e)}`\n\n"
                "لطفاً دوباره تلاش کنید.",
                parse_mode='Markdown'
            )
    
    async def _send_error_message(self, message, error_text):
        """ارسال پیام خطا"""
        error_message = f"""
❌ **خطا در پردازش درخواست**

🔍 **جزئیات خطا:**
`{error_text}`

🔧 **راه‌حل:**
• دوباره تلاش کنید
• از منوی اصلی استفاده کنید

⏰ **زمان خطا:** {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
        """
        
        keyboard = [
            [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
        ]
        
        await message.reply_text(
            error_message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )