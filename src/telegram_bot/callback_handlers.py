"""
Callback handlers for inline keyboard buttons
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.database.database import db_session
from src.database.models import User, Doctor, Subscription, AppointmentLog
from src.telegram_bot.messages import MessageFormatter
from src.telegram_bot.menu_handlers import MenuHandlers
from src.utils.logger import get_logger

logger = get_logger("CallbackHandlers")


class CallbackHandlers:
    """کلاس مدیریت callback های دکمه‌های inline"""
    
    @staticmethod
    async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کلی callback query ها"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            
            # مدیریت callback های مختلف
            if data == "back_to_main":
                await CallbackHandlers._handle_back_to_main(query)
            elif data == "back_to_doctors":
                await CallbackHandlers._handle_back_to_doctors(query)
            elif data.startswith("doctor_info_"):
                await CallbackHandlers._handle_doctor_info(query, data, user_id)
            elif data.startswith("subscribe_"):
                await CallbackHandlers._handle_subscribe(query, data, user_id)
            elif data.startswith("unsubscribe_"):
                await CallbackHandlers._handle_unsubscribe(query, data, user_id)
            elif data.startswith("view_website_"):
                await CallbackHandlers._handle_view_website(query, data)
            elif data.startswith("stats_"):
                await CallbackHandlers._handle_doctor_stats(query, data, user_id)
            elif data.startswith("settings_"):
                await CallbackHandlers._handle_settings(query, data, user_id)
            elif data == "subscription_stats":
                await CallbackHandlers._handle_subscription_stats(query, user_id)
            elif data == "refresh_all_subscriptions":
                await CallbackHandlers._handle_refresh_subscriptions(query, user_id)
            elif data == "unsubscribe_all_confirm":
                await CallbackHandlers._handle_unsubscribe_all_confirm(query, user_id)
            elif data == "unsubscribe_all_execute":
                await CallbackHandlers._handle_unsubscribe_all_execute(query, user_id)
            elif data == "new_subscription":
                await CallbackHandlers._handle_new_subscription(query, user_id)
            elif data == "refresh_status":
                await CallbackHandlers._handle_refresh_status(query, user_id)
            elif data == "detailed_stats":
                await CallbackHandlers._handle_detailed_stats(query, user_id)
            elif data.startswith("help_"):
                await CallbackHandlers._handle_help_callbacks(query, data)
            elif data.startswith("support_"):
                await CallbackHandlers._handle_support_callbacks(query, data, user_id)
            elif data == "system_status":
                await CallbackHandlers._handle_system_status(query)
            elif data == "show_doctors":
                await CallbackHandlers._handle_show_doctors(query)
            elif data == "show_subscriptions":
                await CallbackHandlers._handle_show_subscriptions(query, user_id)
            # Admin callbacks
            elif data.startswith("admin_"):
                await CallbackHandlers._handle_admin_callbacks(query, data, user_id)
            elif data.startswith("super_"):
                await CallbackHandlers._handle_super_admin_callbacks(query, data, user_id)
            elif data.startswith("advanced_"):
                await CallbackHandlers._handle_advanced_settings_callbacks(query, data, user_id)
            elif data.startswith("system_"):
                await CallbackHandlers._handle_system_callbacks(query, data, user_id)
            elif data.startswith("detailed_"):
                await CallbackHandlers._handle_detailed_callbacks(query, data, user_id)
            elif data.startswith("stats_"):
                await CallbackHandlers._handle_stats_callbacks(query, data, user_id)
            elif data.startswith("log_"):
                await CallbackHandlers._handle_log_callbacks(query, data, user_id)
            elif data.startswith("backup_"):
                await CallbackHandlers._handle_backup_callbacks(query, data, user_id)
            elif data.startswith("database_"):
                await CallbackHandlers._handle_database_callbacks(query, data, user_id)
            elif data.startswith("monitoring_"):
                await CallbackHandlers._handle_monitoring_callbacks(query, data, user_id)
            elif data.startswith("list_"):
                await CallbackHandlers._handle_list_callbacks(query, data, user_id)
            elif data.startswith("search_"):
                await CallbackHandlers._handle_search_callbacks(query, data, user_id)
            elif data.startswith("manage_"):
                await CallbackHandlers._handle_manage_callbacks(query, data, user_id)
            elif data.startswith("blocked_"):
                await CallbackHandlers._handle_blocked_callbacks(query, data, user_id)
            elif data.startswith("user_"):
                await CallbackHandlers._handle_user_callbacks(query, data, user_id)
            elif data.startswith("full_"):
                await CallbackHandlers._handle_full_callbacks(query, data, user_id)
            else:
                await query.edit_message_text(
                    "❌ دستور نامشخص. لطفاً دوباره تلاش کنید.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
                    ]])
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در مدیریت callback: {e}")
            try:
                await query.edit_message_text(
                    MessageFormatter.error_message("خطا در پردازش درخواست"),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
                    ]])
                )
            except:
                pass
    
    @staticmethod
    async def _handle_back_to_main(query):
        """بازگشت به منوی اصلی"""
        welcome_text = f"""
🎯 **منوی اصلی**

از دکمه‌های زیر برای استفاده از ربات استفاده کنید:

💡 **نکته:** برای دسترسی سریع‌تر، از منوی پایین صفحه استفاده کنید.
        """
        
        keyboard = [
            [InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors")],
            [InlineKeyboardButton("📝 مدیریت اشتراک‌ها", callback_data="show_subscriptions")],
            [InlineKeyboardButton("🔔 اشتراک جدید", callback_data="new_subscription")],
            [InlineKeyboardButton("📊 و��عیت من", callback_data="refresh_status")],
            [InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def _handle_back_to_doctors(query):
        """بازگشت به لیست دکترها"""
        try:
            with db_session() as session:
                doctors = session.query(Doctor).filter(Doctor.is_active == True).all()
                
                if not doctors:
                    await query.edit_message_text(
                        "❌ هیچ دکتری در سیستم ثبت نشده است.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
                        ]])
                    )
                    return
                
                doctors_text = f"""
👨‍⚕️ **لیست دکترهای موجود ({len(doctors)} دکتر):**

💡 روی نام دکتر کلیک کنید تا اطلاعات کامل را مشاهده کنید.
                """
                
                keyboard = MenuHandlers.get_doctors_inline_keyboard(doctors, "doctor_info")
                
                await query.edit_message_text(
                    doctors_text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در بازگشت به لیست دکترها: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_doctor_info(query, data, user_id):
        """نمایش اطلاعات دکتر"""
        try:
            doctor_id = int(data.split("_")[2])
            
            with db_session() as session:
                doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
                if not doctor:
                    await query.edit_message_text("❌ دکتر یافت نشد.")
                    return
                
                # بررسی اشتراک کاربر
                user = session.query(User).filter(User.telegram_id == user_id).first()
                is_subscribed = False
                if user:
                    subscription = session.query(Subscription).filter(
                        Subscription.user_id == user.id,
                        Subscription.doctor_id == doctor.id,
                        Subscription.is_active == True
                    ).first()
                    is_subscribed = subscription is not None
                
                # آمار نوبت‌های این دکتر
                today = datetime.now().date()
                appointments_today = session.query(AppointmentLog).filter(
                    AppointmentLog.doctor_id == doctor.id,
                    AppointmentLog.created_at >= today
                ).count()
                
                total_subscribers = session.query(Subscription).filter(
                    Subscription.doctor_id == doctor.id,
                    Subscription.is_active == True
                ).count()
                
                info_text = f"""
👨‍⚕️ **{doctor.name}**

🏥 **تخصص:** {doctor.specialty or 'نامشخص'}
🏢 **مرکز:** {doctor.center_name or 'نامشخص'}
📍 **آدرس:** {doctor.center_address or 'نامشخص'}
📞 **تلفن:** {doctor.center_phone or 'نامشخص'}

📊 **آمار:**
• مشترکین فعال: {total_subscribers} نفر
• نوبت‌های پیدا شده امروز: {appointments_today}
• وضعیت: {'�� فعال' if doctor.is_active else '⏸️ غیرفعال'}

🔗 **لینک مستقیم:**
https://www.paziresh24.com/dr/{doctor.slug}/

{'✅ شما در این دکتر مشترک هستید' if is_subscribed else '❌ شما در این دکتر مشترک نیستید'}
                """
                
                keyboard = MenuHandlers.get_doctor_actions_keyboard(doctor.id, is_subscribed)
                
                await query.edit_message_text(
                    info_text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش اطلاعات دکتر: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_subscribe(query, data, user_id):
        """مدیریت اشتراک"""
        try:
            doctor_id = int(data.split("_")[1])
            
            with db_session() as session:
                # بررسی وجود کاربر
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await query.edit_message_text("❌ ابتدا دستور /start را اجرا کنید.")
                    return
                
                # بررسی وجود دکتر
                doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
                if not doctor:
                    await query.edit_message_text("❌ دکتر یافت نشد.")
                    return
                
                # بررسی اشتراک قبلی
                existing_sub = session.query(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.doctor_id == doctor.id
                ).first()
                
                if existing_sub:
                    if existing_sub.is_active:
                        await query.edit_message_text(
                            f"✅ شما قبلاً در دکتر **{doctor.name}** مشترک هستید.",
                            parse_mode='Markdown',
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton("🔙 بازگشت", callback_data=f"doctor_info_{doctor.id}")
                            ]])
                        )
                        return
                    else:
                        # فعال‌سازی مجدد
                        existing_sub.is_active = True
                        existing_sub.created_at = datetime.utcnow()
                else:
                    # اشتراک جدید
                    new_subscription = Subscription(
                        user_id=user.id,
                        doctor_id=doctor.id
                    )
                    session.add(new_subscription)
                
                session.commit()
                
                success_text = f"""
✅ **اشتراک موفق!**

شما با موفقیت در دکتر **{doctor.name}** مشترک شدید.

🔔 از این پس، هر نوبت خالی فوراً به شما اطلاع داده می‌شود.

💡 **نکته:** نوبت‌ها ممکن است سریع تمام شوند، پس سریع عمل کنید!
                """
                
                keyboard = [
                    [InlineKeyboardButton("👨‍⚕️ اطلاعات دکتر", callback_data=f"doctor_info_{doctor.id}")],
                    [InlineKeyboardButton("📝 اشتراک‌های من", callback_data="show_subscriptions")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    success_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
                logger.info(f"📝 اشتراک جدید: {user.full_name} -> {doctor.name}")
                
        except Exception as e:
            logger.error(f"❌ خطا در اشتراک: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_unsubscribe(query, data, user_id):
        """مدیریت لغو اشتراک"""
        try:
            doctor_id = int(data.split("_")[1])
            
            with db_session() as session:
                # بررسی وجود کاربر
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await query.edit_message_text("❌ ابتدا دستور /start را اجرا کنید.")
                    return
                
                # بررسی وجود دکتر
                doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
                if not doctor:
                    await query.edit_message_text("❌ دکتر یافت نشد.")
                    return
                
                # پیدا کردن اشتراک
                subscription = session.query(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.doctor_id == doctor.id,
                    Subscription.is_active == True
                ).first()
                
                if not subscription:
                    await query.edit_message_text(
                        f"❌ شما در دکتر **{doctor.name}** مشترک نیستید.",
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 بازگشت", callback_data=f"doctor_info_{doctor.id}")
                        ]])
                    )
                    return
                
                # لغو اشتراک
                subscription.is_active = False
                session.commit()
                
                success_text = f"""
✅ **لغو اشتراک موفق!**

اشتراک شما از دکتر **{doctor.name}** لغو شد.

🔕 دیگر اطلاع‌رسانی نوبت‌های این دکتر دریافت نخواهید کرد.

💡 در ص��رت نیاز، می‌توانید مجدداً مشترک شوید.
                """
                
                keyboard = [
                    [InlineKeyboardButton("📝 اشتراک مجدد", callback_data=f"subscribe_{doctor.id}")],
                    [InlineKeyboardButton("📝 اشتراک‌های من", callback_data="show_subscriptions")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    success_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
                logger.info(f"🗑️ لغو اشتراک: {user.full_name} -> {doctor.name}")
                
        except Exception as e:
            logger.error(f"❌ خطا در لغو اشتراک: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_view_website(query, data):
        """نمایش لینک وب‌سایت دکتر"""
        try:
            doctor_id = int(data.split("_")[2])
            
            with db_session() as session:
                doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
                if not doctor:
                    await query.edit_message_text("❌ دکتر یافت نشد.")
                    return
                
                website_text = f"""
🔗 **لینک وب‌سایت دکتر {doctor.name}**

برای مشاهده نوبت‌ها و رزرو در سایت پذیرش۲۴:

👆 **کلیک کنید:** https://www.paziresh24.com/dr/{doctor.slug}/

💡 **نکته:** این لینک شما را مستقیماً به صفحه دکتر در سایت پذیرش۲۴ می‌برد.
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔙 بازگشت به دکتر", callback_data=f"doctor_info_{doctor.id}")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    website_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش لینک وب‌سایت: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_doctor_stats(query, data, user_id):
        """نمایش آمار دکتر"""
        try:
            doctor_id = int(data.split("_")[1])
            
            with db_session() as session:
                doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
                if not doctor:
                    await query.edit_message_text("❌ دکتر یافت نشد.")
                    return
                
                # آمار کلی
                total_subscribers = session.query(Subscription).filter(
                    Subscription.doctor_id == doctor.id,
                    Subscription.is_active == True
                ).count()
                
                # آمار نوبت‌ها
                today = datetime.now().date()
                week_ago = today - timedelta(days=7)
                month_ago = today - timedelta(days=30)
                
                appointments_today = session.query(AppointmentLog).filter(
                    AppointmentLog.doctor_id == doctor.id,
                    AppointmentLog.created_at >= today
                ).count()
                
                appointments_week = session.query(AppointmentLog).filter(
                    AppointmentLog.doctor_id == doctor.id,
                    AppointmentLog.created_at >= week_ago
                ).count()
                
                appointments_month = session.query(AppointmentLog).filter(
                    AppointmentLog.doctor_id == doctor.id,
                    AppointmentLog.created_at >= month_ago
                ).count()
                
                # آخرین بررسی
                last_check = doctor.last_checked.strftime('%Y/%m/%d %H:%M') if doctor.last_checked else 'هرگز'
                
                stats_text = f"""
📊 **آمار دکتر {doctor.name}**

👥 **مشترکین:**
• مشترکین فعال: {total_subscribers} نفر

🎯 **نوبت‌های پیدا شده:**
• امروز: {appointments_today}
• این هفته: {appointments_week}
• این ماه: {appointments_month}

⏰ **آخرین بررسی:** {last_check}

🔄 **وضعیت:** {'✅ فعال' if doctor.is_active else '⏸️ غیرفعال'}

📅 **تاریخ افزودن:** {doctor.created_at.strftime('%Y/%m/%d') if doctor.created_at else 'نامشخص'}
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"stats_{doctor.id}")],
                    [InlineKeyboardButton("🔙 بازگشت به دکتر", callback_data=f"doctor_info_{doctor.id}")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    stats_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش آمار دکتر: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_settings(query, data, user_id):
        """مدیریت تنظیمات"""
        setting_type = data.split("_")[1]
        
        if setting_type == "main":
            await query.edit_message_text(
                "⚙️ **تنظیمات ربات**\n\nاز گزینه‌های زیر استفاده کنید:",
                parse_mode='Markdown',
                reply_markup=MenuHandlers.get_settings_keyboard()
            )
        elif setting_type == "notifications":
            await CallbackHandlers._handle_notification_settings(query, user_id)
        elif setting_type == "time":
            await CallbackHandlers._handle_time_settings(query, user_id)
        elif setting_type == "language":
            await CallbackHandlers._handle_language_settings(query, user_id)
        elif setting_type == "privacy":
            await CallbackHandlers._handle_privacy_settings(query, user_id)
    
    @staticmethod
    async def _handle_notification_settings(query, user_id):
        """تنظیمات اطلاع‌رسانی"""
        settings_text = """
🔔 **تنظیمات اطلاع‌رسانی**

⚙️ **گزینه‌های موجود:**
• فعال/غیرفعال کردن اطلاع‌رسانی‌ها
• تنظیم ساعات دریافت پیام
• انتخاب نوع اطلاع‌رسانی

🔧 **این قسمت در حال توسعه است.**
        """
        
        keyboard = [
            [InlineKeyboardButton("🔔 فعال/غیرفعال", callback_data="notif_toggle")],
            [InlineKeyboardButton("⏰ ساعات دریافت", callback_data="notif_hours")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="settings_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            settings_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def _handle_time_settings(query, user_id):
        """تنظیمات زمان"""
        await query.edit_message_text(
            "⏰ **تنظیمات زمان**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="settings_main")
            ]])
        )
    
    @staticmethod
    async def _handle_language_settings(query, user_id):
        """تنظیمات زبان"""
        await query.edit_message_text(
            "🌐 **تنظیمات زبان**\n\n🔧 فعلاً فقط زبان فارسی پشتیبانی می‌شود.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="settings_main")
            ]])
        )
    
    @staticmethod
    async def _handle_privacy_settings(query, user_id):
        """تنظیمات حریم خصوصی"""
        await query.edit_message_text(
            "🔒 **تنظیمات حریم خصوصی**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="settings_main")
            ]])
        )
    
    @staticmethod
    async def _handle_subscription_stats(query, user_id):
        """آمار اشتراک‌ها"""
        try:
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await query.edit_message_text("❌ کاربر یافت نشد.")
                    return
                
                active_subs = [sub for sub in user.subscriptions if sub.is_active]
                total_subs = len(user.subscriptions)
                
                # آمار نوبت‌ها
                today = datetime.now().date()
                week_ago = today - timedelta(days=7)
                
                appointments_today = session.query(AppointmentLog).join(Doctor).join(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.is_active == True,
                    AppointmentLog.created_at >= today
                ).count()
                
                appointments_week = session.query(AppointmentLog).join(Doctor).join(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.is_active == True,
                    AppointmentLog.created_at >= week_ago
                ).count()
                
                stats_text = f"""
📊 **آمار اشتراک‌های من**

📝 **اشتراک‌ها:**
• اشتراک‌های فعال: {len(active_subs)}
• کل اشتراک‌ها: {total_subs}

🎯 **نوبت‌های پیدا شده:**
�� امروز: {appointments_today}
• این هفته: {appointments_week}

📅 **تاریخ عضویت:** {user.created_at.strftime('%Y/%m/%d') if user.created_at else 'نامشخص'}

⏰ **آخرین فعالیت:** {user.last_activity.strftime('%Y/%m/%d %H:%M') if user.last_activity else 'نامشخص'}
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data="subscription_stats")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="show_subscriptions")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    stats_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش آمار اشتراک‌ها: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_refresh_subscriptions(query, user_id):
        """بروزرسانی اشتراک‌ها"""
        await query.edit_message_text(
            "🔄 **بروزرسانی اشتراک‌ها**\n\n�� اشتراک‌های شما بروزرسانی شد.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="show_subscriptions")
            ]])
        )
    
    @staticmethod
    async def _handle_unsubscribe_all_confirm(query, user_id):
        """تأیید لغو همه اشتراک‌ها"""
        confirm_text = """
⚠️ **تأیید لغو همه اشتراک‌ها**

آیا مطمئن هستید که می‌خواهید همه اشتراک‌های خود را لغو کنید؟

🔴 **توجه:** این عمل قابل بازگشت نیست و دیگر هیچ اطلاع‌رسانی‌ای دریافت نخواهید کرد.
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ بله، همه را لغو کن", callback_data="unsubscribe_all_execute")],
            [InlineKeyboardButton("❌ انصراف", callback_data="show_subscriptions")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            confirm_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def _handle_unsubscribe_all_execute(query, user_id):
        """اجرای لغو همه اشتراک‌ها"""
        try:
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await query.edit_message_text("❌ کاربر یافت نشد.")
                    return
                
                # لغو همه اشتراک‌های فعال
                active_subs = session.query(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.is_active == True
                ).all()
                
                count = len(active_subs)
                
                for sub in active_subs:
                    sub.is_active = False
                
                session.commit()
                
                success_text = f"""
✅ **لغو همه اشتراک‌ها موفق!**

{count} اشتراک با موفقیت لغو شد.

🔕 دیگر هیچ اطلاع‌رسانی‌ای دریافت نخواهید کرد.

💡 در صورت نیاز، می‌توانید مجدداً مشترک شوید.
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔔 اشتراک جدید", callback_data="new_subscription")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    success_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
                logger.info(f"🗑️ لغو همه اشتراک‌ها: {user.full_name} ({count} اشتراک)")
                
        except Exception as e:
            logger.error(f"❌ خطا در لغو همه اشتراک‌ها: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_new_subscription(query, user_id):
        """اشتراک جدید"""
        try:
            with db_session() as session:
                # دریافت دکترهای فعال
                doctors = session.query(Doctor).filter(Doctor.is_active == True).all()
                
                if not doctors:
                    await query.edit_message_text(
                        "❌ هیچ دکتری ��رای اشتراک موجود نیست.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
                        ]])
                    )
                    return
                
                # دریافت اشتراک‌های فعلی کاربر
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await query.edit_message_text("❌ کاربر یافت نشد.")
                    return
                
                subscribed_doctor_ids = [
                    sub.doctor_id for sub in user.subscriptions if sub.is_active
                ]
                
                # فیلتر دکترهای غیرمشترک
                available_doctors = [
                    doctor for doctor in doctors 
                    if doctor.id not in subscribed_doctor_ids
                ]
                
                if not available_doctors:
                    await query.edit_message_text(
                        "✅ شما در تمام دکترها�� موجود مشترک هستید!",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
                        ]])
                    )
                    return
                
                text = f"""
🔔 **اشتراک جدید**

{len(available_doctors)} دکتر برای اشتراک موجود است:

💡 روی نام دکتر کلیک کنید تا مشترک شوید.
                """
                
                keyboard = MenuHandlers.get_doctors_inline_keyboard(available_doctors, "subscribe")
                
                await query.edit_message_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در اشتراک جدید: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_refresh_status(query, user_id):
        """بروزرسانی وضعیت کاربر"""
        try:
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await query.edit_message_text("❌ کاربر یافت نشد.")
                    return
                
                # بروزرسانی آخرین فعالیت
                user.last_activity = datetime.utcnow()
                session.commit()
                
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
📊 **وضعیت من (بروزرسانی شده)**

👤 **اطلاعات کاربری:**
• نام: {user.full_name}
• شناسه: `{user.telegram_id}`
• تاریخ عضویت: {user.created_at.strftime('%Y/%m/%d') if user.created_at else 'نامشخص'}

📝 **اشتراک‌ها:**
• اشتراک‌های فعال: {len(active_subscriptions)}
• ��ل اشتراک‌ها: {total_subscriptions}

🎯 **آمار امروز:**
• نوبت‌های پیدا شده: {appointments_today}

⏰ **آخرین بروزرسانی:** {datetime.now().strftime('%Y/%m/%d %H:%M')}
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 بروزرسانی مجدد", callback_data="refresh_status")],
                    [InlineKeyboardButton("📊 آمار تفصیلی", callback_data="detailed_stats")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    status_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در بروزرسانی وضعیت: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_detailed_stats(query, user_id):
        """آمار تفصیلی کاربر"""
        try:
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await query.edit_message_text("❌ کاربر یافت نشد.")
                    return
                
                # آمار تفصیلی
                active_subs = [sub for sub in user.subscriptions if sub.is_active]
                inactive_subs = [sub for sub in user.subscriptions if not sub.is_active]
                
                # آمار نوبت‌ها در بازه‌های مختلف
                today = datetime.now().date()
                week_ago = today - timedelta(days=7)
                month_ago = today - timedelta(days=30)
                
                appointments_today = session.query(AppointmentLog).join(Doctor).join(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.is_active == True,
                    AppointmentLog.created_at >= today
                ).count()
                
                appointments_week = session.query(AppointmentLog).join(Doctor).join(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.is_active == True,
                    AppointmentLog.created_at >= week_ago
                ).count()
                
                appointments_month = session.query(AppointmentLog).join(Doctor).join(Subscription).filter(
                    Subscription.user_id == user.id,
                    Subscription.is_active == True,
                    AppointmentLog.created_at >= month_ago
                ).count()
                
                detailed_text = f"""
📊 **آمار تفصیلی**

👤 **پروفایل:**
• نام کامل: {user.full_name}
• نام کاربری: @{user.username or 'ندارد'}
• شناسه عددی: `{user.telegram_id}`

📝 **اشتراک‌ها:**
• فعال: {len(active_subs)}
• غیرفعال: {len(inactive_subs)}
• کل: {len(user.subscriptions)}

🎯 **نوبت‌های پیدا شده:**
• امروز: {appointments_today}
• این هفته: {appointments_week}
• این ماه: {appointments_month}

📅 **تاریخ‌ها:**
• عضویت: {user.created_at.strftime('%Y/%m/%d %H:%M') if user.created_at else 'نامشخص'}
• آخرین فعالیت: {user.last_activity.strftime('%Y/%m/%d %H:%M') if user.last_activity else 'نامشخص'}

🔄 **وضعیت حساب:** {'✅ فعال' if user.is_active else '❌ غیرفعال'}
                """
                
                keyboard = [
                    [InlineKeyboardButton("📊 آمار ساده", callback_data="refresh_status")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    detailed_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش آمار تفصیلی: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_help_callbacks(query, data):
        """مدیریت callback های راهنما"""
        help_type = data.split("_")[1]
        
        if help_type == "video":
            await query.edit_message_text(
                "🎥 **ویدیو آموزشی**\n\n🔧 ویدیو آموزشی در حال تهیه است.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
                ]])
            )
        elif help_type == "faq":
            faq_text = """
❓ **سوالات متداول**

**س: چگونه مشترک شوم؟**
ج: از منوی "🔔 اشتراک جدید" استفاده کنید.

**س: چرا نوبتی دریافت نمی‌کنم؟**
ج: ممکن است نوبت خالی موجود نباشد یا اشتراک شما غیرفعال باشد.

**س: چگونه اشتراک لغو کنم؟**
ج: از منوی "🗑️ لغو اشتراک" استفاده کنید.

**س: آیا رایگان است؟**
ج: بله، استفاده از ربات کاملاً رایگان است.
            """
            
            await query.edit_message_text(
                faq_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
                ]])
            )
        elif help_type == "contact":
            await query.edit_message_text(
                "📞 **تماس با پشتیبانی**\n\n🔧 اطلاعات تماس در حال بروزرسانی است.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
                ]])
            )
    
    @staticmethod
    async def _handle_support_callbacks(query, data, user_id):
        """مدیریت callback های پشتیبانی"""
        support_type = data.split("_")[1]
        
        if support_type == "chat":
            await query.edit_message_text(
                "💬 **چت با پشتیبانی**\n\n🔧 سیستم چت در حال توسعه است.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
                ]])
            )
        elif support_type == "bug":
            await query.edit_message_text(
                "🐛 **گزارش باگ**\n\n🔧 سیستم گزارش باگ در حال توسعه است.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
                ]])
            )
        elif support_type == "suggestion":
            await query.edit_message_text(
                "💡 **ارسال پیشنهاد**\n\n🔧 سیستم پیشنهادات در حال توسعه است.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
                ]])
            )
    
    @staticmethod
    async def _handle_system_status(query):
        """نمایش وضعیت سیستم"""
        try:
            with db_session() as session:
                # آمار کلی سیستم
                total_users = session.query(User).filter(User.is_active == True).count()
                total_doctors = session.query(Doctor).count()
                active_doctors = session.query(Doctor).filter(Doctor.is_active == True).count()
                total_subscriptions = session.query(Subscription).filter(Subscription.is_active == True).count()
                
                today = datetime.now().date()
                appointments_today = session.query(AppointmentLog).filter(
                    AppointmentLog.created_at >= today
                ).count()
                
                status_text = f"""
📋 **وضعیت سیستم**

👥 **کاربران:** {total_users} نفر فعال
👨‍⚕️ **دکترها:** {active_doctors}/{total_doctors} فعال
📝 **اشتراک‌ها:** {total_subscriptions} فعال
🎯 **نوبت‌های امروز:** {appointments_today}

🔄 **وضعیت سرویس:** ✅ فعال
⏰ **آخرین بروزرسانی:** {datetime.now().strftime('%Y/%m/%d %H:%M')}

💾 **سلامت سیستم:** ✅ عالی
🌐 **اتصال شبکه:** ✅ متصل
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data="system_status")],
                    [InlineKeyboardButton("🔙 بازگ��ت", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    status_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش وضعیت سیستم: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_show_doctors(query):
        """نمایش لیست دکترها از callback"""
        try:
            with db_session() as session:
                doctors = session.query(Doctor).filter(Doctor.is_active == True).all()
                
                if not doctors:
                    await query.edit_message_text(
                        "❌ هیچ دکتری در سیستم ثبت نشده است.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
                        ]])
                    )
                    return
                
                doctors_text = f"""
👨‍⚕️ **لیست دکترهای موجود ({len(doctors)} دکتر):**

💡 روی نام دکتر کلیک کنید تا اطلاعات کامل را مشاهده کنید.
                """
                
                keyboard = MenuHandlers.get_doctors_inline_keyboard(doctors, "doctor_info")
                
                await query.edit_message_text(
                    doctors_text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش لیست دکترها: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_show_subscriptions(query, user_id):
        """نمایش اشتراک‌ها از callback"""
        try:
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await query.edit_message_text(
                        "❌ کاربر یافت نشد. لطفاً دوباره /start کنید.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
                        ]])
                    )
                    return
                
                active_subscriptions = [
                    sub for sub in user.subscriptions if sub.is_active
                ]
                
                if not active_subscriptions:
                    text = """
📝 **اشتراک‌های من**

❌ شما در هیچ دکتری مشترک نیستید.

💡 برای اشتراک جدید از دکمه زیر استفاده کنید.
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
                
                await query.edit_message_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش اشتراک‌ها: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    # Admin callback handlers
    @staticmethod
    async def _handle_admin_callbacks(query, data, user_id):
        """مدیریت callback های ادمین"""
        from src.telegram_bot.user_roles import user_role_manager
        
        # بررسی دسترسی ادمین
        if not user_role_manager.is_admin_or_higher(user_id):
            await query.edit_message_text(
                "❌ شما دسترسی به این بخش را ندارید.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
                ]])
            )
            return
        
        admin_action = data.replace("admin_", "")
        
        # admin_add_doctor حالا توسط ConversationHandler در bot.py handle می‌شود
        if admin_action == "manage_doctors":
            await CallbackHandlers._handle_admin_manage_doctors(query, user_id)
        elif admin_action == "manage_users":
            await CallbackHandlers._handle_admin_manage_users(query, user_id)
        elif admin_action == "system_settings":
            await CallbackHandlers._handle_admin_system_settings(query, user_id)
        elif admin_action == "view_logs":
            await CallbackHandlers._handle_admin_view_logs(query, user_id)
        elif admin_action == "access_control":
            await CallbackHandlers._handle_admin_access_control(query, user_id)
        elif admin_action == "dashboard":
            await CallbackHandlers._handle_admin_dashboard(query, user_id)
        else:
            await query.edit_message_text(
                f"🔧 **{admin_action}**\n\nاین قسمت در حال توسعه است.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
                ]])
            )
    
    @staticmethod
    async def _handle_admin_manage_doctors(query, user_id):
        """مدیریت دکترها توسط ادمین"""
        try:
            with db_session() as session:
                doctors = session.query(Doctor).all()
                
                if not doctors:
                    await query.edit_message_text(
                        "❌ هیچ دکتری در سیستم موجود نیست.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("➕ افزودن دکتر", callback_data="admin_add_doctor"),
                            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
                        ]])
                    )
                    return
                
                text = f"""
👨‍⚕️ **مدیریت دکترها**

📊 **آمار:**
• کل دکترها: {len(doctors)}
• فعال: {len([d for d in doctors if d.is_active])}
• غیرفعال: {len([d for d in doctors if not d.is_active])}

🔧 **عملیات:**
                """
                
                keyboard = [
                    [InlineKeyboardButton("➕ افزودن دکتر", callback_data="admin_add_doctor")],
                    [InlineKeyboardButton("📋 لیست دکترها", callback_data="admin_list_doctors")],
                    [InlineKeyboardButton("🔄 فعال/غیرفعال", callback_data="admin_toggle_doctors")],
                    [InlineKeyboardButton("🗑️ حذف دکتر", callback_data="admin_delete_doctor")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در مدیریت دکترها: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_admin_manage_users(query, user_id):
        """مدیریت کاربران توسط ادمین"""
        await query.edit_message_text(
            "👥 **مدیریت کاربران**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )
    
    @staticmethod
    async def _handle_admin_system_settings(query, user_id):
        """تنظیمات سیستم توسط ادمین"""
        await query.edit_message_text(
            "⚙️ **تنظیمات سیستم**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )
    
    @staticmethod
    async def _handle_admin_view_logs(query, user_id):
        """مشاهده لاگ‌ها توسط ادمین"""
        await query.edit_message_text(
            "📋 **مشاهده لاگ‌ها**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )
    
    @staticmethod
    async def _handle_admin_access_control(query, user_id):
        """مدیریت دسترسی توسط ادمین"""
        await query.edit_message_text(
            "🔒 **مدیریت دسترسی**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )
    
    @staticmethod
    async def _handle_admin_dashboard(query, user_id):
        """داشبورد ادمین"""
        try:
            with db_session() as session:
                # آمار کلی
                total_users = session.query(User).count()
                active_users = session.query(User).filter(User.is_active == True).count()
                total_doctors = session.query(Doctor).count()
                active_doctors = session.query(Doctor).filter(Doctor.is_active == True).count()
                total_subscriptions = session.query(Subscription).filter(Subscription.is_active == True).count()
                
                today = datetime.now().date()
                appointments_today = session.query(AppointmentLog).filter(
                    AppointmentLog.created_at >= today
                ).count()
                
                dashboard_text = f"""
📊 **داشبورد ادمین**

👥 **کاربران:**
• کل: {total_users}
• فعال: {active_users}

👨‍⚕️ **دکترها:**
• کل: {total_doctors}
• فعال: {active_doctors}

📝 **اشتراک‌ها:**
• فعال: {total_subscriptions}

🎯 **نوبت‌های امروز:**
• پیدا شده: {appointments_today}

⏰ **آخرین بروزرسانی:** {datetime.now().strftime('%Y/%m/%d %H:%M')}
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 بروزرسانی", callback_data="admin_dashboard")],
                    [InlineKeyboardButton("📊 آمار تفصیلی", callback_data="admin_detailed_stats")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    dashboard_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در داشبورد ادمین: {e}")
            await query.edit_message_text(MessageFormatter.error_message())

    # Placeholder handlers for other admin callbacks
    @staticmethod
    async def _handle_super_admin_callbacks(query, data, user_id):
        """مدیریت callback های سوپر ادمین"""
        from src.telegram_bot.user_roles import user_role_manager, UserRole
        
        if user_role_manager.get_user_role(user_id) != UserRole.SUPER_ADMIN:
            await query.edit_message_text(
                "❌ شما دسترسی به این بخش را ندارید.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
                ]])
            )
            return
        
        action = data.replace("super_", "")
        await query.edit_message_text(
            f"⭐ **سوپر ادمین - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_advanced_settings_callbacks(query, data, user_id):
        """مدیریت callback های تنظیمات پیشرفته"""
        action = data.replace("advanced_", "")
        await query.edit_message_text(
            f"🛠️ **تنظیمات پیشرفته - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_system_callbacks(query, data, user_id):
        """مدیریت callback های سیستم"""
        action = data.replace("system_", "")
        await query.edit_message_text(
            f"🔧 **سیستم - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_detailed_callbacks(query, data, user_id):
        """مدیریت callback های تفصیلی"""
        action = data.replace("detailed_", "")
        await query.edit_message_text(
            f"📊 **تفصیلی - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_stats_callbacks(query, data, user_id):
        """مدیریت callback های آمار"""
        action = data.replace("stats_", "")
        await query.edit_message_text(
            f"📈 **آمار - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_log_callbacks(query, data, user_id):
        """مدیریت callback های لاگ"""
        action = data.replace("log_", "")
        await query.edit_message_text(
            f"📝 **لاگ - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_backup_callbacks(query, data, user_id):
        """مدیریت callback های پشتیبان‌گیری"""
        action = data.replace("backup_", "")
        await query.edit_message_text(
            f"💾 **پشتیبان‌گیری - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_database_callbacks(query, data, user_id):
        """مدیریت callback های دیتابیس"""
        action = data.replace("database_", "")
        await query.edit_message_text(
            f"🗄️ **دیتابیس - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_monitoring_callbacks(query, data, user_id):
        """مدیریت callback های مانیتورینگ"""
        action = data.replace("monitoring_", "")
        await query.edit_message_text(
            f"📊 **مانیتورینگ - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_list_callbacks(query, data, user_id):
        """مدیریت callback های لیست"""
        action = data.replace("list_", "")
        await query.edit_message_text(
            f"📋 **لیست - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_search_callbacks(query, data, user_id):
        """مدیریت callback های جستجو"""
        action = data.replace("search_", "")
        await query.edit_message_text(
            f"🔍 **جستجو - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_manage_callbacks(query, data, user_id):
        """مدیریت callback های مدیریت"""
        action = data.replace("manage_", "")
        await query.edit_message_text(
            f"🔧 **مدیریت - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_blocked_callbacks(query, data, user_id):
        """مدیریت callback های مسدود شده"""
        action = data.replace("blocked_", "")
        await query.edit_message_text(
            f"🚫 **مسدود شده - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_user_callbacks(query, data, user_id):
        """مدیریت callback های کاربر"""
        action = data.replace("user_", "")
        await query.edit_message_text(
            f"👤 **کاربر - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )

    @staticmethod
    async def _handle_full_callbacks(query, data, user_id):
        """مدیریت callback های کامل"""
        action = data.replace("full_", "")
        await query.edit_message_text(
            f"📋 **کامل - {action}**\n\n🔧 این قسمت در حال توسعه است.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
            ]])
        )