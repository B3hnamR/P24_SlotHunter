"""
Menu-based handlers for Telegram bot with comprehensive button interface
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from src.database.database import db_session
from src.database.models import User, Doctor, Subscription, AppointmentLog
from src.telegram_bot.user_roles import user_role_manager, UserRole
from src.telegram_bot.messages import MessageFormatter
from src.utils.logger import get_logger

logger = get_logger("MenuHandlers")


class MenuHandlers:
    """کلاس handler های منو-محور ربات تلگرام"""
    
    @staticmethod
    def get_main_menu_keyboard(user_id: int = None) -> ReplyKeyboardMarkup:
        """دریافت کیبورد منوی اصلی بر اساس نقش کاربر"""
        
        # منوی پایه برای همه کاربران
        keyboard = [
            [KeyboardButton("👨‍⚕️ دکترها"), KeyboardButton("📝 اشتراک‌ها")],
            [KeyboardButton("🔔 اشتراک جدید"), KeyboardButton("🗑️ لغو اشتراک")],
            [KeyboardButton("📊 وضعیت من"), KeyboardButton("ℹ️ راهنما")]
        ]
        
        # بررسی نقش کاربر و اضافه کردن منوهای مخصوص
        if user_id:
            user_role = user_role_manager.get_user_role(user_id)
            
            # منوی کاربران عادی و بالاتر
            if user_role_manager.is_user_or_higher(user_id):
                keyboard.append([KeyboardButton("⚙️ تنظیمات"), KeyboardButton("📞 پشتیبانی")])
            
            # منوی مدیران و بالاتر
            if user_role_manager.is_moderator_or_higher(user_id):
                keyboard.append([KeyboardButton("📈 آمار سیستم"), KeyboardButton("👥 مدیریت کاربران")])
            
            # منوی ادمین‌ها
            if user_role_manager.is_admin_or_higher(user_id):
                keyboard.append([KeyboardButton("👑 پنل ادمین"), KeyboardButton("🔧 مدیریت سیستم")])
                
            # منوی سوپر ادمین
            if user_role == UserRole.SUPER_ADMIN:
                keyboard.append([KeyboardButton("⭐ سوپر ادمین"), KeyboardButton("🛠️ تنظیمات پیشرفته")])
        else:
            # منوی پیش‌فرض برای کاربران ناشناس
            keyboard.append([KeyboardButton("⚙️ تنظیمات"), KeyboardButton("📞 پشتیبانی")])
        
        return ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True, 
            one_time_keyboard=False,
            input_field_placeholder="یک گزینه انتخاب کنید..."
        )
    
    @staticmethod
    def get_doctors_inline_keyboard(doctors: List[Doctor], action: str = "info") -> InlineKeyboardMarkup:
        """دریافت کیبورد inline برای دکترها"""
        keyboard = []
        
        for doctor in doctors:
            status_emoji = "✅" if doctor.is_active else "⏸️"
            button_text = f"{status_emoji} {doctor.name}"
            callback_data = f"{action}_{doctor.id}"
            
            keyboard.append([
                InlineKeyboardButton(button_text, callback_data=callback_data)
            ])
        
        # دکمه بازگشت
        keyboard.append([
            InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_doctor_actions_keyboard(doctor_id: int, is_subscribed: bool = False) -> InlineKeyboardMarkup:
        """دریافت کیبورد عملیات دکتر"""
        keyboard = []
        
        if not is_subscribed:
            keyboard.append([
                InlineKeyboardButton("📝 اشتراک", callback_data=f"subscribe_{doctor_id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("🗑️ لغو اشتراک", callback_data=f"unsubscribe_{doctor_id}")
            ])
        
        keyboard.extend([
            [InlineKeyboardButton("🔗 مشاهده در سایت", callback_data=f"view_website_{doctor_id}")],
            [InlineKeyboardButton("📊 آمار نوبت‌ها", callback_data=f"stats_{doctor_id}")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_doctors")]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_settings_keyboard() -> InlineKeyboardMarkup:
        """دریافت کیبورد تنظیمات"""
        keyboard = [
            [InlineKeyboardButton("🔔 تنظیمات اطلاع‌رسانی", callback_data="settings_notifications")],
            [InlineKeyboardButton("⏰ تنظیمات زمان", callback_data="settings_time")],
            [InlineKeyboardButton("🌐 تنظیمات زبان", callback_data="settings_language")],
            [InlineKeyboardButton("🔒 تنظیمات حریم خصوصی", callback_data="settings_privacy")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_subscription_management_keyboard(user_subscriptions: List[Subscription]) -> InlineKeyboardMarkup:
        """دریافت کیبورد مدیریت اشتراک‌ها"""
        keyboard = []
        
        if user_subscriptions:
            keyboard.append([
                InlineKeyboardButton("📊 آمار کلی", callback_data="subscription_stats")
            ])
            keyboard.append([
                InlineKeyboardButton("🔄 بروزرسانی همه", callback_data="refresh_all_subscriptions")
            ])
            keyboard.append([
                InlineKeyboardButton("🗑️ لغو همه اشتراک‌ها", callback_data="unsubscribe_all_confirm")
            ])
        
        keyboard.extend([
            [InlineKeyboardButton("📝 اشتراک جدید", callback_data="new_subscription")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت منوی اصلی"""
        try:
            user = update.effective_user
            message_text = update.message.text if update.message else ""
            
            # ثبت/به‌روزرسانی کاربر
            await MenuHandlers._ensure_user_exists(user)
            
            # منوهای پایه
            if message_text == "👨‍⚕️ دکترها":
                await MenuHandlers.show_doctors_menu(update, context)
            elif message_text == "📝 اشتراک‌ها":
                await MenuHandlers.show_subscriptions_menu(update, context)
            elif message_text == "🔔 اشتراک جدید":
                await MenuHandlers.show_subscribe_menu(update, context)
            elif message_text == "🗑️ لغو اشتراک":
                await MenuHandlers.show_unsubscribe_menu(update, context)
            elif message_text == "📊 وضعیت من":
                await MenuHandlers.show_user_status(update, context)
            elif message_text == "ℹ️ راهنما":
                await MenuHandlers.show_help_menu(update, context)
            elif message_text == "⚙️ تنظیمات":
                await MenuHandlers.show_settings_menu(update, context)
            elif message_text == "📞 پشتیبانی":
                await MenuHandlers.show_support_menu(update, context)
            
            # منوهای مدیریتی
            elif message_text == "📈 آمار سیستم":
                from src.telegram_bot.admin_menu_handlers_fixed import AdminMenuHandlers
                await AdminMenuHandlers.show_system_stats_menu(update, context)
            elif message_text == "👥 مدیریت کاربران":
                from src.telegram_bot.admin_menu_handlers_fixed import AdminMenuHandlers
                await AdminMenuHandlers.show_user_management_menu(update, context)
            elif message_text == "👑 پنل ادمین":
                from src.telegram_bot.admin_menu_handlers_fixed import AdminMenuHandlers
                await AdminMenuHandlers.show_admin_panel(update, context)
            elif message_text == "🔧 مدیریت سیستم":
                from src.telegram_bot.admin_menu_handlers_fixed import AdminMenuHandlers
                await AdminMenuHandlers.show_system_management_menu(update, context)
            elif message_text == "⭐ سوپر ادمین":
                from src.telegram_bot.admin_menu_handlers_fixed import AdminMenuHandlers
                await AdminMenuHandlers.show_super_admin_menu(update, context)
            elif message_text == "🛠️ تنظیمات پیشرفته":
                from src.telegram_bot.admin_menu_handlers_fixed import AdminMenuHandlers
                await AdminMenuHandlers.show_advanced_settings_menu(update, context)
            
            else:
                # پیام خوش‌آمدگویی با منو
                await MenuHandlers.show_welcome_menu(update, context)
                
        except Exception as e:
            logger.error(f"❌ خطا در مدیریت منوی اصلی: {e}")
            await update.message.reply_text(
                MessageFormatter.error_message("خطا در پردازش درخواست"),
                reply_markup=MenuHandlers.get_main_menu_keyboard(user.id)
            )
    
    @staticmethod
    async def show_welcome_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی خوش‌آمدگویی"""
        user = update.effective_user
        user_role = user_role_manager.get_user_role(user.id)
        role_display = user_role_manager.get_role_display_name(user_role)
        
        welcome_text = f"""
🎯 **سلام {user.first_name}!**

به ربات نوبت‌یاب پذیرش۲۴ خوش آمدید!

👤 **نقش شما:** {role_display}

🔍 **امکانات:**
• نظارت مداوم بر نوبت‌های خالی
• اطلاع‌رسانی فوری از طریق تلگرام  
• پشتیبانی از چندین دکتر همزمان
• رابط کاربری ساده و کاربردی

📱 **از منوی زیر استفاده کنید:**
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=MenuHandlers.get_main_menu_keyboard(user.id)
        )
    
    @staticmethod
    async def show_doctors_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی دکترها"""
        try:
            with db_session() as session:
                doctors = session.query(Doctor).filter(Doctor.is_active == True).all()
                
                if not doctors:
                    await update.message.reply_text(
                        "❌ هیچ دکتری در سیستم ثبت نشده است.\n\n"
                        "💡 لطفاً با ادمین تماس بگیرید.",
                        reply_markup=MenuHandlers.get_main_menu_keyboard()
                    )
                    return
                
                doctors_text = f"""
👨‍⚕️ **لیست دکترهای موجود ({len(doctors)} دکتر):**

💡 روی نام دکتر کلیک کنید تا اطلاعات کامل را مشاهده کنید.
                """
                
                keyboard = MenuHandlers.get_doctors_inline_keyboard(doctors, "doctor_info")
                
                await update.message.reply_text(
                    doctors_text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منوی دکترها: {e}")
            await update.message.reply_text(
                MessageFormatter.error_message(),
                reply_markup=MenuHandlers.get_main_menu_keyboard()
            )
    
    @staticmethod
    async def show_subscriptions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی اشتراک‌ها"""
        try:
            user_id = update.effective_user.id
            
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await update.message.reply_text(
                        "❌ کاربر یافت نشد. لطفاً دوباره /start کنید.",
                        reply_markup=MenuHandlers.get_main_menu_keyboard()
                    )
                    return
                
                active_subscriptions = [
                    sub for sub in user.subscriptions if sub.is_active
                ]
                
                if not active_subscriptions:
                    text = """
📝 **اشتراک‌های من**

❌ شما در هیچ دکتری مشترک نیستید.

💡 برای اشتراک جدید از دکمه "🔔 اشتراک جدید" استفاده کنید.
                    """
                else:
                    text = f"""
📝 **اشتراک‌های من ({len(active_subscriptions)} اشتراک فعال):**

                    """
                    for i, sub in enumerate(active_subscriptions, 1):
                        date_str = sub.created_at.strftime('%Y/%m/%d') if sub.created_at else "نامشخص"
                        text += f"✅ **{i}. {sub.doctor.name}**\n"
                        text += f"   🏥 {sub.doctor.specialty}\n"
                        text += f"   📅 {date_str}\n\n"
                
                keyboard = MenuHandlers.get_subscription_management_keyboard(active_subscriptions)
                
                await update.message.reply_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logger.error(f"��� خطا در نمایش منوی اشتراک‌ها: {e}")
            await update.message.reply_text(
                MessageFormatter.error_message(),
                reply_markup=MenuHandlers.get_main_menu_keyboard()
            )
    
    @staticmethod
    async def show_subscribe_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی اشتراک جدید"""
        try:
            user_id = update.effective_user.id
            
            with db_session() as session:
                # دریافت دکترهای فعال
                doctors = session.query(Doctor).filter(Doctor.is_active == True).all()
                
                if not doctors:
                    await update.message.reply_text(
                        "❌ هیچ دکتری برای اشتراک موجود نیست.",
                        reply_markup=MenuHandlers.get_main_menu_keyboard()
                    )
                    return
                
                # دریافت اشتراک‌های فعلی کاربر
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await MenuHandlers._ensure_user_exists(update.effective_user)
                    user = session.query(User).filter(User.telegram_id == user_id).first()
                
                subscribed_doctor_ids = [
                    sub.doctor_id for sub in user.subscriptions if sub.is_active
                ]
                
                # فیلتر دکترهای غیرمشترک
                available_doctors = [
                    doctor for doctor in doctors 
                    if doctor.id not in subscribed_doctor_ids
                ]
                
                if not available_doctors:
                    await update.message.reply_text(
                        "✅ شما در تمام دکترهای موجود مشترک هستید!\n\n"
                        "📊 برای مشاهده اشتراک‌ها از منوی \"📝 اشتراک‌ها\" استفاده کنید.",
                        reply_markup=MenuHandlers.get_main_menu_keyboard()
                    )
                    return
                
                text = f"""
🔔 **اشتراک جدید**

{len(available_doctors)} دکتر برای اشتراک موجود است:

💡 روی نام دکتر کلیک کنید تا مشترک شوید.
                """
                
                keyboard = MenuHandlers.get_doctors_inline_keyboard(available_doctors, "subscribe")
                
                await update.message.reply_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منوی اشتراک: {e}")
            await update.message.reply_text(
                MessageFormatter.error_message(),
                reply_markup=MenuHandlers.get_main_menu_keyboard()
            )
    
    @staticmethod
    async def show_unsubscribe_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی لغو اشتراک"""
        try:
            user_id = update.effective_user.id
            
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await update.message.reply_text(
                        "❌ کاربر یافت نشد. لطفاً دوباره /start کنید.",
                        reply_markup=MenuHandlers.get_main_menu_keyboard()
                    )
                    return
                
                # دریافت اشتراک‌های فعال
                active_subscriptions = [
                    sub for sub in user.subscriptions if sub.is_active
                ]
                
                if not active_subscriptions:
                    await update.message.reply_text(
                        "❌ شما در هیچ دکتری مشترک نیستید.\n\n"
                        "💡 برای اشتراک جدید از دکمه \"🔔 اشتراک جدید\" استفاده کنید.",
                        reply_markup=MenuHandlers.get_main_menu_keyboard()
                    )
                    return
                
                text = f"""
🗑️ **لغو اشتراک**

{len(active_subscriptions)} اشتراک فعال دارید:

⚠️ روی نام دکتر کلیک کنید تا اشتراک لغو شود.
                """
                
                # ایجاد keyboard برای لغو اشتراک
                keyboard = []
                for subscription in active_subscriptions:
                    keyboard.append([
                        InlineKeyboardButton(
                            f"🗑️ {subscription.doctor.name}",
                            callback_data=f"unsubscribe_{subscription.doctor.id}"
                        )
                    ])
                
                keyboard.append([
                    InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش منوی لغو اشتراک: {e}")
            await update.message.reply_text(
                MessageFormatter.error_message(),
                reply_markup=MenuHandlers.get_main_menu_keyboard()
            )
    
    @staticmethod
    async def show_user_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش وضعیت کاربر"""
        try:
            user_id = update.effective_user.id
            
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await update.message.reply_text(
                        "❌ کاربر یافت نشد. لطفاً دوباره /start کنید.",
                        reply_markup=MenuHandlers.get_main_menu_keyboard()
                    )
                    return
                
                # آمار کاربر
                active_subscriptions = [sub for sub in user.subscriptions if sub.is_active]
                total_subscriptions = len(user.subscriptions)
                
                # آمار نوبت‌های پیدا شده
                today = datetime.now().date()
                appointments_today = session.query(AppointmentLog).join(Doctor).join(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.is_active == True,
                    AppointmentLog.created_at >= today
                ).count()
                
                status_text = f"""
📊 **وضعیت من**

👤 **اطلاعات کاربری:**
• نام: {user.full_name}
• شناسه: `{user.telegram_id}`
• تاریخ عضویت: {user.created_at.strftime('%Y/%m/%d') if user.created_at else 'نامشخص'}

📝 **اشتراک‌ها:**
• اشتراک‌های فعال: {len(active_subscriptions)}
• کل اشتراک‌ها: {total_subscriptions}

🎯 **آمار امروز:**
• نوبت‌های پیدا شده: {appointments_today}

⏰ **آخرین فعالیت:** {user.last_activity.strftime('%Y/%m/%d %H:%M') if user.last_activity else 'نامشخص'}
                """
                
                # دکمه‌های عملیات
                keyboard = [
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_status")],
                    [InlineKeyboardButton("📊 آمار تفصیلی", callback_data="detailed_stats")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    status_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش وضعیت کاربر: {e}")
            await update.message.reply_text(
                MessageFormatter.error_message(),
                reply_markup=MenuHandlers.get_main_menu_keyboard()
            )
    
    @staticmethod
    async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی راهنما"""
        help_text = """
📚 **راهنمای کامل ربات**

🎯 **هدف ربات:**
این ربات به شما کمک می‌کند تا نوبت‌های خالی دکترها در سایت پذیرش۲۴ را پیدا کنید.

🔍 **نحوه کار:**
1. در دکتر مور�� نظر مشترک شوید
2. ربات مداوم نوبت‌های خالی را بررسی می‌کند
3. فوراً از نوبت‌های جدید مطلع می‌شوید

📱 **استفاده از منو:**
• **👨‍⚕️ دکترها**: مشاهده لیست دکترها
• **📝 اشتراک‌ها**: مدیریت اشتراک‌های فعلی
• **🔔 اشتراک جد��د**: اشتراک در دکتر جدید
• **🗑️ لغو اشتراک**: لغو اشتراک از دکتر
• **📊 وضعیت من**: مشاهده آمار شخصی
• **⚙️ تنظیمات**: تنظیمات ربات

⚡ **نکات مهم:**
• پس از اشتراک، فوراً از نوبت‌های جدید مطلع می‌شوید
• می‌توانید در چندین دکتر همزمان مشترک شوید
• نوبت‌ها ممکن است سریع تمام شوند، پس سریع عمل کنید

🆘 **پشتیبانی:**
در صورت بروز مشکل، از منوی "📞 پشتیبانی" استفاده کنید.
        """
        
        keyboard = [
            [InlineKeyboardButton("🎥 ویدیو آموزشی", callback_data="help_video")],
            [InlineKeyboardButton("❓ سوالات متداول", callback_data="help_faq")],
            [InlineKeyboardButton("📞 تماس با پشتیبانی", callback_data="help_contact")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی تنظیمات"""
        settings_text = """
⚙️ **تنظیمات ربات**

از گزینه‌های زیر برای تنظیم ربات استفاده کنید:
        """
        
        keyboard = MenuHandlers.get_settings_keyboard()
        
        await update.message.reply_text(
            settings_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    
    @staticmethod
    async def show_support_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی پشتیبانی"""
        support_text = """
📞 **پشتیبانی و تماس**

🆘 **راه‌های تماس:**
• تلگرام: @support_username
• ایمیل: support@example.com
• تلفن: 021-12345678

⏰ **ساعات پاسخگویی:**
شنبه تا پنج‌شنبه: 9:00 تا 18:00

🔧 **مشکلات رایج:**
• اگر نوبتی دریافت نمی‌کنید، اشتراک خود را بررسی کنید
• اگر ربات پاسخ نمی‌دهد، چند دقیقه صبر کنید
• برای مشکلات فنی، از دکمه "🐛 گزارش باگ" استفاده کنید

💡 **پیشنهادات:**
��ظرات و پیشنهادات خود را با ما در میان بگذارید.
        """
        
        keyboard = [
            [InlineKeyboardButton("💬 چت با پشتیبانی", callback_data="support_chat")],
            [InlineKeyboardButton("🐛 گزارش باگ", callback_data="support_bug")],
            [InlineKeyboardButton("💡 پیشنهاد", callback_data="support_suggestion")],
            [InlineKeyboardButton("📋 وضعیت سیستم", callback_data="system_status")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            support_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def _ensure_user_exists(user):
        """اطمینان از وجود کاربر در دیتابیس"""
        try:
            with db_session() as session:
                db_user = session.query(User).filter(User.telegram_id == user.id).first()
                
                if not db_user:
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
                    db_user.last_activity = datetime.utcnow()
                
                session.commit()
                
        except Exception as e:
            logger.error(f"❌ خطا در ثبت/به‌روزرسانی کاربر: {e}")