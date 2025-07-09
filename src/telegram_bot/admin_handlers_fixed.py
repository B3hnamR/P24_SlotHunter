"""
Handler های ادمین ربات تلگرام - Fixed Version
"""
import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy.orm import Session
from typing import List

from src.database.database import db_session
from src.database.models import User, Doctor, Subscription
from src.telegram_bot.messages import MessageFormatter
from src.utils.logger import get_logger
from src.utils.config import Config

logger = get_logger("TelegramAdminHandlers")

# States برای ConversationHandler
ADD_DOCTOR_LINK, ADD_DOCTOR_CONFIRM, SET_CHECK_INTERVAL = range(3)


class TelegramAdminHandlers:
    """کلاس handler های ادمین تلگرام"""
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """بررسی دسترسی ادمین"""
        try:
            config = Config()
            admin_chat_id = config.admin_chat_id
            logger.info(f"Checking admin: user_id={user_id}, admin_chat_id={admin_chat_id}")
            
            # بررسی ادمین اصلی
            if user_id == admin_chat_id:
                return True
            
            # بررسی ادمین‌های اضافی از دیتابیس
            try:
                with db_session() as session:
                    user = session.query(User).filter(
                        User.telegram_id == user_id,
                        User.is_admin == True,
                        User.is_active == True
                    ).first()
                    return user is not None
            except Exception as e:
                logger.error(f"خطا در بررسی ادمین از دیتابیس: {e}")
                return False
        except Exception as e:
            logger.error(f"خطا در بررسی دسترسی ادمین: {e}")
            return False
    
    @staticmethod
    async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پنل مدیریت ادمین"""
        try:
            user_id = update.effective_user.id
            logger.info(f"Admin panel request from user: {user_id}")
            
            if not TelegramAdminHandlers.is_admin(user_id):
                await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
                return
            
            keyboard = [
                [InlineKeyboardButton("➕ افزودن دکتر", callback_data="admin_add_doctor")],
                [InlineKeyboardButton("🔧 مدیریت دکترها", callback_data="admin_manage_doctors")],
                [InlineKeyboardButton("⏱️ تنظیم زمان بررسی", callback_data="admin_set_interval")],
                [InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_manage_users")],
                [InlineKeyboardButton("📊 آمار سیستم", callback_data="admin_stats")],
                [InlineKeyboardButton("🔒 تنظیمات دسترسی", callback_data="admin_access_settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            admin_text = "🔧 پنل مدیریت P24_SlotHunter\n\nانتخاب کنید:"
            
            await update.message.reply_text(admin_text, reply_markup=reply_markup)
            logger.info("Admin panel sent successfully")
            
        except Exception as e:
            logger.error(f"خطا در نمایش پنل ادمین: {e}")
            await update.message.reply_text("❌ خطا در بارگذاری پنل مدیریت.")
    
    @staticmethod
    async def start_add_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شروع فرآیند افزودن دکتر"""
        query = update.callback_query
        await query.answer()
        
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return ConversationHandler.END
        
        await query.edit_message_text(
            "🔗 افزودن دکتر جدید\n\n"
            "لینک صفحه دکتر در پذیرش۲۴ را ارسال کنید:\n"
            "مثال: https://www.paziresh24.com/dr/دکتر-نام-خانوادگی-0/\n\n"
            "برای لغو: /cancel"
        )
        
        return ADD_DOCTOR_LINK
    
    @staticmethod
    async def process_doctor_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش لینک دکتر"""
        link = update.message.text.strip()
        
        # بررسی فرمت لینک
        if not re.match(r'https://www\.paziresh24\.com/dr/.+', link):
            await update.message.reply_text(
                "❌ لینک نامعتبر است.\n\n"
                "لطفاً لینک صحیح صفحه دکتر را ارسال کنید:\n"
                "https://www.paziresh24.com/dr/دکتر-نام-خانوادگی-0/"
            )
            return ADD_DOCTOR_LINK
        
        # استخراج slug دکتر
        slug = link.split('/dr/')[1].rstrip('/')
        
        # دریافت اطلاعات دکتر از API
        try:
            doctor_info = await TelegramAdminHandlers._fetch_doctor_info(slug)
            if not doctor_info:
                await update.message.reply_text(
                    "❌ نتوانستم اطلاعات دکتر را دریافت کنم.\n\n"
                    "لطفاً لینک صحیح ارسال کنید یا دوباره تلاش کنید."
                )
                return ADD_DOCTOR_LINK
            
            # ذخیره اطلاعات در context
            context.user_data['doctor_info'] = doctor_info
            
            # نمایش اطلاعات برای تأیید
            confirm_text = f"""✅ اطلاعات دکتر یافت شد:

👨‍⚕️ نام: {doctor_info['name']}
🏥 تخصص: {doctor_info['specialty']}
🏢 مرکز: {doctor_info['center_name']}
📍 آدرس: {doctor_info['center_address']}
📞 تلفن: {doctor_info['center_phone']}

آیا می‌خواهید این دکتر را اضافه کنید؟"""
            
            keyboard = [
                [InlineKeyboardButton("✅ تأیید", callback_data="confirm_add_doctor")],
                [InlineKeyboardButton("❌ لغو", callback_data="cancel_add_doctor")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(confirm_text, reply_markup=reply_markup)
            
            return ADD_DOCTOR_CONFIRM
            
        except Exception as e:
            logger.error(f"خطا در دریافت اطلاعات دکتر: {e}")
            await update.message.reply_text(
                "❌ خطا در دریافت اطلاعات دکتر.\n\n"
                "لطفاً دوباره تلاش کنید."
            )
            return ADD_DOCTOR_LINK
    
    @staticmethod
    async def confirm_add_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأیید افزودن دکتر"""
        query = update.callback_query
        await query.answer()
        
        doctor_info = context.user_data.get('doctor_info')
        if not doctor_info:
            await query.edit_message_text("❌ خطا در دریافت اطلاعات دکتر.")
            return ConversationHandler.END
        
        try:
            with db_session() as session:
                # بررسی وجود دکتر
                existing = session.query(Doctor).filter(Doctor.slug == doctor_info['slug']).first()
                
                if existing:
                    await query.edit_message_text(
                        f"⚠️ دکتر {doctor_info['name']} قبلاً در سیستم موجود است."
                    )
                    return ConversationHandler.END
                
                # افزودن دکتر جدید
                new_doctor = Doctor(
                    name=doctor_info['name'],
                    slug=doctor_info['slug'],
                    center_id=doctor_info['center_id'],
                    service_id=doctor_info['service_id'],
                    user_center_id=doctor_info['user_center_id'],
                    terminal_id=doctor_info['terminal_id'],
                    specialty=doctor_info['specialty'],
                    center_name=doctor_info['center_name'],
                    center_address=doctor_info['center_address'],
                    center_phone=doctor_info['center_phone'],
                    is_active=True
                )
                
                session.add(new_doctor)
                session.commit()
                
                await query.edit_message_text(
                    f"✅ دکتر {doctor_info['name']} با موفقیت اضافه شد!\n\n"
                    f"🔔 از این پس نوبت‌های این دکتر نیز بررسی می‌شود."
                )
                
                logger.info(f"دکتر جدید توسط ادمین اضافه شد: {doctor_info['name']}")
                
        except Exception as e:
            logger.error(f"خطا در افزودن دکتر: {e}")
            await query.edit_message_text("❌ خطا در افزودن دکتر. لطفاً دوباره تلاش کنید.")
        
        return ConversationHandler.END
    
    @staticmethod
    async def manage_doctors(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت دکترها"""
        query = update.callback_query
        await query.answer()
        
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return
        
        try:
            with db_session() as session:
                doctors = session.query(Doctor).all()
                
                if not doctors:
                    await query.edit_message_text("❌ هیچ دکتری در سیستم موجود نیست.")
                    return
                
                keyboard = []
                for doctor in doctors:
                    status_icon = "✅" if doctor.is_active else "⏸️"
                    action = "disable" if doctor.is_active else "enable"
                    
                    keyboard.append([
                        InlineKeyboardButton(
                            f"{status_icon} {doctor.name}",
                            callback_data=f"toggle_doctor_{doctor.id}_{action}"
                        )
                    ])
                
                keyboard.append([
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_panel")
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    "🔧 مدیریت دکترها\n\n"
                    "برای خاموش/روشن کردن نظارت، روی نام دکتر کلیک کنید:",
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"خطا در مدیریت دکترها: {e}")
            await query.edit_message_text("❌ خطا در بارگذاری لیست دکترها.")
    
    @staticmethod
    async def toggle_doctor_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تغییر وضعیت دکتر"""
        query = update.callback_query
        await query.answer()
        
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return
        
        try:
            # استخراج اطلاعات از callback_data
            parts = query.data.split('_')
            doctor_id = int(parts[2])
            action = parts[3]  # enable یا disable
            
            with db_session() as session:
                doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
                
                if not doctor:
                    await query.edit_message_text("❌ دکتر یافت نشد.")
                    return
                
                # تغییر وضعیت
                doctor.is_active = (action == "enable")
                session.commit()
                
                status_text = "فعال" if doctor.is_active else "غیرفعال"
                await query.edit_message_text(
                    f"✅ وضعیت دکتر {doctor.name} به {status_text} تغییر کرد.\n\n"
                    f"🔄 برای بازگشت به لیست: /admin"
                )
                
                logger.info(f"وضعیت دکتر {doctor.name} تغییر کرد: {status_text}")
                
        except Exception as e:
            logger.error(f"خطا در تغییر وضعیت دکتر: {e}")
            await query.edit_message_text("❌ خطا در تغییر وضعیت دکتر.")
    
    @staticmethod
    async def set_check_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تنظیم زمان بررسی"""
        query = update.callback_query
        await query.answer()
        
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return
        
        await query.edit_message_text(
            "⏱️ تنظیم زمان بررسی\n\n"
            "زمان بررسی جدید را به ثانیه وارد کنید (حداقل 1 ثانیه):\n\n"
            "مثال: 30 برای 30 ثانیه\n\n"
            "برای لغو: /cancel"
        )
        
        return SET_CHECK_INTERVAL
    
    @staticmethod
    async def process_check_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش زمان بررسی جدید"""
        try:
            interval = int(update.message.text.strip())
            
            if interval < 1:
                await update.message.reply_text(
                    "❌ زمان بررسی باید حداقل 1 ثانیه باشد.\n\n"
                    "لطفاً عدد معتبر وارد کنید:"
                )
                return SET_CHECK_INTERVAL
            
            # به‌روزرسانی فایل .env
            env_path = ".env"
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # جایگزینی CHECK_INTERVAL
            import re
            content = re.sub(r'CHECK_INTERVAL=\d+', f'CHECK_INTERVAL={interval}', content)
            
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            await update.message.reply_text(
                f"✅ زمان بررسی به {interval} ثانیه تغییر کرد.\n\n"
                f"⚠️ برای اعمال تغییرات، سیستم باید restart شود.\n\n"
                f"🔄 برای بازگشت: /admin"
            )
            
            logger.info(f"زمان بررسی توسط ادمین تغییر کرد: {interval} ثانیه")
            
        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً عدد معتبر وارد کنید.\n\n"
                "مثال: 30"
            )
            return SET_CHECK_INTERVAL
        except Exception as e:
            logger.error(f"خطا در تنظیم زمان بررسی: {e}")
            await update.message.reply_text("❌ خطا در تنظیم زمان بررسی.")
        
        return ConversationHandler.END
    
    @staticmethod
    async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لغو مکالمه"""
        await update.message.reply_text(
            "❌ عملیات لغو شد.\n\n"
            "🔄 برای بازگشت: /admin"
        )
        return ConversationHandler.END
    
    @staticmethod
    async def _fetch_doctor_info(slug: str) -> dict:
        """دریافت اطلاعات دکتر از API پذیرش۲۴"""
        # این تابع باید اطلاعات دکتر را از API دریافت کند
        # فعلاً یک نمونه ساده برمی‌گرداند
        
        # TODO: پیاده‌سازی واقعی API call
        return {
            'name': f'دکتر {slug.replace("-", " ")}',
            'slug': slug,
            'center_id': 'sample-center-id',
            'service_id': 'sample-service-id',
            'user_center_id': 'sample-user-center-id',
            'terminal_id': 'sample-terminal-id',
            'specialty': 'تخصص نامشخص',
            'center_name': 'مرکز نامشخص',
            'center_address': 'آدرس نامشخص',
            'center_phone': 'تلفن نامشخص'
        }