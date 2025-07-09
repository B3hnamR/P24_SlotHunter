"""
ربات تلگرام اصلی
"""
import asyncio
from telegram import Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from typing import List

from src.telegram_bot.handlers import TelegramHandlers
from src.telegram_bot.admin_handlers import TelegramAdminHandlers, ADD_DOCTOR_LINK, ADD_DOCTOR_CONFIRM, SET_CHECK_INTERVAL
from src.telegram_bot.messages import MessageFormatter
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
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", TelegramHandlers.start_command))
        self.application.add_handler(CommandHandler("help", TelegramHandlers.help_command))
        self.application.add_handler(CommandHandler("doctors", TelegramHandlers.doctors_command))
        self.application.add_handler(CommandHandler("subscribe", TelegramHandlers.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", TelegramHandlers.unsubscribe_command))
        self.application.add_handler(CommandHandler("status", TelegramHandlers.status_command))
        
        # Admin commands
        self.application.add_handler(CommandHandler("admin", TelegramAdminHandlers.admin_panel))
        
        # Conversation handlers
        self.application.add_handler(add_doctor_conv)
        self.application.add_handler(set_interval_conv)
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(TelegramAdminHandlers.manage_doctors, pattern="^admin_manage_doctors$"))
        self.application.add_handler(CallbackQueryHandler(TelegramAdminHandlers.toggle_doctor_status, pattern="^toggle_doctor_"))
        self.application.add_handler(CallbackQueryHandler(self._handle_admin_callbacks, pattern="^admin_"))
        self.application.add_handler(CallbackQueryHandler(TelegramHandlers.button_callback))
        
        logger.info("✅ Handler های ربات تنظیم شدند")
    
    async def _handle_admin_callbacks(self, update, context):
        """مدیریت callback های ادمین"""
        query = update.callback_query
        await query.answer()
        
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
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return
        
        try:
            with db_session() as session:
                total_users = session.query(User).filter(User.is_active == True).count()
                total_doctors = session.query(Doctor).count()
                active_doctors = session.query(Doctor).filter(Doctor.is_active == True).count()
                total_subscriptions = session.query(Subscription).filter(Subscription.is_active == True).count()
                
                from src.database.models import AppointmentLog
                from datetime import datetime, timedelta
                
                today = datetime.now().date()
                appointments_today = session.query(AppointmentLog).filter(
                    AppointmentLog.created_at >= today
                ).count()
                
                stats_text = f"""
📊 **آمار سیستم P24_SlotHunter**

👥 **کارب��ان فعال:** {total_users}
👨‍⚕️ **کل دکترها:** {total_doctors}
✅ **دکترهای فعال:** {active_doctors}
📝 **اشتراک‌های فعال:** {total_subscriptions}
🎯 **نوبت‌های پیدا شده امروز:** {appointments_today}

⏰ **آخرین بررسی:** در حال اجرا
🔄 **وضعیت سیستم:** فعال
                """
                
                keyboard = [[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_panel")
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطا در نمایش آمار: {e}")
            await query.edit_message_text("❌ خطا در دریافت آمار سیستم.")
    
    async def _show_user_management(self, query):
        """مدیریت کاربران"""
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return
        
        try:
            with db_session() as session:
                users = session.query(User).filter(User.is_active == True).order_by(User.created_at.desc()).limit(10).all()
                
                user_list = "👥 **آخرین کاربران:**\n\n"
                
                for i, user in enumerate(users, 1):
                    subscription_count = len([sub for sub in user.subscriptions if sub.is_active])
                    admin_badge = " 🔧" if user.is_admin else ""
                    
                    user_list += f"{i}. {user.full_name}{admin_badge}\n"
                    user_list += f"   📱 ID: `{user.telegram_id}`\n"
                    user_list += f"   📝 اشتراک‌ها: {subscription_count}\n\n"
                
                keyboard = [[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_panel")
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(user_list, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطا در مدیریت کاربران: {e}")
            await query.edit_message_text("❌ خطا در بارگذاری لیست کاربران.")
    
    async def _show_access_settings(self, query):
        """تنظیمات دست��سی"""
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return
        
        access_text = """
🔒 **تنظیمات دسترسی**

⚠️ **وضعیت فعلی:** ربات برای همه در دسترس است

🔧 **برای محدود کردن دسترسی:**
1. از منوی مدیریت سرور استفاده کنید
2. گزینه "Access Control" را انتخاب کنید
3. لیست کاربران مجاز را تنظیم کنید

💡 **نکته:** تغییرات از طریق سرور اعمال می‌شود
        """
        
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
    
    async def send_appointment_alert(self, doctor: Doctor, appointments: List[Appointment]):
        """ارسال اطلاع‌رسانی نوبت جدید"""
        try:
            # دری��فت مشترکین فعال این دکتر
            with db_session() as session:
                # پیدا کردن دکتر در دیتابیس
                from src.database.models import Doctor as DBDoctor
                db_doctor = session.query(DBDoctor).filter(DBDoctor.slug == doctor.slug).first()
                
                if not db_doctor:
                    logger.warning(f"⚠️ دکتر {doctor.name} در دیتا��یس یافت نشد")
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