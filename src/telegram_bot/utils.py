"""
Utility functions for Telegram bot handlers
"""
from typing import Optional, List, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from src.database.database import db_session
from src.database.models import User, Doctor, Subscription
from src.utils.logger import get_logger

logger = get_logger("TelegramUtils")


class TelegramUtils:
    """کلاس utility برای handlerهای تلگرام"""
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """بررسی دسترسی ادمین - تابع مشترک"""
        try:
            from src.telegram_bot.user_roles import user_role_manager
            return user_role_manager.is_admin_or_higher(user_id)
        except Exception as e:
            logger.error(f"خطا در بررسی دسترسی ادمین: {e}")
            return False
    
    @staticmethod
    async def ensure_user_exists(user) -> Optional[User]:
        """اطمینان از وجود کاربر در دیتابیس - تابع مشترک"""
        try:
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
                return db_user
                
        except Exception as e:
            logger.error(f"خطا در ثبت/به‌روزرسانی کاربر: {e}")
            return None
    
    @staticmethod
    def create_back_button(callback_data: str = "back_to_main") -> List[List[InlineKeyboardButton]]:
        """ایجاد دکمه بازگشت - تابع مشترک"""
        return [[InlineKeyboardButton("🔙 بازگشت", callback_data=callback_data)]]
    
    @staticmethod
    def create_error_keyboard(callback_data: str = "back_to_main") -> InlineKeyboardMarkup:
        """ایجاد keyboard خطا - تابع مشترک"""
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 بازگشت به منو", callback_data=callback_data)
        ]])
    
    @staticmethod
    async def handle_database_error(query, error: Exception, operation: str = "عملیات"):
        """مدیریت خطای دیتابیس - تابع مشترک"""
        logger.error(f"خطا در {operation}: {error}")
        await query.edit_message_text(
            f"❌ خطا در {operation}. لطفاً دوباره تلاش کنید.",
            reply_markup=TelegramUtils.create_error_keyboard()
        )
    
    @staticmethod
    async def handle_validation_error(query, error: Exception):
        """مدیریت خطای اعتبارسنجی - تابع مشترک"""
        logger.error(f"خطا در اعتبارسنجی: {error}")
        await query.edit_message_text(
            "❌ داده نامعتبر. لطفاً دوباره تلاش کنید.",
            reply_markup=TelegramUtils.create_error_keyboard()
        )
    
    @staticmethod
    def get_user_subscriptions(user_id: int) -> List[Subscription]:
        """دریافت اشتراک‌های کاربر - تابع مشترک"""
        try:
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                if user:
                    return session.query(Subscription).filter(
                        Subscription.user_id == user.id,
                        Subscription.is_active == True
                    ).all()
                return []
        except Exception as e:
            logger.error(f"خطا در دریافت اشتراک‌های کاربر: {e}")
            return []
    
    @staticmethod
    def get_active_doctors() -> List[Doctor]:
        """دریافت دکترهای فعال - تابع مشترک"""
        try:
            with db_session() as session:
                return session.query(Doctor).filter(Doctor.is_active == True).all()
        except Exception as e:
            logger.error(f"خطا در دریافت دکترهای فعال: {e}")
            return [] 