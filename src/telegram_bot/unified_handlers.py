"""
Modern Telegram Handlers with Advanced UI/UX
"""
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy import select
from typing import List
from datetime import datetime

from src.database.models import User, Doctor, Subscription
from src.telegram_bot.messages import MessageFormatter
from src.utils.logger import get_logger

logger = get_logger("ModernHandlers")


class UnifiedTelegramHandlers:
    """کلاس مدرن handlers تلگرام با UI/UX پیشرفته"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    # ==================== Command Handlers ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /start با UI مدرن"""
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
            
            # پیام خوش‌آمدگویی مدرن
            if is_new_user:
                welcome_text = f"""
🎯 **سلام {user.first_name}! خوش آمدید** 🎉

به **ربات نوبت‌یاب پذیرش۲۴** خوش آمدید!

🔥 **ویژگی‌های منحصر به فرد:**
• �� **نظارت هوشمند** بر نوبت‌های خالی
• ⚡ **اطلاع‌رسانی فوری** در کمتر از 30 ثانیه
• 👨‍⚕️ **پشتیبانی از چندین دکتر** همزمان
• 📊 **آمار و گزارش‌های تفصیلی**
• 🔔 **اعلان‌های هوشمند** بر اساس ترجیحات شما

💡 **نکته:** این ربات به صورت ۲۴/۷ نوبت‌های خالی را رصد می‌کند!
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
            
            # منوی اصلی مدرن
            keyboard = [
                [
                    InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors"),
                    InlineKeyboardButton("📝 اشتراک‌های من", callback_data="my_subscriptions")
                ],
                [
                    InlineKeyboardButton("🔔 اشتراک جدید", callback_data="new_subscription"),
                    InlineKeyboardButton("📊 آمار و گزارش", callback_data="my_stats")
                ],
                [
                    InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings"),
                    InlineKeyboardButton("❓ راهنما", callback_data="help_menu")
                ]
            ]
            
            # اضافه کردن دکمه ادمین برای ادمین‌ها
            if await self._is_admin(user.id):
                keyboard.append([
                    InlineKeyboardButton("🔧 پنل مدیریت", callback_data="admin_panel")
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # ارسال پیام با انیمیشن
            await update.message.reply_text(
                welcome_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # تنظیم منوی دائمی
            await self._setup_persistent_menu(update)
            
        except Exception as e:
            logger.error(f"❌ خطا در start: {e}")
            await self._send_error_message(update.message, str(e))
    
    async def _setup_persistent_menu(self, update):
        """تنظیم منوی دائمی در پایین صفحه"""
        keyboard = [
            [
                KeyboardButton("👨‍⚕️ دکترها"),
                KeyboardButton("📝 اشتراک‌ها"),
                KeyboardButton("📊 آمار")
            ],
            [
                KeyboardButton("🔔 اشتراک جدید"),
                KeyboardButton("❓ راهنما")
            ]
        ]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder="انتخاب کنید..."
        )
        
        # ارسال پیام کوتاه برای تنظیم منو
        await update.message.reply_text(
            "📱 **منوی سریع فعال شد!**\n\nاز دکمه‌های پایین صفحه برای دسترسی سریع استفاده کنید.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /help مدرن"""
        try:
            help_text = """
📚 **راهنمای کامل ربات نوبت‌یاب**

🎯 **دستورات اصلی:**
• `/start` - شروع مجدد و منوی اصلی
• `/doctors` - مشاهده سریع لیست دکترها  
• `/status` - وضعیت اشتراک‌های من
• `/help` - نمایش این راهنما

🔥 **ویژگی‌های پیشرفته:**

🔍 **نظارت هوشمند:**
• بررسی خودکار هر ۳۰ ثانیه
• اطلاع‌رسانی فوری نوبت‌های خالی
• پشتیبانی از چندین دکتر همزمان

📊 **آمار و گزارش:**
• تعداد نوبت‌های پیدا شده
• آمار روزانه و هفتگی
• گزارش عملکرد اشتراک‌ها

⚙️ **تنظیمات شخصی:**
• انتخاب ساعات اطلاع‌رسانی
• تنظیم نوع اعلان‌ها
• مدیریت اشتراک‌ها

💡 **نکات مهم:**
• نوبت‌ها ممکن است سریع تمام شوند
• همیشه آماده باشید تا سریع رزرو کنید
• از چندین دکتر همزمان استفاده کنید

🆘 **پشتیبانی:**
در صورت بروز مشکل، با ادمین تماس بگیرید.
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🎬 آموزش ویدیویی", callback_data="video_tutorial"),
                    InlineKeyboardButton("❓ سوالا�� متداول", callback_data="faq")
                ],
                [
                    InlineKeyboardButton("📞 تماس با پشتیبانی", callback_data="contact_support"),
                    InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                ]
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
        """دستور /doctors مدرن"""
        try:
            await self._show_doctors_list_modern(update.message)
        except Exception as e:
            logger.error(f"❌ خطا در doctors: {e}")
            await self._send_error_message(update.message, str(e))
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /status مدرن"""
        try:
            await self._show_user_status_modern(update.message, update.effective_user.id)
        except Exception as e:
            logger.error(f"❌ خطا در status: {e}")
            await self._send_error_message(update.message, str(e))
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /admin مدرن"""
        try:
            user_id = update.effective_user.id
            
            if not await self._is_admin(user_id):
                await update.message.reply_text(
                    "❌ **دسترسی محدود**\n\nشما دسترسی به پنل مدیریت ندارید.",
                    parse_mode='Markdown'
                )
                return
            
            await self._show_admin_panel_modern(update.message)
            
        except Exception as e:
            logger.error(f"❌ خطا در admin: {e}")
            await self._send_error_message(update.message, str(e))
    
    # ==================== Message Handlers ====================
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پیام‌های متنی از منوی دائمی"""
        try:
            text = update.message.text
            
            if text == "👨‍⚕️ دکترها":
                await self._show_doctors_list_modern(update.message)
            elif text == "📝 اشتراک‌ها":
                await self._show_subscriptions_modern(update.message, update.effective_user.id)
            elif text == "📊 آمار":
                await self._show_user_status_modern(update.message, update.effective_user.id)
            elif text == "🔔 اشتراک جدید":
                await self._show_new_subscription_modern(update.message, update.effective_user.id)
            elif text == "❓ راهنما":
                await self.help_command(update, context)
            else:
                # پیام پیش‌فرض برای متن‌های نامشخص
                await update.message.reply_text(
                    "🤔 **متوجه نشدم!**\n\nلطفاً از دکمه‌های منو استفاده کنید یا `/help` بزنید.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در پیام متنی: {e}")
            await self._send_error_message(update.message, str(e))
    
    # ==================== Callback Handlers ====================
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت callback های مدرن"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            
            # مسیریابی callback ها
            if data == "show_doctors":
                await self._callback_show_doctors_modern(query)
            elif data == "my_subscriptions":
                await self._callback_show_subscriptions_modern(query, user_id)
            elif data == "new_subscription":
                await self._callback_new_subscription_modern(query, user_id)
            elif data == "my_stats":
                await self._callback_user_stats_modern(query, user_id)
            elif data == "settings":
                await self._callback_settings_modern(query, user_id)
            elif data == "help_menu":
                await self._callback_help_menu_modern(query)
            elif data == "admin_panel":
                await self._callback_admin_panel_modern(query, user_id)
            elif data.startswith("doctor_info_"):
                await self._callback_doctor_info_modern(query, data, user_id)
            elif data.startswith("subscribe_"):
                await self._callback_subscribe_modern(query, data, user_id)
            elif data.startswith("unsubscribe_"):
                await self._callback_unsubscribe_modern(query, data, user_id)
            elif data == "back_to_main":
                await self._callback_back_to_main_modern(query)
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
    
    # ==================== Modern UI Methods ====================
    
    async def _show_doctors_list_modern(self, message):
        """نمایش لیست دکترها با UI مدرن"""
        async with self.db_manager.session_scope() as session:
            result = await session.execute(
                select(Doctor).filter(Doctor.is_active == True)
            )
            doctors = result.scalars().all()
            
            if not doctors:
                text = """
❌ **هیچ دکتری موجود نیست**

متأسفانه در حال حاضر هیچ دکتری در سیستم ثبت نشده است.

💡 **پیشنهاد:** با ادمین تماس بگیرید تا دکتر مورد نظرتان را اضافه کند.
                """
                
                keyboard = [[
                    InlineKeyboardButton("📞 تماس با ادمین", callback_data="contact_admin"),
                    InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                ]]
                
                await message.reply_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            
            text = f"""
👨‍⚕️ **لیست دکترهای موجود**

📊 **آمار کلی:**
• تعداد دکترها: **{len(doctors)}** نفر
• وضعیت سیستم: ✅ **فعال**
• آخرین بروزرسانی: **{datetime.now().strftime('%H:%M')}**

💡 **راهنما:** روی نام دکتر کلیک کنید تا اطلاعات کامل و گزینه‌های اشتراک را مشاهده کنید.

📋 **لیست دکترها:**
            """
            
            # ایجاد keyboard
            keyboard = []
            for doctor in doctors:
                # اضافه کردن ایموجی بر اساس تخصص
                specialty_emoji = self._get_specialty_emoji(doctor.specialty)
                
                keyboard.append([
                    InlineKeyboardButton(
                        f"{specialty_emoji} {doctor.name}",
                        callback_data=f"doctor_info_{doctor.id}"
                    )
                ])
            
            # دکمه‌های اضافی
            keyboard.extend([
                [
                    InlineKeyboardButton("🔄 بروزرسانی", callback_data="show_doctors"),
                    InlineKeyboardButton("🔍 جستجو", callback_data="search_doctors")
                ],
                [
                    InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                ]
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.reply_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    def _get_specialty_emoji(self, specialty):
        """دریافت ایموجی مناسب برای تخصص"""
        if not specialty:
            return "👨‍⚕️"
        
        specialty_lower = specialty.lower()
        
        if "قلب" in specialty_lower or "کاردیولوژی" in specialty_lower:
            return "❤️"
        elif "مغز" in specialty_lower or "نورولوژی" in specialty_lower:
            return "🧠"
        elif "چشم" in specialty_lower or "افتالمولوژی" in specialty_lower:
            return "👁️"
        elif "دندان" in specialty_lower:
            return "🦷"
        elif "کودکان" in specialty_lower or "اطفال" in specialty_lower:
            return "👶"
        elif "زنان" in specialty_lower or "زایمان" in specialty_lower:
            return "👩"
        elif "ارتوپدی" in specialty_lower or "استخوان" in specialty_lower:
            return "🦴"
        elif "پوست" in specialty_lower or "درمتولوژی" in specialty_lower:
            return "🧴"
        elif "گوش" in specialty_lower or "حلق" in specialty_lower:
            return "👂"
        else:
            return "👨‍⚕️"
    
    async def _is_admin(self, user_id):
        """بررسی ادمین بودن"""
        try:
            from src.utils.config import Config
            config = Config()
            return user_id == config.admin_chat_id
        except:
            return False
    
    async def _send_error_message(self, message, error_text):
        """ارسال پیام خطا مدرن"""
        error_message = f"""
❌ **خطا در پردازش درخواست**

🔍 **جزئیات خطا:**
`{error_text}`

🔧 **راه‌حل‌های پیشنهادی:**
• دوباره تلاش کنید
• از منوی اصلی استفاده کنید
• در صورت تکرار، با ادمین تماس بگیرید

⏰ **زمان خطا:** {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 تلاش مجدد", callback_data="back_to_main"),
                InlineKeyboardButton("📞 تماس با ادمین", callback_data="contact_admin")
            ]
        ]
        
        await message.reply_text(
            error_message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ==================== Callback Methods ====================
    
    async def _callback_show_doctors_modern(self, query):
        """callback نمایش دکترها"""
        await self._show_doctors_list_modern(query.message)
    
    async def _callback_show_subscriptions_modern(self, query, user_id):
        """callback نمایش اشتراک‌ها"""
        await self._show_subscriptions_modern(query.message, user_id)
    
    async def _callback_new_subscription_modern(self, query, user_id):
        """callback اشتراک جدید"""
        await self._show_new_subscription_modern(query.message, user_id)
    
    async def _callback_user_stats_modern(self, query, user_id):
        """callback آمار کاربر"""
        await self._show_user_status_modern(query.message, user_id)
    
    async def _callback_settings_modern(self, query, user_id):
        """callback تنظیمات"""
        await query.edit_message_text(
            "⚙️ **تنظیمات ربات**\n\n🔧 این قسمت در حال توسعه است.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
            ]])
        )
    
    async def _callback_help_menu_modern(self, query):
        """callback منوی راهنما"""
        await self.help_command(query, None)
    
    async def _callback_admin_panel_modern(self, query, user_id):
        """callback پنل ادمین"""
        if not await self._is_admin(user_id):
            await query.edit_message_text("❌ دسترسی ندارید.")
            return
        
        await self._show_admin_panel_modern(query.message)
    
    async def _callback_doctor_info_modern(self, query, data, user_id):
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
                
                specialty_emoji = self._get_specialty_emoji(doctor.specialty)
                
                text = f"""
{specialty_emoji} **{doctor.name}**

🏥 **تخصص:** {doctor.specialty or 'نامشخص'}
🏢 **مرکز:** {doctor.center_name or 'نامشخص'}
📍 **آدرس:** {doctor.center_address or 'نامشخص'}

🔗 **لینک مستقیم:**
https://www.paziresh24.com/dr/{doctor.slug}/

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
    
    async def _callback_subscribe_modern(self, query, data, user_id):
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

🔔 از این پس نوبت‌های خالی به شما اطلاع داده می‌شود.

💡 **نکته:** نوبت‌ها ممکن است سریع تمام شوند، پس آماده باشید!
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
    
    async def _callback_unsubscribe_modern(self, query, data, user_id):
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
                
                # پ��دا کردن اشتراک
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

🔕 دیگر اطلاع‌رسانی دریافت نخواهید کرد.

💡 در صورت نیاز، می‌توانید مجدداً مشترک شوید.
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
    
    async def _callback_back_to_main_modern(self, query):
        """callback بازگشت به منوی اصلی"""
        text = """
🎯 **منوی اصلی**

از دکمه‌های زیر برای استفاده از ربات استفاده کنید:

💡 **نکته:** از منوی پایین صفحه نیز می‌توانید استفاده کنید.
        """
        
        keyboard = [
            [
                InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors"),
                InlineKeyboardButton("📝 اشتراک‌های من", callback_data="my_subscriptions")
            ],
            [
                InlineKeyboardButton("🔔 اشتراک جدید", callback_data="new_subscription"),
                InlineKeyboardButton("📊 آمار و گزارش", callback_data="my_stats")
            ],
            [
                InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings"),
                InlineKeyboardButton("❓ راهنما", callback_data="help_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ==================== Helper Methods ====================
    
    async def _show_subscriptions_modern(self, message, user_id):
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

💡 برای شروع، از دکمه زیر استفاده کنید.
                """
                keyboard = [
                    [InlineKeyboardButton("🔔 اشتراک جدید", callback_data="new_subscription")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
            else:
                text = f"""
📝 **اشتراک‌های من ({len(subscriptions)} اشتراک فعال)**

✅ **لیست اشتراک‌ها:**

                """
                
                keyboard = []
                for sub in subscriptions:
                    specialty_emoji = self._get_specialty_emoji(sub.doctor.specialty)
                    text += f"• {specialty_emoji} **{sub.doctor.name}**\n"
                    text += f"  📅 تاریخ اشتراک: {sub.created_at.strftime('%Y/%m/%d') if sub.created_at else 'نامشخص'}\n\n"
                    
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
            
            await message.reply_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def _show_new_subscription_modern(self, message, user_id):
        """نمایش اشتراک جدید"""
        async with self.db_manager.session_scope() as session:
            # دریافت دکترهای فعال
            result = await session.execute(
                select(Doctor).filter(Doctor.is_active == True)
            )
            doctors = result.scalars().all()
            
            if not doctors:
                await message.reply_text(
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
                await message.reply_text(
                    "✅ شما در تمام دکترها مشترک هستید!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
                return
            
            text = f"""
🔔 **اشتراک جدید**

📊 **آمار:**
• دکترهای موجود: {len(available_doctors)} نفر
• وضعیت سیستم: ✅ فعال

💡 **راهنما:** روی نام دکتر کلیک کنید تا مشترک شوید.

📋 **دکترهای قابل اشتراک:**
            """
            
            keyboard = []
            for doctor in available_doctors:
                specialty_emoji = self._get_specialty_emoji(doctor.specialty)
                keyboard.append([
                    InlineKeyboardButton(
                        f"📝 {specialty_emoji} {doctor.name}",
                        callback_data=f"subscribe_{doctor.id}"
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
    
    async def _show_user_status_modern(self, message, user_id):
        """نمایش وضعیت کاربر"""
        async with self.db_manager.session_scope() as session:
            result = await session.execute(
                select(User).filter(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await message.reply_text("❌ کاربر یافت نشد.")
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
📊 **آمار و وضعیت من**

👤 **اطلاعات کاربری:**
• نام: **{user.full_name}**
• شناسه: `{user.telegram_id}`
• نام کاربری: @{user.username or 'ندارد'}

📝 **اشتراک‌ها:**
• اشتراک‌های فعال: **{active_subs}** دکتر
• وضعیت حساب: ✅ **فعال**

📅 **تاریخ‌ها:**
• عضویت: **{user.created_at.strftime('%Y/%m/%d') if user.created_at else 'نامشخص'}**
• آخرین فعالیت: **{datetime.now().strftime('%Y/%m/%d %H:%M')}**

🎯 **عملکرد:**
• سیستم: ✅ **فعال و آماده**
• اطلاع‌رسانی: ✅ **فعال**
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 بروزرسانی", callback_data="my_stats"),
                    InlineKeyboardButton("📝 اشتراک‌ها", callback_data="my_subscriptions")
                ],
                [
                    InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.reply_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def _show_admin_panel_modern(self, message):
        """نمایش پنل ادمین مدرن"""
        text = """
🔧 **پنل مدیریت**

خوش آمدید به پنل مدیریت ربات نوبت‌یاب!

⚙️ **امکانات مدیریت:**
• مدیریت دکترها و کاربران
• مشاهده آمار سیستم
• تنظیمات پیشرفته

💡 **نکته:** این قسمت در حال توسعه است.
        """
        
        keyboard = [
            [
                InlineKeyboardButton("👨‍⚕️ مدیریت دکترها", callback_data="admin_doctors"),
                InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("📊 آمار سیستم", callback_data="admin_stats"),
                InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings")
            ],
            [
                InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )