"""
ربات تلگرام اصلی
"""
import asyncio
from telegram import Bot, Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ConversationHandler,
    MessageHandler, filters, ContextTypes, Defaults, AIORateLimiter
)
from typing import List

from src.telegram_bot.handlers import TelegramHandlers
from src.telegram_bot.menu_handlers import MenuHandlers
from src.telegram_bot.callback_handlers import CallbackHandlers
from src.telegram_bot.admin_handlers import TelegramAdminHandlers
from src.telegram_bot.constants import AdminCallback, ConversationStates
from src.telegram_bot.messages import MessageFormatter
from src.database.database import db_session
from src.database.models import User, Subscription, Doctor, AppointmentLog
from src.api.models import Appointment
from src.utils.logger import get_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import Forbidden, BadRequest, TimedOut, NetworkError

logger = get_logger("TelegramBot")


class SlotHunterBot:
    """کلاس اصلی ربات تلگرام"""
    
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token)
        self.application = None
        self.is_running = False
        
    async def initialize(self):
        """راه‌اندازی ربات"""
        try:
            # تنظیمات پیش‌فرض با Rate Limiter
            # این کار باعث می‌شود تا هر کاربر نتواند بیش از حد درخواست ارسال کند
            defaults = Defaults(
                rate_limiter=AIORateLimiter(
                    max_retries=3,  # حداکثر تلاش مجدد در صورت خطا
                    time_period=10  # بازه زمانی برای محدودیت (مثلا ۱۰ ثانیه)
                ),
                block=False # جلوگیری از بلاک شدن کامل ربات
            )

            # ایجاد Application با تنظیمات جدید
            self.application = Application.builder().token(self.token).defaults(defaults).build()
            
            # تنظیم handlers
            self._setup_handlers()
            
            # راه‌اندازی
            await self.application.initialize()
            await self.application.start()
            
            # دریافت اطلاعات ربات
            bot_info = await self.bot.get_me()
            logger.info(f"🤖 ربات راه‌اندازی شد: @{bot_info.username}")
            
            self.is_running = True
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
            raise
    
    def _setup_handlers(self):
        """تنظیم handler های ربات"""
        
        # ConversationHandler for adding a doctor
        add_doctor_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(TelegramAdminHandlers.start_add_doctor, pattern=f"^{AdminCallback.ADD_DOCTOR}$")],
            states={
                ConversationStates.ADD_DOCTOR_LINK.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, TelegramAdminHandlers.process_doctor_link)],
                ConversationStates.ADD_DOCTOR_CONFIRM.value: [
                    CallbackQueryHandler(TelegramAdminHandlers.confirm_add_doctor, pattern=f"^{AdminCallback.CONFIRM_ADD_DOCTOR}$"),
                    CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern=f"^{AdminCallback.CANCEL_ADD_DOCTOR}$")
                ]
            },
            fallbacks=[CommandHandler("cancel", TelegramAdminHandlers.cancel_conversation)]
        )

        # ConversationHandler for setting the check interval
        set_interval_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(TelegramAdminHandlers.set_check_interval, pattern=f"^{AdminCallback.SET_INTERVAL}$")],
            states={
                ConversationStates.SET_CHECK_INTERVAL.value: [MessageHandler(filters.TEXT & ~filters.COMMAND, TelegramAdminHandlers.process_check_interval)]
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
        
        # یکپارچه‌سازی CallbackQueryHandler ها
        # تمام callback ها توسط یک handler مدیریت می‌شوند
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
            
        except Exception as e:
            logger.error(f"❌ خطا در دستور start: {e}")
            await update.message.reply_text(
                MessageFormatter.error_message(),
                reply_markup=MenuHandlers.get_main_menu_keyboard()
            )
    
    async def _handle_admin_callbacks(self, update, context):
        """مدیریت callback های ادمین"""
        # این متد دیگر استفاده نمی‌شود و منطق آن به callback_handlers منتقل شده است
        pass
    
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
            with db_session() as session:
                total_users = session.query(User).filter(User.is_active == True).count()
                total_subscriptions = session.query(Subscription).filter(
                    Subscription.is_active == True
                ).count()
                
                from src.database.models import AppointmentLog
                from datetime import datetime, timedelta
                
                today = datetime.now().date()
                appointments_today = session.query(AppointmentLog).filter(
                    AppointmentLog.created_at >= today
                ).count()
                
                return {
                    'total_users': total_users,
                    'total_subscriptions': total_subscriptions,
                    'appointments_found_today': appointments_today,
                    'bot_status': 'فعال' if self.is_running else 'غیرفعال'
                }
                
        except Exception as e:
            logger.error(f"❌ خطا در دریافت آمار: {e}")
            return {}