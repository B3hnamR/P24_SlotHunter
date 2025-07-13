#!/usr/bin/env python3
"""
فایل اصلی P24_SlotHunter - نسخه حل شده
"""
import asyncio
import logging
import signal
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.api.paziresh_client import PazireshAPI
from src.telegram_bot.bot import SlotHunterBot
from src.database.database import init_database, db_session
from src.database.models import Doctor as DBDoctor


class SimpleDoctor:
    """کلاس ساده برای نگهداری اطلاعات دکتر بدون SQLAlchemy dependency"""
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.slug = data['slug']
        self.center_id = data['center_id']
        self.service_id = data['service_id']
        self.user_center_id = data['user_center_id']
        self.terminal_id = data['terminal_id']
        self.specialty = data['specialty']
        self.center_name = data['center_name']
        self.center_address = data['center_address']
        self.center_phone = data['center_phone']


class SlotHunter:
    """کلاس اصلی نوبت‌یاب"""
    
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger(
            level=self.config.log_level,
            log_file=self.config.log_file
        )
        self.running = False
        self.telegram_bot = None
        
    async def start(self):
        """شروع نوبت‌یاب"""
        self.logger.info("🚀 شروع P24_SlotHunter")
        
        # بررسی تنظیمات
        if not self.config.telegram_bot_token:
            self.logger.error("❌ توکن ربات تلگرام تنظیم نشده است")
            return
        
        # راه‌اندازی دیتابیس
        try:
            init_database()
            self.logger.info("✅ دیتابیس راه‌اندازی شد")
        except Exception as e:
            self.logger.error(f"❌ خطا در راه‌اندازی دیتابیس: {e}")
            return
        
        # بارگذاری دکترها در دیتابیس
        await self._load_doctors_to_db()
        
        # راه‌اندازی ربات تلگرام
        try:
            self.telegram_bot = SlotHunterBot(self.config.telegram_bot_token)
            await self.telegram_bot.initialize()
            self.logger.info("✅ ربات تلگرام راه‌اندازی شد")
        except Exception as e:
            self.logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
            return
        
        # بررسی دکترها از دیتابیس
        try:
            with db_session() as session:
                db_doctors_count = session.query(DBDoctor).count()
                active_doctors_count = session.query(DBDoctor).filter(DBDoctor.is_active == True).count()
                
                if db_doctors_count == 0:
                    self.logger.warning("⚠️ هیچ دکتری در دیتابیس یافت نشد - ربات فقط برای مدیریت فعال است")
                else:
                    self.logger.info(f"👨‍⚕️ {db_doctors_count} دکتر در دیتابیس ({active_doctors_count} فعال)")
        except Exception as e:
            self.logger.error(f"❌ خطا در بررسی دکترها: {e}")
        
        self.running = True
        
        # شروع ربات تلگرام
        self.running = True
        self.logger.info("✅ ربات تلگرام در حال اجرا است...")
        self.logger.info("🕒 وظایف بررسی نوبت‌ها توسط Celery در پس‌زمینه مدیریت می‌شود.")
        self.logger.info("برای مشاهده لاگ‌های Celery، دستور `celery -A src.celery_app worker -l info` را اجرا کنید.")
        self.logger.info("برای اجرای Celery Beat، دستور `celery -A src.celery_app beat -l info` را اجرا کنید.")

        # این حلقه فقط برای زنده نگه داشتن برنامه است
        while self.running:
            await asyncio.sleep(1)

    async def _load_doctors_to_db(self):
        """بارگذاری دکترها در دی��ابیس"""
        try:
            doctors_config = self.config.get_doctors_config()
            config_doctors = [Doctor(**doc_config) for doc_config in doctors_config]
            
            with db_session() as session:
                for doctor in config_doctors:
                    # بررسی وجود دکتر
                    existing = session.query(DBDoctor).filter(
                        DBDoctor.slug == doctor.slug
                    ).first()
                    
                    if not existing:
                        # اضافه کردن دکتر جدید
                        db_doctor = DBDoctor(
                            name=doctor.name,
                            slug=doctor.slug,
                            center_id=doctor.center_id,
                            service_id=doctor.service_id,
                            user_center_id=doctor.user_center_id,
                            terminal_id=doctor.terminal_id,
                            specialty=doctor.specialty,
                            center_name=doctor.center_name,
                            center_address=doctor.center_address,
                            center_phone=doctor.center_phone,
                            is_active=doctor.is_active
                        )
                        session.add(db_doctor)
                        self.logger.info(f"➕ دکتر جدید اضافه شد: {doctor.name}")
                    else:
                        # به‌روزرسانی اطلاعات
                        existing.name = doctor.name
                        existing.specialty = doctor.specialty
                        existing.center_name = doctor.center_name
                        existing.center_address = doctor.center_address
                        existing.center_phone = doctor.center_phone
                        existing.is_active = doctor.is_active
                
                session.commit()
                
        except Exception as e:
            self.logger.error(f"❌ خطا در بارگذاری دکترها: {e}")
    
    
    async def stop(self):
        """توقف نوبت‌یاب"""
        self.logger.info("🛑 در حال توقف...")
        self.running = False
        
        if self.telegram_bot:
            await self.telegram_bot.stop()


def signal_handler(signum, frame):
    """مدیریت سیگنال‌های سیستم"""
    print("\n🛑 دریافت سیگنال توقف...")
    sys.exit(0)


async def main():
    """تابع اصلی"""
    # تنظیم signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # ایجاد و اجرای نوبت‌یاب
    hunter = SlotHunter()
    try:
        await hunter.start()
    except KeyboardInterrupt:
        await hunter.stop()
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")


if __name__ == "__main__":
    asyncio.run(main())