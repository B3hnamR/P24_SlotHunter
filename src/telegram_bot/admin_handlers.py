"""
Handler های ادمین ربات تلگرام - Fixed Version
"""
import re
import requests
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

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
        """بررسی دسترسی ادمین - استفاده از سیستم نقش‌های جدید"""
        try:
            from src.telegram_bot.user_roles import user_role_manager
            return user_role_manager.is_admin_or_higher(user_id)
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
            
            # اگر از callback query آمده، ویرایش کن، وگرنه پیام جدید بفرست
            if update.callback_query:
                await update.callback_query.edit_message_text(admin_text, reply_markup=reply_markup)
            else:
                await update.message.reply_text(admin_text, reply_markup=reply_markup)
            logger.info("Admin panel sent successfully")
            
        except Exception as e:
            logger.error(f"خطا در نمایش پنل ادمین: {e}")
            error_message = "❌ خطا در بارگذاری پنل مدیریت."
            if update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
    
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
            "لینک صفحه دکتر در پذیرش۲۴ را ارسال کنید:\n\n"
            "✅ فرمت‌های پشتیبانی شده:\n"
            "• https://www.paziresh24.com/dr/دکتر-نام-0/\n"
            "• https://www.paziresh24.com/dr/%D8%AF%DA%A9%D8%AA%D8%B1-...\n\n"
            "برای لغو: /cancel"
        )
        
        return ADD_DOCTOR_LINK
    
    @staticmethod
    async def process_doctor_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش لینک دکتر"""
        link = update.message.text.strip()
        
        logger.info(f"Processing doctor link: {link}")
        
        # بررسی فرمت لینک
        if not re.match(r'https://www\.paziresh24\.com/dr/.+', link):
            await update.message.reply_text(
                "❌ لینک نامعتبر است.\n\n"
                "لطفاً لینک صحیح صفحه دکتر در پذیرش۲۴ را ارسال کنید.\n\n"
                "مثال:\n"
                "https://www.paziresh24.com/dr/دکتر-نام-خانوادگی-0/"
            )
            return ADD_DOCTOR_LINK

        from src.api.parser import extract_doctor_info_from_url

        await update.message.reply_text("در حال استخراج اطلاعات دکتر... لطفاً صبر کنید.")
        
        doctor_info = extract_doctor_info_from_url(link)
        
        if not doctor_info:
            await update.message.reply_text(
                "❌ نتوانستم اطلاعات دکتر را از لینک استخراج کنم.\n\n"
                "لطفاً از صحت لینک مطمئن شوید و دوباره تلاش کنید."
            )
            return ADD_DOCTOR_LINK
        
        context.user_data['doctor_info'] = doctor_info
        
        # نمایش اطلاعات برای تأیید
        confirm_text = f"""✅ اطلاعات دکتر:

👨‍⚕️ نام: {doctor_info.get('name', 'نامشخص')}
🏥 تخصص: {doctor_info.get('specialty', 'نامشخص')}
🏢 مرکز: {doctor_info.get('center_name', 'نامشخص')}

🔧 اطلاعات فنی:
• Slug: {doctor_info.get('slug', 'نامشخص')}
• Center ID: {doctor_info.get('center_id', 'نامشخص')}
• Service ID: {doctor_info.get('service_id', 'نامشخص')}

آیا می‌خواهید این دکتر را اضافه کنید؟"""
        
        keyboard = [
            [InlineKeyboardButton("✅ تأیید", callback_data="confirm_add_doctor")],
            [InlineKeyboardButton("❌ لغو", callback_data="cancel_add_doctor")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(confirm_text, reply_markup=reply_markup)
        
        return ADD_DOCTOR_CONFIRM
    
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
                    f"🔔 از این پس نوبت‌های این دکتر نیز بررسی می‌شود.\n\n"
                    f"📋 اطلاعات ثبت شده:\n"
                    f"• نام: {doctor_info['name']}\n"
                    f"• تخصص: {doctor_info['specialty']}\n"
                    f"• مرکز: {doctor_info['center_name']}"
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
            
            # ذخیره در دیتابیس یا فایل کانفیگ
            config = Config()
            config.set_check_interval(interval) # فرض بر اینکه این متد وجود دارد

            await update.message.reply_text(
                f"✅ زمان بررسی به {interval} ثانیه تغییر کرد.\n\n"
                f"این تغییر در دور بعدی نظارت اعمال خواهد شد."
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
            await update.message.reply_text(
                f"❌ خطا در تنظیم زمان بررسی.\n\n"
                f"جزئیات: {str(e)}"
            )
        
        return ConversationHandler.END
    
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
    async def show_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش آمار سیستم"""
        query = update.callback_query
        await query.answer()
        
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
                
                stats_text = f"""📊 **آمار سیستم P24_SlotHunter**

👥 **کاربران فعال:** {total_users}
👨‍⚕️ **کل دکترها:** {total_doctors}
✅ **دکترهای فعال:** {active_doctors}
📝 **اشتراک‌های فعال:** {total_subscriptions}
🎯 **نوبت‌های پیدا شده امروز:** {appointments_today}

⏰ **آخرین بررسی:** در حال اجرا
🔄 **وضعیت سیستم:** فعال"""
                
                keyboard = [[
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_panel")
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"خطا در نمایش آمار: {e}")
            await query.edit_message_text("❌ خطا در دریافت آمار سیستم.")
    
    @staticmethod
    async def show_user_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کاربران"""
        query = update.callback_query
        await query.answer()
        
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
    
    @staticmethod
    async def show_access_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تنظیمات دسترسی"""
        query = update.callback_query
        await query.answer()
        
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return
        
        access_text = """🔒 **تنظیمات دسترسی**

⚠️ **وضعیت فعلی:** ربات برای همه در دسترس است

🔧 **برای محدود کردن دسترسی:**
1. از منوی مدیریت سرور استفاده کنید
2. گزینه "Access Control" را انتخاب کنید
3. لیست کاربران مجاز را تنظیم کنید

💡 **نکته:** تغییرات از طریق سرور اعمال می‌شود"""
        
        keyboard = [[
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_panel")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(access_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    @staticmethod
    async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لغو مکالمه"""
        await update.message.reply_text(
            "❌ عملیات لغو شد.\n\n"
            "🔄 برای بازگشت: /admin"
        )
        return ConversationHandler.END