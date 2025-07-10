"""
Admin menu handlers for role-based access control
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.database.database import db_session
from src.database.models import User, Doctor, Subscription, AppointmentLog
from src.telegram_bot.user_roles import user_role_manager, UserRole
from src.telegram_bot.messages import MessageFormatter
from src.utils.logger import get_logger

logger = get_logger("AdminMenuHandlers")


class AdminMenuHandlers:
    """کلاس handler های منوی ادمین"""
    
    @staticmethod
    async def show_system_stats_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی آمار سیستم (مدیر و بالاتر)"""
        user_id = update.effective_user.id
        
        # بررسی ��سترسی
        if not user_role_manager.is_moderator_or_higher(user_id):
            await update.message.reply_text(
                "❌ شما دسترسی به این بخش را ندارید.",
                reply_markup=MenuHandlers.get_main_menu_keyboard(user_id)
            )
            return
        
        try:
            with db_session() as session:
                # آمار کلی
                total_users = session.query(User).count()
                active_users = session.query(User).filter(User.is_active == True).count()
                total_doctors = session.query(Doctor).count()
                active_doctors = session.query(Doctor).filter(Doctor.is_active == True).count()
                total_subscriptions = session.query(Subscription).filter(Subscription.is_active == True).count()
                
                # آمار امروز
                today = datetime.now().date()
                appointments_today = session.query(AppointmentLog).filter(
                    AppointmentLog.created_at >= today
                ).count()
                
                # آمار هفته گذشته
                week_ago = today - timedelta(days=7)
                appointments_week = session.query(AppointmentLog).filter(
                    AppointmentLog.created_at >= week_ago
                ).count()
                
                stats_text = f"""
📈 **آمار سیستم**

👥 **کاربران:**
• کل کاربران: {total_users}
• کاربران فعال: {active_users}

👨‍⚕️ **دکترها:**
• کل دکترها: {total_doctors}
• دکترهای فعال: {active_doctors}

📝 **اشتراک‌ها:**
• اشتراک‌های فعال: {total_subscriptions}

🎯 **نوبت‌ها:**
• امروز: {appointments_today}
• هفته گذشته: {appointments_week}

📅 **تاریخ:** {datetime.now().strftime('%Y/%m/%d %H:%M')}
                """
                
                keyboard = [
                    [InlineKeyboardButton("📊 آمار تفصیلی", callback_data="detailed_system_stats")],
                    [InlineKeyboardButton("📈 نمودار آمار", callback_data="stats_chart")],
                    [InlineKeyboardButton("📋 گزارش کامل", callback_data="full_report")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    stats_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش آمار سیستم: {e}")
            await update.message.reply_text(
                MessageFormatter.error_message(),
                reply_markup=MenuHandlers.get_main_menu_keyboard(user_id)
            )
    
    @staticmethod
    async def show_user_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی مدیریت کاربران (مدیر و بالاتر)"""
        user_id = update.effective_user.id
        
        # بررسی دسترسی
        if not user_role_manager.is_moderator_or_higher(user_id):
            await update.message.reply_text(
                "❌ شما دسترسی به این بخش را ندارید.",
                reply_markup=MenuHandlers.get_main_menu_keyboard(user_id)
            )
            return
        
        try:
            with db_session() as session:
                # آمار کاربران
                total_users = session.query(User).count()
                active_users = session.query(User).filter(User.is_active == True).count()
                admin_users = session.query(User).filter(User.is_admin == True).count()
                
                # کاربران جدید (24 ساعت گذشته)
                yesterday = datetime.now() - timedelta(days=1)
                new_users = session.query(User).filter(
                    User.created_at >= yesterday
                ).count()
                
                management_text = f"""
👥 **مدیریت کاربران**

📊 **آمار کلی:**
• کل کاربران: {total_users}
• کاربران فعال: {active_users}
• ادمین‌ها: {admin_users}
• کاربران جدید (24 ساعت): {new_users}

🔧 **عملیات مدیریتی:**
                """
                
                keyboard = [
                    [InlineKeyboardButton("👤 لیست کاربران", callback_data="list_users")],
                    [InlineKeyboardButton("🔍 جستجوی کاربر", callback_data="search_user")],
                    [InlineKeyboardButton("👑 مدیریت ادمین‌ها", callback_data="manage_admins")],
                    [InlineKeyboardButton("🚫 کاربران مسدود", callback_data="blocked_users")],
                    [InlineKeyboardButton("📊 آمار کاربران", callback_data="user_statistics")],
                    [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    management_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"❌ خطا در نمایش مدیریت کاربران: {e}")
            await update.message.reply_text(
                MessageFormatter.error_message(),
                reply_markup=MenuHandlers.get_main_menu_keyboard(user_id)
            )
    
    @staticmethod
    async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش پنل ادمین (ادمین و بالاتر)"""
        user_id = update.effective_user.id
        
        # بررسی دسترسی
        if not user_role_manager.is_admin_or_higher(user_id):
            await update.message.reply_text(
                "❌ شما دسترسی به این بخش را ندارید.",
                reply_markup=MenuHandlers.get_main_menu_keyboard(user_id)
            )
            return
        
        user_role = user_role_manager.get_user_role(user_id)
        role_display = user_role_manager.get_role_display_name(user_role)
        
        admin_text = f"""
👑 **پنل ادمین**

👤 **نقش شما:** {role_display}

🔧 **امکانات ادمین:**
• مدیریت دکترها
• مدیریت کاربران
• تنظیمات سیستم
• مشاهده لاگ‌ها
• مدیریت دسترسی‌ها

⚡ **عملیات سریع:**
        """
        
        keyboard = [
            [InlineKeyboardButton("👨‍⚕️ مدیریت دکترها", callback_data="admin_manage_doctors")],
            [InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_manage_users")],
            [InlineKeyboardButton("⚙️ تنظیمات سیستم", callback_data="admin_system_settings")],
            [InlineKeyboardButton("📋 مشاهده لاگ‌ها", callback_data="admin_view_logs")],
            [InlineKeyboardButton("🔒 مدیریت دسترسی", callback_data="admin_access_control")],
            [InlineKeyboardButton("📊 داشبورد ادمین", callback_data="admin_dashboard")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            admin_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def show_system_management_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی مدیریت سیستم (ادمین و بالاتر)"""
        user_id = update.effective_user.id
        
        # بررسی دسترسی
        if not user_role_manager.is_admin_or_higher(user_id):
            await update.message.reply_text(
                "❌ شما دسترسی به این بخش را ندارید.",
                reply_markup=MenuHandlers.get_main_menu_keyboard(user_id)
            )
            return
        
        system_text = f"""
🔧 **مدیریت سیستم**

🖥️ **وضعیت سیستم:**
• ربات: ✅ فعال
• دیتابیس: ✅ متصل
• API: ✅ در دسترس

⚙️ **عملیات سیستم:**
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 ریستارت سیستم", callback_data="system_restart")],
            [InlineKeyboardButton("📊 مانیتورینگ", callback_data="system_monitoring")],
            [InlineKeyboardButton("🗄️ مدیریت دیتابیس", callback_data="database_management")],
            [InlineKeyboardButton("📝 مدیریت لاگ‌ها", callback_data="log_management")],
            [InlineKeyboardButton("🔧 تنظیمات پیشرفته", callback_data="advanced_settings")],
            [InlineKeyboardButton("💾 پشتیبان‌گیری", callback_data="backup_system")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            system_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def show_super_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی سوپر ادمین (فقط سوپر ادمین)"""
        user_id = update.effective_user.id
        
        # بررسی دسترسی
        if user_role_manager.get_user_role(user_id) != UserRole.SUPER_ADMIN:
            await update.message.reply_text(
                "❌ شما دسترسی به این بخش را ندارید.",
                reply_markup=MenuHandlers.get_main_menu_keyboard(user_id)
            )
            return
        
        super_admin_text = f"""
⭐ **پنل سوپر ادمین**

🔐 **دسترسی کامل سیستم**

⚡ **امکانات ویژه:**
• مدیریت ادمین‌ها
• تنظیمات امنیتی
• کنترل کامل سیستم
• دسترسی به همه داده‌ها

🛡️ **عملیات حساس:**
        """
        
        keyboard = [
            [InlineKeyboardButton("👑 مدیریت ادمین‌ها", callback_data="super_manage_admins")],
            [InlineKeyboardButton("🔐 تنظیمات امنیتی", callback_data="super_security_settings")],
            [InlineKeyboardButton("🗄️ مدیریت کامل دیتابیس", callback_data="super_database_control")],
            [InlineKeyboardButton("📊 آمار کامل سیستم", callback_data="super_full_stats")],
            [InlineKeyboardButton("🔧 تنظیمات سیستمی", callback_data="super_system_config")],
            [InlineKeyboardButton("⚠️ عملیات اضطراری", callback_data="super_emergency_ops")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            super_admin_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def show_advanced_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش منوی تنظیمات پیشرفته (سوپر ادمین)"""
        user_id = update.effective_user.id
        
        # بررسی دسترسی
        if user_role_manager.get_user_role(user_id) != UserRole.SUPER_ADMIN:
            await update.message.reply_text(
                "❌ شما دسترسی به این بخش را ندارید.",
                reply_markup=MenuHandlers.get_main_menu_keyboard(user_id)
            )
            return
        
        advanced_text = f"""
🛠️ **تنظیمات پی��رفته**

⚙️ **تنظیمات سیستم:**
• تنظیمات API
• تنظیمات دیتابیس
• تنظیمات امنیتی
• تنظیمات شبکه

🔧 **پیکربندی:**
        """
        
        keyboard = [
            [InlineKeyboardButton("🌐 تنظیمات API", callback_data="advanced_api_settings")],
            [InlineKeyboardButton("🗄️ تنظیمات دیتابیس", callback_data="advanced_db_settings")],
            [InlineKeyboardButton("🔐 تنظیمات امنیتی", callback_data="advanced_security_settings")],
            [InlineKeyboardButton("📡 تنظیمات شبکه", callback_data="advanced_network_settings")],
            [InlineKeyboardButton("⏰ تنظیمات زمان‌بندی", callback_data="advanced_schedule_settings")],
            [InlineKeyboardButton("📊 تنظیمات لاگ", callback_data="advanced_log_settings")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            advanced_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )


# Import MenuHandlers to avoid circular import
from src.telegram_bot.menu_handlers import MenuHandlers