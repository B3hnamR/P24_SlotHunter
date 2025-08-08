"""
Enhanced Telegram Handlers - نسخه بهبود یافته با متن‌های جذاب
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
    """کلاس پیشرفته handlers تلگرام - نسخه بهبود یافته"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.doctor_handlers = DoctorHandlers(db_manager)
        self.doctor_manager = DoctorManager(db_manager)
    
    # ==================== Command Handlers ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /start با متن‌های بهبود یافته"""
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
            
            # پیام خوش‌آمدگویی بهبود یافته
            if is_new_user:
                welcome_text = MessageFormatter.welcome_message(user.first_name, is_returning=False)
            else:
                welcome_text = MessageFormatter.returning_user_message(
                    user.first_name, 
                    db_user.last_activity
                )
            
            # منوی اصلی بهبود یافته
            keyboard = [
                [InlineKeyboardButton("👨‍⚕️ دکترها", callback_data="show_doctors")],
                [InlineKeyboardButton("📊 وضعیت من", callback_data="my_subscriptions")],
                [InlineKeyboardButton("🆕 اضافه کردن دکتر", callback_data="add_doctor")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # ارسال پیام
            await update.message.reply_text(
                welcome_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
            # تنظیم منوی دائمی بهبود یافته
            await self._setup_improved_menu(update)
            
        except Exception as e:
            logger.error(f"❌ خطا در start: {e}")
            await self._send_error_message(update.message, str(e))
    
    async def _setup_improved_menu(self, update):
        """تنظیم منوی دائمی بهبود یافته"""
        keyboard = [
            [
                KeyboardButton("👨‍⚕️ دکترها"),
                KeyboardButton("📊 وضعیت من")
            ]
        ]
        
        reply_markup = ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder="یکی رو انتخاب کن..."
        )
        
        await update.message.reply_text(
            "📱 **منوی سریع فعال شد!**\n\nاز دکمه‌های پایین استفاده کن.",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /help بهبود یافته"""
        try:
            help_text = MessageFormatter.help_message()
            
            keyboard = [
                [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                help_text,
                parse_mode='HTML',
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
        """مدیریت پیام‌های متنی بهبود یافته"""
        try:
            text = update.message.text
            user_id = update.effective_user.id
            
            if text == "👨‍⚕️ دکترها":
                await self._show_doctors_list(update.message)
            elif text in ["📊 وضعیت من", "📝 اشتراک‌ها"]:
                await self._show_subscriptions(update.message, user_id)
            elif self._is_doctor_url(text):
                # اگر پیام شبیه URL دکتر است، سعی کن اضافه کنی
                await self._handle_doctor_url(update.message, text, user_id)
            else:
                # پیام پیش‌فرض بهبود یافته
                await update.message.reply_text(
                    "🤔 **متوجه نشدم چی گفتی!**\n\n"
                    "💡 **چیکار می‌تونی بکنی؟**\n"
                    "• از دکمه‌های پایین استفاده کن\n"
                    "• یا لینک دکتر رو بفرست تا اضافه کنم\n\n"
                    "🆘 **کمک می‌خوای؟** /help بزن",
                    parse_mode='HTML'
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در پیام متنی: {e}")
            await self._send_error_message(update.message, str(e))
    
    # ==================== Callback Handlers ====================
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت callback های بهبود یافته"""
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
            elif data == "back_to_main":
                await self._callback_back_to_main(query, user_id)
            else:
                await query.edit_message_text(
                    "❌ **دستور نامشخص!**\n\n"
                    "😅 یه چیزی اشتباه شد. از منوی اصلی استفاده کن.",
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
            
        except Exception as e:
            logger.error(f"❌ خطا در callback: {e}")
            try:
                await query.edit_message_text(
                    MessageFormatter.error_message(f"مشکلی پیش اومد: {str(e)}"),
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
            except:
                pass
    
    # ==================== Core Functions ====================
    
    async def _show_doctors_list(self, message):
        """نمایش لیست دکترها بهبود یافته"""
        try:
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(Doctor).filter(Doctor.is_active == True)
                )
                doctors = result.scalars().all()
                
                if not doctors:
                    text = """
😔 **هنوز دکتری اضافه نشده!**

🤔 **چیکار کنی؟**
می‌تونی خودت دکتر اضافه کنی! فقط لینک صفحه دکتر رو از پذیرش۲۴ برام بفرست.

📋 **مثال:**
`https://www.paziresh24.com/dr/دکتر-احمد-محمدی-0/`

💡 **یا از دکمه زیر استفاده کن:**
                    """
                    
                    keyboard = [
                        [InlineKeyboardButton("🆕 اضافه کردن دکتر", callback_data="add_doctor")],
                        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                    ]
                    
                    await message.reply_text(
                        text,
                        parse_mode='HTML',
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    return
                
                text = f"""
👨‍⚕️ **دکترهای موجود ({len(doctors)} دکتر)**

🎯 **چطور کار می‌کنه؟**
روی اسم دکتر کلیک کن تا اطلاعات کامل و گزینه ثبت‌نام رو ببینی.

✨ **دکترهای فعال:**
                """
                
                # ایجاد keyboard بهبود یافته
                keyboard = []
                for doctor in doctors:
                    specialty_emoji = self._get_specialty_emoji(doctor.specialty)
                    
                    keyboard.append([
                        InlineKeyboardButton(
                            f"{specialty_emoji} {doctor.name}",
                            callback_data=f"doctor_info_{doctor.id}"
                        )
                    ])
                
                keyboard.extend([
                    [InlineKeyboardButton("🆕 اضافه کردن دکتر", callback_data="add_doctor")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await message.reply_text(
                    text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
        except Exception as e:
            logger.error(f"❌ خطا در نمایش لیست دکترها: {e}")
            await self._send_error_message(message, str(e))
    
    async def _show_subscriptions(self, message, user_id):
        """نمایش اشتراک‌ها بهبود یافته"""
        try:
            async with self.db_manager.session_scope() as session:
                # دریافت کاربر
                result = await session.execute(
                    select(User).filter(User.telegram_id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    await message.reply_text("❌ کاربر یافت نشد. لطفاً /start کنید.")
                    return
                
                # دریافت اشتراک‌های فعال
                sub_result = await session.execute(
                    select(Subscription)
                    .options(selectinload(Subscription.doctor))
                    .filter(
                        Subscription.user_id == user.id,
                        Subscription.is_active == True
                    )
                )
                subscriptions = sub_result.scalars().all()
                
                if not subscriptions:
                    text = """
📊 **وضعیت ثبت‌نام‌های تو**

😔 **هنوز توی هیچ دکتری ثبت‌نام نکردی!**

🤔 **چیکار کنی؟**
1️⃣ برو قسمت "👨‍⚕️ دکترها"
2️⃣ دکتر مورد نظرت رو انتخاب کن
3️⃣ روی "📝 ثبت‌نام" بزن

🔔 **بعدش چی میشه؟**
من مداوم نوبت‌های خالی اون دکتر رو چک می‌کنم و تا پیدا شد، فوری بهت خبر می‌دم!
                    """
                    keyboard = [
                        [InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors")],
                        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                    ]
                else:
                    text = f"""
📊 **وضعیت ثبت‌نام‌های تو**

✅ **{len(subscriptions)} دکتر در حال رصد:**

🤖 **وضعیت:** من مداوم نوبت‌های خالی این دکترها رو چک می‌کنم!

                    """
                    
                    keyboard = []
                    for sub in subscriptions:
                        specialty_emoji = self._get_specialty_emoji(sub.doctor.specialty)
                        text += f"• {specialty_emoji} **{sub.doctor.name}**\n"
                        text += f"  🩺 {sub.doctor.specialty or 'عمومی'}\n"
                        text += f"  📅 ثبت‌نام: {sub.created_at.strftime('%Y/%m/%d') if sub.created_at else 'نامشخص'}\n\n"
                        
                        keyboard.append([
                            InlineKeyboardButton(
                                f"🗑️ لغو {sub.doctor.name}",
                                callback_data=f"unsubscribe_{sub.doctor.id}"
                            )
                        ])
                    
                    text += """
💡 **نکته:** نوبت‌ها معمولاً خیلی سریع تموم میشن، پس آماده باش!
                    """
                    
                    keyboard.extend([
                        [InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors")],
                        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                    ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await message.reply_text(
                    text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
        except Exception as e:
            logger.error(f"❌ خطا در نمایش اشتراک‌ها: {e}")
            await self._send_error_message(message, str(e))
    
    # ==================== Callback Methods ====================
    
    async def _callback_show_doctors(self, query):
        """callback نمایش دکترها"""
        await self._show_doctors_list(query.message)
    
    async def _callback_show_subscriptions(self, query, user_id):
        """callback نمایش اشتراک‌ها"""
        await self._show_subscriptions(query.message, user_id)
    
    async def _callback_doctor_info(self, query, data, user_id):
        """callback اطلاعات دکتر بهب��د یافته"""
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
                
                # دریافت اطلاعات مرکز
                center_info = ""
                if doctor.centers:
                    first_center = doctor.centers[0]
                    center_info = f"""
🏥 **مطب/کلینیک:** {first_center.center_name}
📍 **آدرس:** {first_center.center_address or 'آدرس موجود نیست'}
📞 **تلفن:** {first_center.center_phone or 'شماره موجود نیست'}"""
                    
                    if len(doctor.centers) > 1:
                        center_info += f"\n🏢 **تعداد مراکز:** {len(doctor.centers)} مرکز"
                else:
                    center_info = "\n🏥 **مطب/کلینیک:** اطلاعات موجود نیست"
                
                text = f"""
{specialty_emoji} **{doctor.name}**

🩺 **تخصص:** {doctor.specialty or 'عمومی'}{center_info}

🔗 **لینک صفحه دکتر:**
https://www.paziresh24.com/dr/{doctor.slug}/

📊 **وضعیت ثبت‌نام شما:**
{'✅ ثبت‌نام کردی' if is_subscribed else '❌ ثبت‌نام نکردی'}

🤖 **چطور کار می‌کنه؟**
اگه ثبت‌نام کنی، من هر چند دقیقه یه بار نوبت‌های خالی این دکتر رو چک می‌کنم و تا پیدا شد، فوری بهت خبر می‌دم!

💡 **نکته:** نوبت‌ها خیلی سریع تموم میشن، پس آماده باش!
                """
                
                keyboard = []
                if is_subscribed:
                    keyboard.append([
                        InlineKeyboardButton("🗑️ لغو ثبت‌نام", callback_data=f"unsubscribe_{doctor.id}")
                    ])
                else:
                    keyboard.append([
                        InlineKeyboardButton("📝 ثبت‌نام در این دکتر", callback_data=f"subscribe_{doctor.id}")
                    ])
                
                keyboard.extend([
                    [InlineKeyboardButton("🔙 لیست دکترها", callback_data="show_doctors")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در اطلاعات دکتر: {e}")
            await query.edit_message_text(MessageFormatter.error_message(str(e)))
    
    async def _callback_subscribe(self, query, data, user_id):
        """callback اشتراک بهبود یافته"""
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
                            MessageFormatter.error_message(f"قبلاً توی {doctor.name} ثبت‌نام کردی!"),
                            parse_mode='HTML'
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
                
                text = MessageFormatter.subscription_success_message(doctor)
                
                keyboard = [
                    [InlineKeyboardButton("👨‍⚕️ اطلاعات دکتر", callback_data=f"doctor_info_{doctor.id}")],
                    [InlineKeyboardButton("📊 وضعیت من", callback_data="my_subscriptions")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                
                logger.info(f"📝 اشتراک جدید: {user.full_name} -> {doctor.name}")
                
        except Exception as e:
            logger.error(f"❌ خطا در اشتراک: {e}")
            await query.edit_message_text(MessageFormatter.error_message(str(e)))
    
    async def _callback_unsubscribe(self, query, data, user_id):
        """callback لغو اشتراک بهبود یافته"""
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
                        MessageFormatter.error_message(f"توی {doctor.name} ثبت‌نام نکردی که!"),
                        parse_mode='HTML'
                    )
                    return
                
                # لغو اشتراک
                subscription.is_active = False
                
                text = MessageFormatter.unsubscription_success_message(doctor)
                
                keyboard = [
                    [InlineKeyboardButton("📝 ثبت‌نام مجدد", callback_data=f"subscribe_{doctor.id}")],
                    [InlineKeyboardButton("📊 وضعیت من", callback_data="my_subscriptions")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                
                logger.info(f"🗑️ لغو اشتراک: {user.full_name} -> {doctor.name}")
                
        except Exception as e:
            logger.error(f"❌ خطا در لغو اشتراک: {e}")
            await query.edit_message_text(MessageFormatter.error_message(str(e)))
    
    async def _callback_add_doctor(self, query):
        """callback اضافه کردن دکتر بهبود یافته"""
        text = MessageFormatter.add_doctor_prompt_message()
        
        keyboard = [
            [InlineKeyboardButton("❌ لغو", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    async def _callback_back_to_main(self, query, user_id):
        """callback بازگشت به منوی اصلی بهبود یافته"""
        keyboard = [
            [InlineKeyboardButton("👨‍⚕️ دکترها", callback_data="show_doctors")],
            [InlineKeyboardButton("📊 وضعیت من", callback_data="my_subscriptions")],
            [InlineKeyboardButton("🆕 اضافه کردن دکتر", callback_data="add_doctor")]
        ]
        
        text = """
🎯 **منوی اصلی**

🤖 **من چیکار می‌کنم؟**
نوبت‌های خالی دکترها رو برات پیدا می‌کنم!

💡 **چطور استفاده کنی؟**
از دکمه‌های زیر یا منوی پایین صفحه استفاده کن.

⚡ **سریع و آسان!**
        """
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    # ==================== Utility Methods ====================
    
    def _get_specialty_emoji(self, specialty):
        """دریافت ایموجی مناسب برای تخصص"""
        if not specialty:
            return "👨‍⚕️"
        
        specialty_lower = specialty.lower()
        
        emoji_map = {
            "قلب": "❤️", "کاردیولوژی": "❤️", "قلبی": "❤️",
            "مغز": "🧠", "نورولوژی": "🧠", "اعصاب": "🧠",
            "چشم": "👁️", "افتالمولوژی": "👁️",
            "دندان": "🦷", "دندانپزشک": "🦷",
            "کودکان": "👶", "اطفال": "👶", "نوزاد": "👶",
            "زنان": "👩", "زایمان": "👩", "زنان و زایمان": "👩",
            "ارتوپدی": "🦴", "استخوان": "🦴", "مفصل": "🦴",
            "پوست": "🧴", "درمتولوژی": "🧴",
            "گوش": "👂", "حلق": "👂", "بینی": "👂",
            "روانپزشک": "🧠", "روان": "🧠",
            "جراح": "🔪", "جراحی": "🔪",
            "داخلی": "🩺", "عمومی": "👨‍⚕️"
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
        """پردازش URL دکتر و اضافه کردن به سیستم بهبود یافته"""
        try:
            # ارسال پیام در حال پردازش
            processing_message = await message.reply_text(
                "🔄 **صبر کن، دارم کار می‌کنم...**\n\n"
                "⏳ دارم از پذیرش۲۴ اطلاعات دکتر رو می‌گیرم\n"
                "🔍 اطلاعات مهم رو استخراج می‌کنم\n"
                "💾 توی سیستم ذخیره می‌کنم\n\n"
                "⏰ چند ثانیه طول می‌کشه...",
                parse_mode='HTML'
            )
            
            # اعتبارسنجی URL
            is_valid, validation_message = self.doctor_manager.validate_doctor_url(url)
            if not is_valid:
                await processing_message.edit_text(
                    MessageFormatter.error_message(f"لینک درست نیست!\n\n{validation_message}"),
                    parse_mode='HTML'
                )
                return
            
            # اضافه کردن دکتر
            success, message_text, doctor = await self.doctor_manager.add_doctor_from_url(url, user_id)
            
            if success:
                # موفقیت
                text = MessageFormatter.doctor_extraction_success_message(doctor.name)
                
                keyboard = [
                    [InlineKeyboardButton("👨‍⚕️ مشاهده دکتر", callback_data=f"doctor_info_{doctor.id}")],
                    [InlineKeyboardButton("📝 ثبت‌نام در ا��ن دکتر", callback_data=f"subscribe_{doctor.id}")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await processing_message.edit_text(
                    text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                
                logger.info(f"✅ دکتر جدید اضافه شد: {doctor.name} توسط {message.from_user.first_name}")
                
            else:
                # خطا
                text = MessageFormatter.doctor_extraction_failed_message()
                
                keyboard = [
                    [InlineKeyboardButton("🔄 دوباره امتحان کن", callback_data="add_doctor")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await processing_message.edit_text(
                    text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            
        except Exception as e:
            logger.error(f"❌ خطا در پردازش URL دکتر: {e}")
            await message.reply_text(
                MessageFormatter.error_message(f"مشکلی پیش اومد: {str(e)}"),
                parse_mode='HTML'
            )
    
    async def _send_error_message(self, message, error_text):
        """ارسال پیام خطا بهبود یافته"""
        error_message = MessageFormatter.error_message(error_text)
        
        keyboard = [
            [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
        ]
        
        await message.reply_text(
            error_message,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
