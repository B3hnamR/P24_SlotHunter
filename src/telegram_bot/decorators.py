"""
Decorator های ربات تلگرام
"""
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from src.telegram_bot.access_control import access_control
from src.utils.logger import get_logger

logger = get_logger("TelegramDecorators")


def require_access(func):
    """Decorator برای بررسی دسترسی کاربر"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        if not access_control.is_user_allowed(user_id):
            # پیام عدم دسترسی
            access_denied_message = """
🔒 **دسترسی محدود**

متأسفانه شما دسترسی به استفاده از این ربات را ندارید.

📞 **برای دریافت دسترسی:**
با ادمین سیستم تماس بگیرید.

🆔 **شناسه شما:** `{}`
            """.format(user_id)
            
            if update.message:
                await update.message.reply_text(access_denied_message, parse_mode='Markdown')
            elif update.callback_query:
                await update.callback_query.edit_message_text(access_denied_message, parse_mode='Markdown')
            
            logger.warning(f"دسترسی غیرمجاز: کاربر {user_id} ({update.effective_user.first_name})")
            return
        
        # اجرای تابع اصلی
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def admin_only(func):
    """Decorator برای دسترسی فقط ادمین"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        from src.telegram_bot.admin_handlers import TelegramAdminHandlers
        
        if not TelegramAdminHandlers.is_admin(user_id):
            admin_only_message = """
🔧 **دسترسی ادمین مورد نیاز**

این دستور فقط برای ادمین‌های سیستم در دسترس است.

🆔 **شناسه شما:** `{}`
            """.format(user_id)
            
            if update.message:
                await update.message.reply_text(admin_only_message, parse_mode='Markdown')
            elif update.callback_query:
                await update.callback_query.edit_message_text(admin_only_message, parse_mode='Markdown')
            
            logger.warning(f"تلاش دسترسی غیرمجاز به پنل ادمین: کاربر {user_id}")
            return
        
        # اجرای تابع اصلی
        return await func(update, context, *args, **kwargs)
    
    return wrapper


# Aliases برای سازگاری با __init__.py
admin_required = admin_only
user_required = require_access