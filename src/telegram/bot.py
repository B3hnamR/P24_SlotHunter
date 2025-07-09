"""
ربات تلگرام اصلی
"""
import asyncio
from telegram import Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from typing import List

from src.telegram.handlers import TelegramHandlers
from src.telegram.messages import MessageFormatter
from src.database.database import db_session
from src.database.models import User, Subscription
from src.api.models import Doctor, Appointment
from src.utils.logger import get_logger

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
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
            raise
    
    def _setup_handlers(self):
        """تنظیم handler های ربات"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", TelegramHandlers.start_command))
        self.application.add_handler(CommandHandler("help", TelegramHandlers.help_command))
        self.application.add_handler(CommandHandler("doctors", TelegramHandlers.doctors_command))
        self.application.add_handler(CommandHandler("subscribe", TelegramHandlers.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", TelegramHandlers.unsubscribe_command))
        self.application.add_handler(CommandHandler("status", TelegramHandlers.status_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(TelegramHandlers.button_callback))
        
        logger.info("✅ Handler های ربات تنظیم شدند")
    
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
    
    async def send_appointment_alert(self, doctor: Doctor, appointments: List[Appointment]):
        """ارسال اطلاع‌رسانی نوبت جدید"""
        try:
            # دری��فت مشترکین فعال این دکتر
            with db_session() as session:
                # پیدا کردن دکتر در دیتابیس
                from src.database.models import Doctor as DBDoctor
                db_doctor = session.query(DBDoctor).filter(DBDoctor.slug == doctor.slug).first()
                
                if not db_doctor:
                    logger.warning(f"⚠️ دکتر {doctor.name} در دیتابیس یافت نشد")
                    return
                
                # دریافت مشترکین فعال
                active_subscriptions = session.query(Subscription).filter(
                    Subscription.doctor_id == db_doctor.id,
                    Subscription.is_active == True
                ).all()
                
                if not active_subscriptions:
                    logger.info(f"📭 هیچ مشترکی برای {doctor.name} وجود ندارد")
                    return
                
                # ایجاد پیام
                message = MessageFormatter.appointment_alert_message(doctor, appointments)
                
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
                            session.commit()
                            logger.info(f"🚫 کاربر {subscription.user.telegram_id} ربات را block کرده")
                
                logger.info(
                    f"📢 اطلاع‌رسانی {doctor.name}: "
                    f"✅ {sent_count} موفق، ❌ {failed_count} ناموفق"
                )
                
                # ثبت لاگ در دیتابیس
                from src.database.models import AppointmentLog
                from datetime import datetime
                
                appointment_log = AppointmentLog(
                    doctor_id=db_doctor.id,
                    appointment_date=appointments[0].start_datetime,
                    appointment_count=len(appointments),
                    notified_users=sent_count
                )
                session.add(appointment_log)
                session.commit()
                
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