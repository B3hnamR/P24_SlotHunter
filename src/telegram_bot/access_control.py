"""
سیستم کنترل دسترسی ربات تلگرام
"""
import os
from typing import List, Set
from pathlib import Path

from src.database.database import db_session
from src.database.models import User
from src.utils.logger import get_logger

logger = get_logger("AccessControl")


class AccessControl:
    """کلاس مدیریت دسترسی"""
    
    def __init__(self):
        self.allowed_users_file = Path("config/allowed_users.txt")
        self.access_mode = os.getenv('ACCESS_MODE', 'open')  # open, restricted, admin_only
        
    def is_user_allowed(self, user_id: int) -> bool:
        """بررسی دسترسی کاربر"""
        
        # حالت باز (همه دسترسی دارند)
        if self.access_mode == 'open':
            return True
        
        # بررسی ادمین
        if self._is_admin(user_id):
            return True
        
        # حالت فقط ادمین
        if self.access_mode == 'admin_only':
            return False
        
        # حالت محدود (بررسی لیست مجاز)
        if self.access_mode == 'restricted':
            return self._is_in_allowed_list(user_id)
        
        return False
    
    def _is_admin(self, user_id: int) -> bool:
        """بررسی ادمین بودن کاربر"""
        from src.utils.config import Config
        config = Config()
        
        # ادمین اصلی
        if user_id == config.admin_chat_id:
            return True
        
        # ادمین‌های اضافی از دیتابیس
        try:
            with db_session() as session:
                user = session.query(User).filter(
                    User.telegram_id == user_id,
                    User.is_admin == True,
                    User.is_active == True
                ).first()
                return user is not None
        except:
            return False
    
    def _is_in_allowed_list(self, user_id: int) -> bool:
        """بررسی وجود در لیست مجاز"""
        try:
            if not self.allowed_users_file.exists():
                return False
            
            with open(self.allowed_users_file, 'r') as f:
                allowed_users = [int(line.strip()) for line in f if line.strip().isdigit()]
            
            return user_id in allowed_users
        except:
            return False
    
    def add_allowed_user(self, user_id: int) -> bool:
        """اضافه کردن کاربر به لیست مجاز"""
        try:
            # ایجاد پوشه config در صورت عدم وجود
            self.allowed_users_file.parent.mkdir(exist_ok=True)
            
            # خواندن لیست فعلی
            allowed_users = set()
            if self.allowed_users_file.exists():
                with open(self.allowed_users_file, 'r') as f:
                    allowed_users = {int(line.strip()) for line in f if line.strip().isdigit()}
            
            # اضافه کردن کاربر جدید
            allowed_users.add(user_id)
            
            # نوشتن لیست جدید
            with open(self.allowed_users_file, 'w') as f:
                for uid in sorted(allowed_users):
                    f.write(f"{uid}\n")
            
            logger.info(f"کاربر {user_id} به لیست مجاز اضافه شد")
            return True
        except Exception as e:
            logger.error(f"خطا در اضافه کردن کاربر به لیست مجاز: {e}")
            return False
    
    def remove_allowed_user(self, user_id: int) -> bool:
        """حذف کاربر از لیست مجاز"""
        try:
            if not self.allowed_users_file.exists():
                return False
            
            # خواندن لیست فعلی
            with open(self.allowed_users_file, 'r') as f:
                allowed_users = {int(line.strip()) for line in f if line.strip().isdigit()}
            
            # حذف کاربر
            if user_id in allowed_users:
                allowed_users.remove(user_id)
                
                # نوشتن لیست جدید
                with open(self.allowed_users_file, 'w') as f:
                    for uid in sorted(allowed_users):
                        f.write(f"{uid}\n")
                
                logger.info(f"کاربر {user_id} از لیست مجاز حذف شد")
                return True
            
            return False
        except Exception as e:
            logger.error(f"خطا در حذف کاربر از لیست مجاز: {e}")
            return False
    
    def get_allowed_users(self) -> List[int]:
        """دریافت لیست کاربران مجاز"""
        try:
            if not self.allowed_users_file.exists():
                return []
            
            with open(self.allowed_users_file, 'r') as f:
                return [int(line.strip()) for line in f if line.strip().isdigit()]
        except:
            return []
    
    def set_access_mode(self, mode: str) -> bool:
        """تنظیم حالت دسترسی"""
        valid_modes = ['open', 'restricted', 'admin_only']
        
        if mode not in valid_modes:
            return False
        
        try:
            # به‌روزرسانی فایل .env
            env_file = Path(".env")
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # اضافه یا به‌روزرسانی ACCESS_MODE
                if 'ACCESS_MODE=' in content:
                    import re
                    content = re.sub(r'ACCESS_MODE=.*', f'ACCESS_MODE={mode}', content)
                else:
                    content += f"\nACCESS_MODE={mode}\n"
                
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            self.access_mode = mode
            logger.info(f"حالت دسترسی به {mode} تغییر کرد")
            return True
        except Exception as e:
            logger.error(f"خطا در تنظیم حالت دسترسی: {e}")
            return False
    
    def get_access_mode(self) -> str:
        """دریافت حالت دسترسی فعلی"""
        return self.access_mode


# Instance سراسری
access_control = AccessControl()