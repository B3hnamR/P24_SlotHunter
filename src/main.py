#!/usr/bin/env python3
"""
فایل اصلی P24_SlotHunter - نسخه حل شده
"""
import asyncio
import signal
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.api.paziresh_client import PazireshAPI
from src.telegram_bot.bot import SlotHunterBot
from src.database.database import db_session, DatabaseManager
from src.database.models import Doctor as DBDoctor
from src.utils.logger import notify_admin_critical_error
from sqlalchemy import select, func


import httpx

class SlotHunter:
    """کلاس اصلی نوبت‌یاب"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.config = Config()
        self.logger = setup_logger(
            level=self.config.log_level,
            log_file=self.config.log_file
        )
        self.running = False
        self.telegram_bot = None
        self.http_client = None
        
    async def start(self):
        """شروع نوبت‌یاب"""
        self.logger.info("🚀 شروع P24_SlotHunter")
        
        # بررسی تنظیمات
        if not self.config.telegram_bot_token:
            self.logger.error("❌ توکن ربات تلگرام تنظیم نشده است")
            return
        
        # راه‌اندازی دیتابیس
        try:
            await self.db_manager._setup_database()
            self.logger.info("✅ دیتابیس راه‌اندازی شد")
        except Exception as e:
            self.logger.error(f"❌ خطا در راه‌اندازی دیتابیس: {e}")
            await notify_admin_critical_error(f"خطا در راه‌اندازی دیتابیس: {e}")
            return
        
        # بارگذاری دکترها در دیتابیس
        await self._load_doctors_to_db()
        
        # راه‌اندازی ربات تلگرام
        try:
            self.telegram_bot = SlotHunterBot(self.config.telegram_bot_token, self.db_manager)
            await self.telegram_bot.initialize()
            self.logger.info("✅ ربات تلگرام راه‌اندازی شد")
        except Exception as e:
            self.logger.error(f"❌ خطا در راه‌اندازی ربات: {e}")
            await notify_admin_critical_error(f"خطا در راه‌اندازی ربات: {e}")
            return
        
        # بررسی دکترها از دیتابیس
        try:
            async with db_session(self.db_manager) as session:
                db_doctors_count = await session.scalar(select(func.count(DBDoctor.id)))
                active_doctors_count = await session.scalar(
                    select(func.count(DBDoctor.id)).filter(DBDoctor.is_active == True)
                )
                
                if db_doctors_count == 0:
                    self.logger.warning("⚠️ هیچ دکتری در دیتابیس یافت نشد - ربات فقط برای مدیریت فعال است")
                else:
                    self.logger.info(f"👨‍⚕️ {db_doctors_count} دکتر در دیتابیس ({active_doctors_count} فعال)")
        except Exception as e:
            self.logger.error(f"❌ خطا در بررسی دکترها: {e}")
        
        self.running = True
        self.http_client = httpx.AsyncClient(timeout=self.config.api_timeout)
        
        # شروع همزمان ربات و نظارت
        try:
            await asyncio.gather(
                self.telegram_bot.start_polling(),
                self.monitor_loop()
            )
        finally:
            await self.http_client.aclose()
    
    async def _load_doctors_to_db(self):
        """بارگذاری دکترها در دیتابیس"""
        try:
            config_doctors = self.config.get_doctors()
            
            async with db_session(self.db_manager) as session:
                for doctor in config_doctors:
                    # بررسی وجود دکتر
                    result = await session.execute(select(DBDoctor).filter(DBDoctor.slug == doctor.slug))
                    existing = result.scalar_one_or_none()
                    
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
                
                await session.commit()
                
        except Exception as e:
            self.logger.error(f"❌ خطا در بارگذاری دکترها: {e}")
    
    async def monitor_loop(self):
        """حلقه اصلی نظارت"""
        while self.running:
            try:
                # دریافت اطلاعات دکترهای فعال
                async with db_session(self.db_manager) as session:
                    result = await session.execute(select(DBDoctor).filter(DBDoctor.is_active == True))
                    active_doctors = result.scalars().all()
                
                if active_doctors:
                    self.logger.info(f"🔍 شروع دور جدید بررسی {len(active_doctors)} دکتر...")
                    
                    # بررسی همه دکترها
                    for doctor in active_doctors:
                        await self.check_doctor(doctor)
                else:
                    self.logger.debug("📭 هیچ دکتر فعالی برای بررسی وجود ندارد")
                
                # صبر تا دور بعدی
                self.logger.info(f"⏰ صبر {self.config.check_interval} ثانیه تا دور بعدی...")
                await asyncio.sleep(self.config.check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("⏹️ دریافت سیگنال توقف...")
                break
            except Exception as e:
                self.logger.error(f"❌ خطا در حلقه نظارت: {e}")
                await notify_admin_critical_error(f"خطا در حلقه نظارت: {e}")
                await asyncio.sleep(60)  # صبر بیشتر در صورت خطا
    
    async def check_doctor(self, doctor: DBDoctor):
        """بررسی نوبت‌های یک دکتر"""
        try:
            api = PazireshAPI(doctor, client=self.http_client, base_url=self.config.api_base_url)
            appointments = await api.get_available_appointments(days_ahead=self.config.days_ahead)
            
            if appointments:
                self.logger.info(f"🎯 {len(appointments)} نوبت برای {doctor.name} پیدا شد!")
                
                # نمایش در لاگ
                for apt in appointments[:3]:
                    self.logger.info(f"  ⏰ {apt.time_str}")
                
                # اطلاع‌رسانی ��ا ربات تلگرام
                await self.telegram_bot.send_appointment_alert(doctor, appointments)
            else:
                self.logger.debug(f"📅 هیچ نوبتی برای {doctor.name} موجود نیست")
                
        except Exception as e:
            self.logger.error(f"❌ خطا در بررسی {doctor.name}: {e}")
    
        
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
    config = Config()
    db_manager = DatabaseManager(config.database_url)
    hunter = SlotHunter(db_manager)
    try:
        await hunter.start()
    except KeyboardInterrupt:
        await hunter.stop()
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        try:
            asyncio.run(notify_admin_critical_error(f"خطای غیرمنتظره: {e}"))
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())