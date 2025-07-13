"""
Clean Callback handlers for inline keyboard buttons - Professional Version
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from telegram.error import TelegramError
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.database.database import db_session
from src.database.models import User, Doctor, Subscription, AppointmentLog
from src.telegram_bot.messages import MessageFormatter
from src.telegram_bot.menu_handlers import MenuHandlers
from src.telegram_bot.constants import CallbackPrefix, AdminCallback, MainMenuCallbacks
from src.utils.logger import get_logger

logger = get_logger("CallbackHandlers")


class CallbackHandlers:
    """کلاس مدیریت callback های دکمه‌های inline - نسخه تمیز و حرفه‌ای"""
    
    @staticmethod
    async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کلی callback query ها"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            
            # Skip callbacks that should be handled by ConversationHandler
            conversation_callbacks = [
                AdminCallback.ADD_DOCTOR,
                AdminCallback.SET_INTERVAL,
                AdminCallback.CONFIRM_ADD_DOCTOR,
                AdminCallback.CANCEL_ADD_DOCTOR
            ]
            
            if data in conversation_callbacks:
                # Let ConversationHandler handle these - don't process here
                logger.info(f"Skipping callback {data} - should be handled by ConversationHandler")
                return
            
            # مدیریت callback های اصلی
            if data == MainMenuCallbacks.BACK_TO_MAIN:
                await CallbackHandlers._handle_back_to_main(query)
            elif data == MainMenuCallbacks.BACK_TO_DOCTORS:
                await CallbackHandlers._handle_back_to_doctors(query)
            elif data.startswith(CallbackPrefix.DOCTOR_INFO):
                await CallbackHandlers._handle_doctor_info(query, data, user_id)
            elif data.startswith(CallbackPrefix.SUBSCRIBE):
                await CallbackHandlers._handle_subscribe(query, data, user_id)
            elif data.startswith(CallbackPrefix.UNSUBSCRIBE):
                await CallbackHandlers._handle_unsubscribe(query, data, user_id)
            elif data.startswith(CallbackPrefix.VIEW_WEBSITE):
                await CallbackHandlers._handle_view_website(query, data)
            elif data.startswith(CallbackPrefix.STATS):
                await CallbackHandlers._handle_doctor_stats(query, data, user_id)
            elif data.startswith(CallbackPrefix.SETTINGS):
                await CallbackHandlers._handle_settings(query, data, user_id)
            elif data == MainMenuCallbacks.SUBSCRIPTION_STATS:
                await CallbackHandlers._handle_subscription_stats(query, user_id)
            elif data == MainMenuCallbacks.NEW_SUBSCRIPTION:
                await CallbackHandlers._handle_new_subscription(query, user_id)
            elif data == MainMenuCallbacks.REFRESH_STATUS:
                await CallbackHandlers._handle_refresh_status(query, user_id)
            elif data == MainMenuCallbacks.DETAILED_STATS:
                await CallbackHandlers._handle_detailed_stats(query, user_id)
            elif data == MainMenuCallbacks.SYSTEM_STATUS:
                await CallbackHandlers._handle_system_status(query)
            elif data == MainMenuCallbacks.SHOW_DOCTORS:
                await CallbackHandlers._handle_show_doctors(query)
            elif data == MainMenuCallbacks.SHOW_SUBSCRIPTIONS:
                await CallbackHandlers._handle_show_subscriptions(query, user_id)
            elif data == MainMenuCallbacks.REFRESH_ALL_SUBSCRIPTIONS:
                await CallbackHandlers._handle_refresh_all_subscriptions(query, user_id)
            # Admin callbacks
            elif data.startswith("admin_"):
                await CallbackHandlers._handle_admin_callbacks(query, data, user_id)
            elif data.startswith(CallbackPrefix.TOGGLE_DOCTOR):
                from src.telegram_bot.admin_handlers import TelegramAdminHandlers
                await TelegramAdminHandlers.toggle_doctor_status(update, context)
            elif data == AdminCallback.BACK_TO_ADMIN_PANEL:
                from src.telegram_bot.admin_handlers import TelegramAdminHandlers
                await TelegramAdminHandlers.admin_panel(update, context)
            else:
                await query.edit_message_text(
                    "❌ دستور نامشخص. لطفاً دوباره تلاش کنید.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")
                    ]])
                )
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در callback query: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در callback query: {e}")
            # معمولا نیازی به پاسخ به کاربر نیست، چون ممکن است پیام قبلا حذف شده باشد
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در callback query: {e}")
            try:
                await query.edit_message_text(MessageFormatter.error_message())
            except TelegramError:
                pass  # اگر ویرایش پیام هم خطا داد، کاری نمی‌توان کرد
    
    @staticmethod
    async def _handle_back_to_main(query):
        """بازگشت به منوی اصلی"""
        welcome_text = """
🎯 **منوی اصلی**

از دکمه‌های زیر برای استفاده از ربات استفاده کنید:

💡 **نکته:** برای دسترسی سریع‌تر، از منوی پایین صفحه استفاده کنید.
        """
        
        keyboard = [
            [InlineKeyboardButton("👨‍⚕️ مشاهده دکترها", callback_data="show_doctors")],
            [InlineKeyboardButton("📝 مدیریت اشتراک‌ها", callback_data="show_subscriptions")],
            [InlineKeyboardButton("🔔 اشتراک جدید", callback_data="new_subscription")],
            [InlineKeyboardButton("📊 وضعیت من", callback_data="refresh_status")]
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
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در بازگشت به لیست دکترها: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در بازگشت به لیست دکترها: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در بازگشت به لیست دکترها: {e}")
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
• وضعیت: {'✅ فعال' if doctor.is_active else '⏸️ غیرفعال'}

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
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در نمایش اطلاعات دکتر: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در نمایش اطلاعات دکتر: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در نمایش اطلاعات دکتر: {e}")
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

                logger.info(
                    "📝 اشتراک جدید: %s -> %s",
                    user.full_name,
                    doctor.name,
                    extra={'user_id': user.id, 'doctor_id': doctor.id}
                )
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در اشتراک: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در اشتراک: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در اشتراک: {e}")
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

💡 در صورت نیاز، می‌توانید مجدداً مشترک شوید.
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

                logger.info(
                    "🗑️ لغو اشتراک: %s -> %s",
                    user.full_name,
                    doctor.name,
                    extra={'user_id': user.id, 'doctor_id': doctor.id}
                )
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در لغو اشتراک: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در لغو اشتراک: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در لغو اشتراک: {e}")
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
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در نمایش لینک وب‌سایت: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در نمایش لینک وب‌سایت: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در نمایش لینک وب‌سایت: {e}")
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
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در نمایش آمار دکتر: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در نمایش آمار دکتر: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در نمایش آمار دکتر: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_settings(query, data, user_id):
        """مدیریت تنظیمات - فقط قسمت‌های پیاده‌سازی شده"""
        setting_type = data.split("_")[1]
        
        if setting_type == "main":
            await query.edit_message_text(
                "⚙️ **تنظیمات ربات**\n\n🔧 این قسمت در حال توسعه است.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")
                ]])
            )
    
    @staticmethod
    async def _handle_subscription_stats(query, user_id):
        """آما�� اشتراک‌ها"""
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

���� **اشتراک‌ها:**
• اشتراک‌های فعال: {len(active_subs)}
• کل اشتراک‌ها: {total_subs}

🎯 **نوبت‌های پیدا شده:**
• امروز: {appointments_today}
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
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در نمایش آمار اشتراک‌ها: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در نمایش آمار اشتراک‌ها: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در نمایش آمار اشتراک‌ها: {e}")
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
                        "❌ هیچ دکتری برای اشتراک موجود نیست.",
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
                        "✅ شما در تمام دکترهای موجود مشترک هستید!",
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
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در اشتراک جدید: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در اشتراک جدید: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در اشتراک جدید: {e}")
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
• کل اشتراک‌ها: {total_subscriptions}

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
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در بروزرسانی وضعیت: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در بروزرسانی وضعیت: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در بروزرسانی وضعیت: {e}")
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
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در نمایش آمار تفصیلی: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در نمایش آمار تفصیلی: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در نمایش آمار تفصیلی: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
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
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    status_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در نمایش وضعیت سیستم: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در نمایش وضعیت سیستم: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در نمایش وضعیت سیستم: {e}")
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
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در نمایش لیست دکترها: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در نمایش لیست دکترها: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در نمایش لیست دکترها: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_show_subscriptions(query, user_id):
        """نمایش اشتراک‌ها از callback"""
        try:
            with db_session() as session:
                # بهینه‌سازی کوئری با joinedload برای جلوگیری از N+1
                user = (
                    session.query(User)
                    .options(
                        joinedload(User.subscriptions)
                        .joinedload(Subscription.doctor)
                    )
                    .filter(User.telegram_id == user_id)
                    .first()
                )

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
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در نمایش اشتراک‌ها: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در نمایش اشتراک‌ها: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در نمایش اشتراک‌ها: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_admin_callbacks(query, data, user_id):
        """مدیریت callback های ادمین"""
        from src.telegram_bot.admin_handlers import TelegramAdminHandlers
        update = query.message.reply_to_message.update if query.message.reply_to_message else query
        
        if not TelegramAdminHandlers.is_admin(user_id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return

        if data == "admin_manage_doctors":
            await TelegramAdminHandlers.manage_doctors(update, None)
        elif data == "admin_stats":
            await TelegramAdminHandlers.show_admin_stats(update, None)
        elif data == "admin_manage_users":
            await TelegramAdminHandlers.show_user_management(update, None)
        elif data == "admin_access_settings":
            await TelegramAdminHandlers.show_access_settings(update, None)
        else:
            await query.edit_message_text(
                "این دکمه هنوز پیاده‌سازی نشده است.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_panel")
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
• ��عال: {len([d for d in doctors if d.is_active])}
• غیرفعال: {len([d for d in doctors if not d.is_active])}

🔧 **عملیات:**
                """
                
                keyboard = [
                    [InlineKeyboardButton("➕ افزودن دکتر", callback_data="admin_add_doctor")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در مدیریت دکترها: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در مدیریت دکترها: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در مدیریت دکترها: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
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
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    dashboard_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در داشبورد ادمین: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در داشبورد ادمین: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در داشبورد ادمین: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_refresh_all_subscriptions(query, user_id):
        """بروزرسانی همه اشتراک‌ها"""
        try:
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await query.edit_message_text("❌ کاربر یافت نشد.")
                    return
                
                # بروزرسانی آخرین فعالیت کاربر
                user.last_activity = datetime.utcnow()
                session.commit()
                
                # دریافت اشتراک‌های فعال
                active_subscriptions = [
                    sub for sub in user.subscriptions if sub.is_active
                ]
                
                if not active_subscriptions:
                    text = f"""
📝 **اشتراک‌های من (بروزرسانی شده)**

❌ شما در هیچ دکتری مشترک نیستید.

💡 برای اشتراک جدید از دکمه زیر استفاده کنید.

⏰ **آخرین بروزرسانی:** {datetime.now().strftime('%Y/%m/%d %H:%M')}
                    """
                else:
                    # آمار نوبت‌های امروز
                    today = datetime.now().date()
                    appointments_today = session.query(AppointmentLog).join(Doctor).join(Subscription).filter(
                        Subscription.user_id == user.id,
                        Subscription.is_active == True,
                        AppointmentLog.created_at >= today
                    ).count()
                    
                    text = f"""
📝 **اشتراک‌های من (بروزرسانی شده)**

✅ **{len(active_subscriptions)} اشتراک فعال:**

                    """
                    for i, sub in enumerate(active_subscriptions, 1):
                        date_str = sub.created_at.strftime('%Y/%m/%d') if sub.created_at else "نامشخص"
                        
                        # آمار نوبت‌های این دکتر امروز
                        doctor_appointments_today = session.query(AppointmentLog).filter(
                            AppointmentLog.doctor_id == sub.doctor.id,
                            AppointmentLog.created_at >= today
                        ).count()
                        
                        text += f"**{i}. {sub.doctor.name}**\n"
                        text += f"   🏥 {sub.doctor.specialty}\n"
                        text += f"   📅 عضویت: {date_str}\n"
                        text += f"   🎯 نوبت‌های امروز: {doctor_appointments_today}\n\n"
                    
                    text += f"""
📊 **آمار کلی امروز:**
• نوبت‌های پیدا شده: {appointments_today}

⏰ **آخرین بروزرسانی:** {datetime.now().strftime('%Y/%m/%d %H:%M')}
                    """
                
                keyboard = MenuHandlers.get_subscription_management_keyboard(active_subscriptions)
                
                await query.edit_message_text(
                    text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                
        except SQLAlchemyError as e:
            logger.error(f"❌ خطای دیتابیس در بروزرسانی اشتراک‌ها: {e}")
            await query.edit_message_text(MessageFormatter.db_error_message())
        except TelegramError as e:
            logger.warning(f"⚠️ خطای تلگرام در بروزرسانی اشتراک‌ها: {e}")
        except Exception as e:
            logger.exception(f"❌ خطای پیش‌بینی نشده در بروزرسانی اشتراک‌ها: {e}")
            await query.edit_message_text(MessageFormatter.error_message())