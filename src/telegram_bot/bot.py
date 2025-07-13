"""
New Telegram Bot - معماری جدید و ساده
"""
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from typing import Optional

from src.telegram_bot.unified_handlers import UnifiedTelegramHandlers
from src.utils.logger import get_logger

logger = get_logger("NewTelegramBot")


class SlotHunterBot:
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
            
            logger.info("✅ ربات جدید راه‌��ندازی شد")
            
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
        app.add_handler(CommandHandler("status", self.handlers.status_command))
        app.add_handler(CommandHandler("admin", self.handlers.admin_command))
        
        # Message handler for persistent menu
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handlers.handle_text_message
        ))
        
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