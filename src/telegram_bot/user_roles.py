"""
سیستم مدیریت نقش‌های کاربری
"""
from enum import Enum
from typing import Optional, List
import os

from src.database.database import db_session
from src.database.models import User
from src.utils.logger import get_logger
from src.utils.config import Config

logger = get_logger("UserRoles")


class UserRole(Enum):
    """نقش‌های کاربری"""
    GUEST = "guest"           # کاربر مهمان (دسترسی محدود)
    USER = "user"             # کاربر عادی (دسترسی کامل به امکانات کاربری)
    MODERATOR = "moderator"   # مدیر (دسترسی به بعضی امکانات ادمین)
    ADMIN = "admin"           # ادمین کامل (دسترسی به همه چیز)
    SUPER_ADMIN = "super_admin"  # سوپر ادمین (مالک سیستم)


class UserRoleManager:
    """مدیریت نقش‌های کاربری"""
    
    def __init__(self):
        self.config = Config()
        
    def get_user_role(self, user_id: int) -> UserRole:
        """تشخیص نقش کاربر"""
        
        # بررسی سوپر ادمین (از .env)
        if self._is_super_admin(user_id):
            return UserRole.SUPER_ADMIN
        
        # بررسی در دیتابیس
        try:
            with db_session() as session:
                user = session.query(User).filter(
                    User.telegram_id == user_id,
                    User.is_active == True
                ).first()
                
                if user:
                    if user.is_admin:
                        return UserRole.ADMIN
                    elif hasattr(user, 'is_moderator') and user.is_moderator:
                        return UserRole.MODERATOR
                    else:
                        return UserRole.USER
                else:
                    # کاربر جدید - بررسی حالت دسترسی
                    access_mode = os.getenv('ACCESS_MODE', 'open')
                    
                    if access_mode == 'open':
                        return UserRole.USER  # کاربران جدید به عنوان USER
                    elif access_mode == 'admin_only':
                        return UserRole.GUEST  # فقط مهمان
                    else:  # restricted
                        return UserRole.GUEST  # نیاز به تایید
                        
        except Exception as e:
            logger.error(f"خطا در تشخیص نقش کاربر {user_id}: {e}")
            return UserRole.GUEST
    
    def _is_super_admin(self, user_id: int) -> bool:
        """بررسی سوپر ادمین بودن"""
        return user_id == self.config.admin_chat_id
    
    def is_admin_or_higher(self, user_id: int) -> bool:
        """بررسی ادمین یا بالاتر بودن"""
        role = self.get_user_role(user_id)
        return role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    def is_moderator_or_higher(self, user_id: int) -> bool:
        """بررسی مدیر یا بالاتر بودن"""
        role = self.get_user_role(user_id)
        return role in [UserRole.MODERATOR, UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    def is_user_or_higher(self, user_id: int) -> bool:
        """بررسی کاربر یا بالاتر بودن"""
        role = self.get_user_role(user_id)
        return role in [UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    def can_access_admin_panel(self, user_id: int) -> bool:
        """بررسی دسترسی به پنل ادمین"""
        return self.is_admin_or_higher(user_id)
    
    def can_manage_users(self, user_id: int) -> bool:
        """بررسی دسترسی به مدیریت کاربران"""
        return self.is_admin_or_higher(user_id)
    
    def can_manage_doctors(self, user_id: int) -> bool:
        """بررسی دسترسی به مدیریت دکترها"""
        return self.is_moderator_or_higher(user_id)
    
    def can_view_statistics(self, user_id: int) -> bool:
        """بررسی دسترسی به آمار"""
        return self.is_moderator_or_higher(user_id)
    
    def can_change_settings(self, user_id: int) -> bool:
        """بررسی دسترسی به تنظیمات"""
        return self.is_admin_or_higher(user_id)
    
    def set_user_role(self, user_id: int, role: UserRole, by_admin_id: int) -> bool:
        """تنظیم نقش کاربر"""
        
        # بررسی دسترسی ادمین
        if not self.is_admin_or_higher(by_admin_id):
            logger.warning(f"کاربر {by_admin_id} سعی در تغییر نقش کاربر {user_id} داشت")
            return False
        
        # سوپر ادمین نمی‌تواند تغییر کند
        if self._is_super_admin(user_id):
            logger.warning(f"سعی در تغییر نقش سوپر ادمین {user_id}")
            return False
        
        try:
            with db_session() as session:
                user = session.query(User).filter(User.telegram_id == user_id).first()
                
                if not user:
                    # ایجاد کاربر جدید
                    user = User(
                        telegram_id=user_id,
                        is_active=True,
                        is_admin=False
                    )
                    session.add(user)
                
                # تنظیم نقش
                if role == UserRole.ADMIN:
                    user.is_admin = True
                    if hasattr(user, 'is_moderator'):
                        user.is_moderator = False
                elif role == UserRole.MODERATOR:
                    user.is_admin = False
                    if hasattr(user, 'is_moderator'):
                        user.is_moderator = True
                elif role == UserRole.USER:
                    user.is_admin = False
                    if hasattr(user, 'is_moderator'):
                        user.is_moderator = False
                elif role == UserRole.GUEST:
                    user.is_active = False
                
                session.commit()
                logger.info(f"نقش کاربر {user_id} به {role.value} تغییر کرد (توسط {by_admin_id})")
                return True
                
        except Exception as e:
            logger.error(f"خطا در تنظیم نقش کاربر: {e}")
            return False
    
    def get_role_display_name(self, role: UserRole) -> str:
        """نام نمایشی نقش"""
        role_names = {
            UserRole.GUEST: "🔒 مهمان",
            UserRole.USER: "👤 کاربر",
            UserRole.MODERATOR: "👮 مدیر",
            UserRole.ADMIN: "👑 ادمین",
            UserRole.SUPER_ADMIN: "⭐ سوپر ادمین"
        }
        return role_names.get(role, "❓ نامشخص")
    
    def get_role_permissions(self, role: UserRole) -> List[str]:
        """لیست مجوزهای نقش"""
        permissions = {
            UserRole.GUEST: [
                "مشاهده اطلاعات عمومی"
            ],
            UserRole.USER: [
                "مشاهده دکترها",
                "اشتراک در دکترها", 
                "دریافت اطلاعیه‌ها",
                "مدیریت اشتراک‌های شخصی"
            ],
            UserRole.MODERATOR: [
                "همه مجوزهای کاربر",
                "مدیریت دکترها",
                "مشاهده آمار",
                "مدیریت محتوا"
            ],
            UserRole.ADMIN: [
                "همه مجوزهای مدیر",
                "مدیریت کاربران",
                "تغییر تنظیمات",
                "دسترسی به پنل ادمین",
                "مدیریت سیستم"
            ],
            UserRole.SUPER_ADMIN: [
                "همه مجوزها",
                "مدیریت ادمین‌ها",
                "تنظیمات پیشرفته",
                "دسترسی کامل سیستم"
            ]
        }
        return permissions.get(role, [])


# Instance سراسری
user_role_manager = UserRoleManager()