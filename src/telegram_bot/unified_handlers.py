"""
Modern Telegram Handlers with Scalable Architecture
"""
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy import select
from typing import List, Dict, Callable
from datetime import datetime

from src.database.models import User, Doctor, Subscription
from src.telegram_bot.messages import MessageFormatter
from src.utils.logger import get_logger

logger = get_logger("ModernHandlers")


class UnifiedTelegramHandlers:
    """کلاس مدرن handlers تلگرام با معماری مقیاس‌پذیر"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
        # ==================== EXTENSIBLE CALLBACK REGISTRY ====================
        # این بخش برای اضافه کردن callback های جدید بدون تغییر کد اصلی
        self.callback_handlers: Dict[str, Callable] = {
            # Core callbacks
            "show_doctors": self._callback_show_doctors_modern,
            "my_subscriptions": self._callback_show_subscriptions_modern,
            "new_subscription": self._callback_new_subscription_modern,
            "my_stats": self._callback_user_stats_modern,
            "settings": self._callback_settings_modern,
            "help_menu": self._callback_help_menu_modern,
            "admin_panel": self._callback_admin_panel_modern,
            "back_to_main": self._callback_back_to_main_modern,
            
            # ==================== FUTURE FEATURES PLACEHOLDER ====================
            # اینجا می‌توانید قابلیت‌های جدید اضافه کنید:
            
            # Notification settings
            "notification_settings": self._callback_notification_settings,
            "toggle_notifications": self._callback_toggle_notifications,
            "set_notification_hours": self._callback_set_notification_hours,
            
            # Advanced search
            "search_doctors": self._callback_search_doctors,
            "filter_by_specialty": self._callback_filter_by_specialty,
            "filter_by_location": self._callback_filter_by_location,
            
            # User preferences
            "user_preferences": self._callback_user_preferences,
            "language_settings": self._callback_language_settings,
            "theme_settings": self._callback_theme_settings,
            
            # Analytics and reports
            "detailed_stats": self._callback_detailed_stats,
            "export_data": self._callback_export_data,
            "appointment_history": self._callback_appointment_history,
            
            # Social features
            "share_doctor": self._callback_share_doctor,
            "rate_doctor": self._callback_rate_doctor,
            "doctor_reviews": self._callback_doctor_reviews,
            
            # Admin features
            "admin_doctors": self._callback_admin_doctors,
            "admin_users": self._callback_admin_users,
            "admin_stats": self._callback_admin_stats,
            "admin_settings": self._callback_admin_settings,
            "admin_broadcast": self._callback_admin_broadcast,
            
            # Help and support
            "video_tutorial": self._callback_video_tutorial,
            "faq": self._callback_faq,
            "contact_support": self._callback_contact_support,
            "contact_admin": self._callback_contact_admin,
        }
        
        # ==================== EXTENSIBLE COMMAND REGISTRY ====================
        # این بخش برای اضافه کردن command های جدید
        self.command_handlers: Dict[str, Callable] = {
            "start": self.start_command,
            "help": self.help_command,
            "doctors": self.doctors_command,
            "status": self.status_command,
            "admin": self.admin_command,
            
            # ==================== FUTURE COMMANDS PLACEHOLDER ====================
            # اینجا می‌توانید command های جدید اضافه کنید:
            
            # "search": self.search_command,
            # "notifications": self.notifications_command,
            # "preferences": self.preferences_command,
            # "export": self.export_command,
            # "feedback": self.feedback_command,
        }
        
        # ==================== EXTENSIBLE TEXT MENU REGISTRY ====================
        # این بخش برای اضافه کردن گزینه‌های منوی متنی جدید
        self.text_menu_handlers: Dict[str, Callable] = {
            "👨‍⚕️ دکترها": self._show_doctors_list_modern,
            "📝 اشتراک‌ها": self._show_subscriptions_modern,
            "📊 آمار": self._show_user_status_modern,
            "🔔 اشتراک جدید": self._show_new_subscription_modern,
            "❓ راهنما": self.help_command,
            
            # ==================== FUTURE MENU OPTIONS PLACEHOLDER ====================
            # اینجا می‌توانید گزینه‌های منوی جدید اضافه کنید:
            
            # "🔍 جستجو": self._show_search_menu,
            # "⚙️ تنظیمات": self._show_settings_menu,
            # "📈 گزارش‌ها": self._show_reports_menu,
            # "🔔 اعلان‌ها": self._show_notifications_menu,
        }
    
    # ==================== CORE COMMAND HANDLERS ====================
    
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
            welcome_text = await self._get_welcome_message(user, is_new_user, db_user)
            
            # منوی اصلی مدرن (قابل توسعه)
            keyboard = await self._get_main_menu_keyboard(user.id)
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # ارسال پیام
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
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /help مدرن"""
        try:
            help_text = MessageFormatter.help_message()
            
            keyboard = [
                [
                    InlineKeyboardButton("🎬 آموزش ویدیویی", callback_data="video_tutorial"),
                    InlineKeyboardButton("❓ سوالات متداول", callback_data="faq")
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
    
    # ==================== EXTENSIBLE MESSAGE HANDLER ====================
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پیام‌های متنی از منوی دائمی (قابل توسعه)"""
        try:
            text = update.message.text
            user_id = update.effective_user.id
            
            # بررسی در registry منوی متنی
            if text in self.text_menu_handlers:
                handler = self.text_menu_handlers[text]
                if asyncio.iscoroutinefunction(handler):
                    if handler.__code__.co_argcount > 2:  # اگر user_id نیاز دارد
                        await handler(update.message, user_id)
                    else:
                        await handler(update.message)
                else:
                    await handler(update, context)
            else:
                # پیام پیش‌فرض برای متن‌های نامشخص
                await update.message.reply_text(
                    "🤔 **متوجه نشدم!**\n\nلطفاً از دکمه‌های منو استفاده کنید یا `/help` بزنید.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در پیام متنی: {e}")
            await self._send_error_message(update.message, str(e))
    
    # ==================== EXTENSIBLE CALLBACK HANDLER ====================
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت callback های مدرن (قابل توسعه)"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            
            # مدیریت callback های با prefix
            if data.startswith("doctor_info_"):
                await self._callback_doctor_info_modern(query, data, user_id)
            elif data.startswith("subscribe_"):
                await self._callback_subscribe_modern(query, data, user_id)
            elif data.startswith("unsubscribe_"):
                await self._callback_unsubscribe_modern(query, data, user_id)
            elif data.startswith("page_"):
                await self._callback_pagination(query, data, user_id)
            elif data.startswith("filter_"):
                await self._callback_filter(query, data, user_id)
            # بررسی در registry callback ها
            elif data in self.callback_handlers:
                handler = self.callback_handlers[data]
                if handler.__code__.co_argcount > 2:  # اگر user_id نیاز دارد
                    await handler(query, user_id)
                else:
                    await handler(query)
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
    
    # ==================== EXTENSIBLE HELPER METHODS ====================
    
    async def _get_welcome_message(self, user, is_new_user, db_user):
        """تولید پیام خوش‌آ��دگویی (قابل شخصی‌سازی)"""
        if is_new_user:
            return f"""
🎯 **سلام {user.first_name}! خوش آمدید** 🎉

به **ربات نوبت‌یاب پذیرش۲۴** خوش آمدید!

🔥 **ویژگی‌های منحصر به فرد:**
• 🔍 **نظارت هوشمند** بر نوبت‌های خالی
• ⚡ **اطلاع‌رسانی فوری** در کمتر از 30 ثانیه
• 👨‍⚕️ **پشتیبانی از چندین دکتر** همزمان
• 📊 **آمار و گزارش‌های تفصیلی**
• 🔔 **اعلان‌های هوشمند** بر اساس ترجیحات شما

💡 **نکته:** این ربات به صورت ۲۴/۷ نوبت‌های خالی را رصد می‌کند!
            """
        else:
            return f"""
👋 **سلام مجدد {user.first_name}!**

خوشحالیم که دوباره اینجا هستید! 

📊 **وضعیت سریع:**
• آخرین بازدید: {db_user.last_activity.strftime('%Y/%m/%d %H:%M') if db_user.last_activity else 'اولین بار'}
• حساب کاربری: ✅ فعال

🚀 **آماده برای شروع؟**
            """
    
    async def _get_main_menu_keyboard(self, user_id):
        """تولید کیبورد منوی اصلی (قابل شخصی‌سازی)"""
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
        if await self._is_admin(user_id):
            keyboard.append([
                InlineKeyboardButton("🔧 پنل مدیریت", callback_data="admin_panel")
            ])
        
        return keyboard
    
    async def _setup_persistent_menu(self, update):
        """تنظیم منوی دائمی (قابل شخصی‌سازی)"""
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
        
        # ==================== FUTURE: CUSTOMIZABLE MENU ====================
        # اینجا می‌توانید منوی شخصی‌سازی شده بر اساس تنظیمات کاربر اضافه کنید
        
        reply_markup = ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder="انتخاب کنید..."
        )
        
        await update.message.reply_text(
            "📱 **منوی سریع فعال شد!**\n\nاز دکمه‌های پایین صفحه برای دسترسی سریع استفاده کنید.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ==================== CORE CALLBACK IMPLEMENTATIONS ====================
    
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
    
    async def _callback_back_to_main_modern(self, query):
        """callback بازگشت به منوی اصلی"""
        user_id = query.from_user.id
        keyboard = await self._get_main_menu_keyboard(user_id)
        
        text = """
🎯 **منوی اصلی**

از دکمه‌های زیر برای استفاده از ربات استفاده کنید:

💡 **نکته:** از منوی پایین صفحه نیز می‌توانید استفاده کنید.
        """
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # ==================== FUTURE FEATURES IMPLEMENTATIONS ====================
    # این بخش برای قابلیت‌های آینده آماده شده است
    
    async def _callback_notification_settings(self, query, user_id):
        """تنظیمات اعلان‌ها - آماده برای پیاده‌سازی"""
        await query.edit_message_text(
            "🔔 **تنظیمات اعلان‌ها**\n\n🔧 این قسمت در حال توسعه است.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="settings")
            ]])
        )
    
    async def _callback_search_doctors(self, query, user_id):
        """جستجوی دکترها - آماده برای پیاده‌سازی"""
        await query.edit_message_text(
            "🔍 **جستجوی دکترها**\n\n🔧 این قسمت در حال توسعه است.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="show_doctors")
            ]])
        )
    
    async def _callback_detailed_stats(self, query, user_id):
        """آمار تفصیلی - آماده برای پیاده‌سازی"""
        await query.edit_message_text(
            "📈 **آمار تفصیلی**\n\n🔧 این قسمت در حال توسعه است.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="my_stats")
            ]])
        )
    
    async def _callback_admin_broadcast(self, query, user_id):
        """پخش پیام ادمین - آماده برای پیاده‌سازی"""
        if not await self._is_admin(user_id):
            await query.edit_message_text("❌ دسترسی ندارید.")
            return
            
        await query.edit_message_text(
            "📢 **پخش پیام**\n\n🔧 این قسمت در حال توسعه است.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="admin_panel")
            ]])
        )
    
    # ==================== PLACEHOLDER METHODS ====================
    # این متدها برای قابلیت‌های آینده placeholder هستند
    
    async def _callback_settings_modern(self, query, user_id):
        """تنظیمات - قابل توسعه"""
        keyboard = [
            [
                InlineKeyboardButton("🔔 تنظیمات اعلان", callback_data="notification_settings"),
                InlineKeyboardButton("🌐 زبان", callback_data="language_settings")
            ],
            [
                InlineKeyboardButton("🎨 تم", callback_data="theme_settings"),
                InlineKeyboardButton("👤 تنظیمات کاربری", callback_data="user_preferences")
            ],
            [
                InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
            ]
        ]
        
        await query.edit_message_text(
            "⚙️ **تنظیمات ربات**\n\nگزینه مورد نظر را انتخاب کنید:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _callback_help_menu_modern(self, query):
        """منوی راهنما"""
        keyboard = [
            [
                InlineKeyboardButton("🎬 آموزش ویدیویی", callback_data="video_tutorial"),
                InlineKeyboardButton("❓ سوالات متداول", callback_data="faq")
            ],
            [
                InlineKeyboardButton("📞 تماس با پشتیبانی", callback_data="contact_support"),
                InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
            ]
        ]
        
        help_text = MessageFormatter.help_message()
        
        await query.edit_message_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def _callback_admin_panel_modern(self, query, user_id):
        """پنل ادمین"""
        if not await self._is_admin(user_id):
            await query.edit_message_text("❌ دسترسی ندارید.")
            return
        
        await self._show_admin_panel_modern(query.message)
    
    # ==================== UTILITY METHODS ====================
    
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
    
    # ==================== CORE UI METHODS ====================
    # (باقی متدهای اصلی که قبلاً پیاده‌سازی شده‌اند)
    
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
    
    # ==================== PLACEHOLDER IMPLEMENTATIONS ====================
    # این متدها placeholder هستند و در آینده پیاده‌سازی خواهند شد
    
    async def _callback_toggle_notifications(self, query, user_id): pass
    async def _callback_set_notification_hours(self, query, user_id): pass
    async def _callback_filter_by_specialty(self, query, user_id): pass
    async def _callback_filter_by_location(self, query, user_id): pass
    async def _callback_user_preferences(self, query, user_id): pass
    async def _callback_language_settings(self, query, user_id): pass
    async def _callback_theme_settings(self, query, user_id): pass
    async def _callback_export_data(self, query, user_id): pass
    async def _callback_appointment_history(self, query, user_id): pass
    async def _callback_share_doctor(self, query, user_id): pass
    async def _callback_rate_doctor(self, query, user_id): pass
    async def _callback_doctor_reviews(self, query, user_id): pass
    async def _callback_admin_doctors(self, query, user_id): pass
    async def _callback_admin_users(self, query, user_id): pass
    async def _callback_admin_stats(self, query, user_id): pass
    async def _callback_admin_settings(self, query, user_id): pass
    async def _callback_video_tutorial(self, query): pass
    async def _callback_faq(self, query): pass
    async def _callback_contact_support(self, query): pass
    async def _callback_contact_admin(self, query): pass
    async def _callback_pagination(self, query, data, user_id): pass
    async def _callback_filter(self, query, data, user_id): pass
    
    # ==================== EXISTING IMPLEMENTATIONS ====================
    # (باقی متدهای موجود که قبلاً پیاده‌سازی شده‌اند)
    
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
                
                # ==================== FUTURE: ADDITIONAL DOCTOR ACTIONS ====================
                # اینجا می‌توانید عملیات اضافی برای دکتر اضافه کنید:
                # keyboard.append([
                #     InlineKeyboardButton("⭐ امتیاز دهی", callback_data=f"rate_doctor_{doctor.id}"),
                #     InlineKeyboardButton("📤 اشتراک‌گذاری", callback_data=f"share_doctor_{doctor.id}")
                # ])
                
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
    
    # ==================== REMAINING CORE METHODS ====================
    # (باقی متدهای اصلی که برای کوتاهی حذف شده‌اند)
    
    async def _show_subscriptions_modern(self, message, user_id):
        """نمایش اشتراک‌ها"""
        # Implementation similar to before...
        pass
    
    async def _show_new_subscription_modern(self, message, user_id):
        """نمایش اشتراک جدید"""
        # Implementation similar to before...
        pass
    
    async def _show_user_status_modern(self, message, user_id):
        """نمایش وضعیت کاربر"""
        # Implementation similar to before...
        pass
    
    async def _show_admin_panel_modern(self, message):
        """نمایش پنل ادمین مدرن"""
        # Implementation similar to before...
        pass