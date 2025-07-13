"""
ربات تلگرام اصلی
"""
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from typing import List

from src.telegram_bot.handlers import TelegramHandlers
from src.telegram_bot.menu_handlers import MenuHandlers
from src.telegram_bot.callback_handlers import CallbackHandlers
from src.telegram_bot.admin_handlers import TelegramAdminHandlers, ADD_DOCTOR_LINK, ADD_DOCTOR_CONFIRM, SET_CHECK_INTERVAL
from src.telegram_bot.messages import MessageFormatter
from src.database.database import db_session, DatabaseManager
from src.database.models import User, Subscription, Doctor, AppointmentLog
from src.api.models import Appointment
from src.utils.logger import get_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from src.database.models import Doctor as DBDoctor
from datetime import datetime
from sqlalchemy import select, func

logger = get_logger("TelegramBot")


class SlotHunterBot:
    """کلاس اصلی ربات تلگرام"""
    
    def __init__(self, token: str, db_manager: DatabaseManager):
        self.token = token
        self.bot = Bot(token)
        self.db_manager = db_manager
        self.application = None
        self.is_running = False
        
    async def initialize(self):
        """راه‌اندازی ربات"""
        try:
            # ایجاد Application
            self.application = Application.builder().token(self.token).build()
            
            # تنظیم handlers
            self._setup_handlers()
            
            # راه‌اندازی
            await self.application.initialize()
            await self.application.start()
            
            # دریافت اطلاعات ربات
            bot_info = await self.bot.get_me()
            logger.info(f"🤖 ربات راه‌اندازی شد: @{bot_info.username}")
            
            self.is_running = True
            
        except ValueError as e:
            logger.error(f"❌ خطا در تنظیمات ربات (توکن نامعتبر): {e}")
            raise
        except ConnectionError as e:
            logger.error(f"❌ خطا در اتصال به تلگرام: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره در راه‌اندازی ربات: {e}")
            raise
    
    def _setup_handlers(self):
        """تنظیم handler های ربات"""
        
        # ConversationHandler برای افزودن دکتر
        add_doctor_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(TelegramAdminHandlers.start_add_doctor, pattern="^admin_add_doctor$")],
            states={
                ADD_DOCTOR_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, TelegramAdminHandlers.process_doctor_link)],
                ADD_DOCTOR_CONFIRM: [
                    CallbackQueryHandler(TelegramAdminHandlers.confirm_add_doctor, pattern="^confirm_add_doctor$"),
                    CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern="^cancel_add_doctor$")
                ]
            },
            fallbacks=[CommandHandler("cancel", TelegramAdminHandlers.cancel_conversation)]
        )
        
        # ConversationHandler برای تنظیم زمان بررسی
        set_interval_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(TelegramAdminHandlers.set_check_interval, pattern="^admin_set_interval$")],
            states={
                SET_CHECK_INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, TelegramAdminHandlers.process_check_interval)]
            },
            fallbacks=[CommandHandler("cancel", TelegramAdminHandlers.cancel_conversation)]
        )
        
        # Callback query handlers - Order matters!
        # Conversation handlers MUST come first to catch their entry points
        self.application.add_handler(add_doctor_conv)
        self.application.add_handler(set_interval_conv)
        
        # Command handlers (legacy support)
        self.application.add_handler(CommandHandler("start", self._handle_start_command))
        self.application.add_handler(CommandHandler("help", TelegramHandlers.help_command))
        self.application.add_handler(CommandHandler("doctors", TelegramHandlers.doctors_command))
        self.application.add_handler(CommandHandler("subscribe", TelegramHandlers.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", TelegramHandlers.unsubscribe_command))
        self.application.add_handler(CommandHandler("status", TelegramHandlers.status_command))
        
        # Specific admin callbacks - These must come before the general handler
        self.application.add_handler(CallbackQueryHandler(TelegramAdminHandlers.manage_doctors, pattern="^admin_manage_doctors$"))
        self.application.add_handler(CallbackQueryHandler(TelegramAdminHandlers.toggle_doctor_status, pattern="^toggle_doctor_"))
        self.application.add_handler(CallbackQueryHandler(TelegramAdminHandlers.show_admin_stats, pattern="^admin_stats$"))
        self.application.add_handler(CallbackQueryHandler(TelegramAdminHandlers.show_user_management, pattern="^admin_manage_users$"))
        self.application.add_handler(CallbackQueryHandler(TelegramAdminHandlers.show_access_settings, pattern="^admin_access_settings$"))
        self.application.add_handler(CallbackQueryHandler(self._handle_admin_callbacks, pattern="^back_to_admin_panel$"))
        
        # Menu callbacks (new role-based system) - This handles all other callbacks
        self.application.add_handler(CallbackQueryHandler(CallbackHandlers.handle_callback_query))
        
        # Menu-based message handlers - MUST be last to not interfere with conversations
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            MenuHandlers.handle_main_menu
        ))
        
        logger.info("✅ Handler های ربات تنظیم شدند")
    
    async def _handle_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت دستور /start با منوی جدید"""
        try:
            user = update.effective_user
            
            # ثبت/به‌روزرسانی کاربر در دیتابیس
            await MenuHandlers._ensure_user_exists(user)
            
            # نمایش منوی خوش‌آمدگویی
            await MenuHandlers.show_welcome_menu(update, context)
            
        except ConnectionError as e:
            logger.error(f"❌ خطا در اتصال به دیتابیس در دستور start: {e}")
            await update.message.reply_text(
                "❌ خطا در اتصال به سیستم. لطفاً دوباره تلاش کنید.",
                reply_markup=MenuHandlers.get_main_menu_keyboard()
            )
        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره در دستور start: {e}")
            await update.message.reply_text(
                "❌ خطا در پردازش درخواست. لطفاً دوباره تلاش کنید.",
                reply_markup=MenuHandlers.get_main_menu_keyboard()
            )
    
    async def _handle_admin_callbacks(self, update, context):
        """مدیریت callback های ادمین"""
        query = update.callback_query
        await query.answer()

        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text(MessageFormatter.access_denied_message())
            return
        
        if query.data == "admin_stats":
            await self._show_admin_stats(query)
        elif query.data == "admin_manage_users":
            await self._show_user_management(query)
        elif query.data == "admin_access_settings":
            await self._show_access_settings(query)
        elif query.data == "back_to_admin_panel":
            await TelegramAdminHandlers.admin_panel(update, context)
    
    async def _show_admin_stats(self, query):
        """نمایش آمار سیستم"""
        try:
            async with db_session(self.db_manager) as session:
                total_users = await session.scalar(select(func.count(User.id)).filter(User.is_active == True))
                total_doctors = await session.scalar(select(func.count(Doctor.id)))
                active_doctors = await session.scalar(select(func.count(Doctor.id)).filter(Doctor.is_active == True))
                total_subscriptions = await session.scalar(select(func.count(Subscription.id)).filter(Subscription.is_active == True))
                
                from datetime import timedelta
                
                today = datetime.now().date()
                appointments_today = await session.scalar(
                    select(func.count(AppointmentLog.id)).filter(AppointmentLog.created_at >= today)
                )
                
                stats = {
                    'total_users': total_users,
                    'total_doctors': total_doctors,
                    'active_doctors': active_doctors,
                    'total_subscriptions': total_subscriptions,
                    'appointments_today': appointments_today,
                }
                stats_text = MessageFormatter.admin_stats_message(stats)
                
                keyboard = [[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_panel")
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطا در نمایش آمار: {e}")
            await query.edit_message_text(MessageFormatter.error_message("خطا در دریافت آمار سیستم"))
    
    async def _show_user_management(self, query):
        """مدیریت کاربران"""
        try:
            async with db_session(self.db_manager) as session:
                result = await session.execute(select(User).filter(User.is_active == True).order_by(User.created_at.desc()).limit(10))
                users = result.scalars().all()
                
                user_list = MessageFormatter.user_management_message(users)
                
                keyboard = [[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_panel")
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(user_list, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطا در مدیریت کاربران: {e}")
            await query.edit_message_text(MessageFormatter.error_message("خطا در بارگذاری لیست کاربران"))
    
    async def _show_access_settings(self, query):
        """تنظیمات دسترسی"""
        
        access_text = MessageFormatter.access_settings_message()
        
        keyboard = [[
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_panel")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(access_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def start_polling(self):
        """شروع polling"""
        if not self.application:
            await self.initialize()
        
        try:
            logger.info("🔄 شروع polling...")
            await self.application.updater.start_polling()
            
            # نگه داشتن ربات زنده
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ خطا در polling: {e}")
            raise
    
    async def stop(self):
        """توقف ربات"""
        try:
            self.is_running = False
            
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
            logger.info("🛑 ربات متوقف شد")
            
        except Exception as e:
            logger.error(f"❌ خطا در توقف ربات: {e}")
    
    async def send_appointment_alert(self, db_doctor: DBDoctor, appointments: List[Appointment]):
        """ارسال اطلاع‌رسانی نوبت جدید"""
        try:
            # دریافت مشترکین فعال این دکتر
            async with db_session(self.db_manager) as session:
                session.add(db_doctor)
                
                # دریافت مشترکین فعال
                result = await session.execute(
                    select(Subscription).filter(
                        Subscription.doctor_id == db_doctor.id,
                        Subscription.is_active == True
                    )
                )
                active_subscriptions = result.scalars().all()
                
                if not active_subscriptions:
                    logger.info(f"📭 هیچ مشترکی برای {db_doctor.name} وجود ندارد")
                    return
                
                # ایجاد پیام
                message = MessageFormatter.appointment_alert_message(db_doctor, appointments)
                
                # ارسال به تمام مشترکین
                sent_count = 0
                failed_count = 0
                
                for subscription in active_subscriptions:
                    try:
                        await self.bot.send_message(
                            chat_id=subscription.user.telegram_id,
                            text=message,
                            parse_mode='Markdown',
                            disable_web_page_preview=True
                        )
                        sent_count += 1
                        
                        # کمی صبر برای جلوگیری از rate limiting
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"❌ خطا در ارسال به {subscription.user.telegram_id}: {e}")
                        failed_count += 1
                        
                        # اگر کاربر ربات را block کرده، اشتراک را غیرفعال کن
                        if "bot was blocked" in str(e).lower():
                            subscription.is_active = False
                            await session.commit()
                            logger.info(f"🚫 کاربر {subscription.user.telegram_id} ربات را block کرده")
                
                logger.info(
                    f"📢 اطلاع‌رسانی {db_doctor.name}: "
                    f"✅ {sent_count} موفق، ❌ {failed_count} ناموفق"
                )
                
                # ثبت لاگ در دیتابیس
                appointment_log = AppointmentLog(
                    doctor_id=db_doctor.id,
                    appointment_date=appointments[0].start_datetime,
                    appointment_count=len(appointments),
                    notified_users=sent_count
                )
                session.add(appointment_log)
                await session.commit()
                
        except Exception as e:
            logger.error(f"❌ خطا در ارسال اطلاع‌رسانی: {e}")
    
    async def send_admin_message(self, message: str, admin_chat_id: int):
        """ارسال پیام به ادمین"""
        try:
            await self.bot.send_message(
                chat_id=admin_chat_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"❌ خطا در ارسال پیام ادمین: {e}")
    
    async def get_bot_stats(self) -> dict:
        """دریافت آمار ربات"""
        try:
            async with db_session(self.db_manager) as session:
                total_users = await session.scalar(select(func.count(User.id)).filter(User.is_active == True))
                total_subscriptions = await session.scalar(
                    select(func.count(Subscription.id)).filter(Subscription.is_active == True)
                )
                
                from datetime import timedelta
                
                today = datetime.now().date()
                appointments_today = await session.scalar(
                    select(func.count(AppointmentLog.id)).filter(AppointmentLog.created_at >= today)
                )
                
                return {
                    'total_users': total_users,
                    'total_subscriptions': total_subscriptions,
                    'appointments_found_today': appointments_today,
                    'bot_status': 'فعال' if self.is_running else 'غیرفعال'
                }
                
        except Exception as e:
            logger.error(f"❌ خطا در دریافت آمار: {e}")
            return {}
