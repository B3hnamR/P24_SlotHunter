"""
Handler های ربات تلگرام
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from typing import List

from src.database.database import db_session
from src.database.models import User, Doctor, Subscription
from src.telegram_bot.messages import MessageFormatter
from src.utils.logger import get_logger

logger = get_logger("TelegramHandlers")


class TelegramHandlers:
    """کلاس handler های تلگرام"""
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /start"""
        try:
            user = update.effective_user
            
            # ثبت/به‌روزرسانی کاربر در دیتابیس
            with db_session() as session:
                db_user = session.query(User).filter(User.telegram_id == user.id).first()
                
                if not db_user:
                    # کاربر جدید
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
                
                session.commit()
            
            # ارسال پیام خوش‌آمدگویی
            welcome_text = MessageFormatter.welcome_message(user.first_name)
            await update.message.reply_text(welcome_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ خطا در دستور start: {e}")
            await update.message.reply_text(MessageFormatter.error_message())
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /help"""
        try:
            help_text = MessageFormatter.help_message()
            await update.message.reply_text(help_text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"❌ خطا در دستور help: {e}")
            await update.message.reply_text(MessageFormatter.error_message())
    
    @staticmethod
    async def doctors_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /doctors"""
        try:
            with db_session() as session:
                doctors = session.query(Doctor).filter(Doctor.is_active == True).all()
                
                if not doctors:
                    await update.message.reply_text("❌ هیچ دکتری در سیستم ثبت نشده است.")
                    return
                
                # ایجاد keyboard
                keyboard = []
                for doctor in doctors:
                    keyboard.append([
                        InlineKeyboardButton(
                            f"👨‍⚕️ {doctor.name}",
                            callback_data=f"doctor_info_{doctor.id}"
                        )
                    ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                doctors_text = MessageFormatter.doctor_list_message(doctors)
                
                await update.message.reply_text(
                    doctors_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در دستور doctors: {e}")
            await update.message.reply_text(MessageFormatter.error_message())
    
    @staticmethod
    async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /subscribe"""
        try:
            user_id = update.effective_user.id
            
            with db_session() as session:
                # دریافت دکترهای فعال
                doctors = session.query(Doctor).filter(Doctor.is_active == True).all()
                
                if not doctors:
                    await update.message.reply_text("❌ هیچ دکتری برای اشتراک موجود نیست.")
                    return
                
                # دریافت اشتراک‌های فعلی کاربر
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await update.message.reply_text("❌ ابتدا دستور /start را اجرا کنید.")
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
                    await update.message.reply_text(
                        "✅ شما در تمام دکترهای موجود مشترک هستید.\n\n"
                        "📊 برای مشاهده اشتراک‌ها از دستور /status استفاده کنید."
                    )
                    return
                
                # ایجاد keyboard
                keyboard = []
                for doctor in available_doctors:
                    keyboard.append([
                        InlineKeyboardButton(
                            f"📝 {doctor.name}",
                            callback_data=f"subscribe_{doctor.id}"
                        )
                    ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "📝 **انتخاب دکتر برای اشتراک:**\n\n"
                    "روی نام دکتر مورد نظر کلیک کنید:",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در دستور subscribe: {e}")
            await update.message.reply_text(MessageFormatter.error_message())
    
    @staticmethod
    async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /unsubscribe"""
        try:
            user_id = update.effective_user.id
            
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await update.message.reply_text("❌ ابتدا دستور /start را اجرا کنید.")
                    return
                
                # دریافت اشتراک‌های فعال
                active_subscriptions = [
                    sub for sub in user.subscriptions if sub.is_active
                ]
                
                if not active_subscriptions:
                    await update.message.reply_text(
                        "❌ شما در هیچ دکتری ��شترک نیستید.\n\n"
                        "💡 برای اشتراک از دستور /subscribe استفاده کنید."
                    )
                    return
                
                # ایجاد keyboard
                keyboard = []
                for subscription in active_subscriptions:
                    keyboard.append([
                        InlineKeyboardButton(
                            f"🗑️ {subscription.doctor.name}",
                            callback_data=f"unsubscribe_{subscription.doctor.id}"
                        )
                    ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "🗑️ **انتخاب دکتر برای لغو اشتراک:**\n\n"
                    "روی نام دکتر مورد نظر کلیک کنید:",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در دستور unsubscribe: {e}")
            await update.message.reply_text(MessageFormatter.error_message())
    
    @staticmethod
    async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور /status"""
        try:
            user_id = update.effective_user.id
            
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if not user:
                    await update.message.reply_text("❌ ابتدا دستور /start را اجرا کنید.")
                    return
                
                # دریافت اشتراک‌های فعال
                active_subscriptions = [
                    (sub.doctor, sub.created_at) 
                    for sub in user.subscriptions if sub.is_active
                ]
                
                status_text = MessageFormatter.subscription_status_message(active_subscriptions)
                await update.message.reply_text(status_text, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"❌ خطا در دستور status: {e}")
            await update.message.reply_text(MessageFormatter.error_message())
    
    @staticmethod
    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت callback های دکم��‌ها"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            
            if data.startswith("doctor_info_"):
                await TelegramHandlers._handle_doctor_info(query, data)
            elif data.startswith("subscribe_"):
                await TelegramHandlers._handle_subscribe(query, data, user_id)
            elif data.startswith("unsubscribe_"):
                await TelegramHandlers._handle_unsubscribe(query, data, user_id)
            
        except Exception as e:
            logger.error(f"❌ خطا در callback: {e}")
            await query.edit_message_text(MessageFormatter.error_message())
    
    @staticmethod
    async def _handle_doctor_info(query, data):
        """نمایش اطلاعات دکتر"""
        doctor_id = int(data.split("_")[2])
        
        with db_session() as session:
            doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
            if not doctor:
                await query.edit_message_text("❌ دکتر یافت نشد.")
                return
            
            info_text = MessageFormatter.doctor_info_message(doctor)
            
            # دکمه اشتراک
            keyboard = [[
                InlineKeyboardButton(
                    "📝 اشتراک در این دکتر",
                    callback_data=f"subscribe_{doctor.id}"
                )
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                info_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    @staticmethod
    async def _handle_subscribe(query, data, user_id):
        """مدیریت اشتراک"""
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
                        parse_mode='Markdown'
                    )
                    return
                else:
                    # فعال‌سازی مجدد
                    existing_sub.is_active = True
            else:
                # اشتراک جدید
                new_subscription = Subscription(
                    user_id=user.id,
                    doctor_id=doctor.id
                )
                session.add(new_subscription)
            
            session.commit()
            
            success_text = MessageFormatter.subscription_success_message(doctor)
            await query.edit_message_text(success_text, parse_mode='Markdown')
            
            logger.info(f"📝 اشتراک جدید: {user.full_name} -> {doctor.name}")
    
    @staticmethod
    async def _handle_unsubscribe(query, data, user_id):
        """مدیریت لغو اشتراک"""
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
                    parse_mode='Markdown'
                )
                return
            
            # لغو اشتراک
            subscription.is_active = False
            session.commit()
            
            success_text = MessageFormatter.unsubscription_success_message(doctor)
            await query.edit_message_text(success_text, parse_mode='Markdown')
            
            logger.info(f"🗑️ لغو اشتراک: {user.full_name} -> {doctor.name}")