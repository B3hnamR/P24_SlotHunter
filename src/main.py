#!/usr/bin/env python3
"""
فایل اصلی P24_SlotHunter
"""
import asyncio
import signal
import sys
from pathlib import Path

# اضافه کردن مسیر src به Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.api.paziresh_client import PazireshAPI
from src.telegram.bot import SlotHunterBot
from src.database.database import init_database, db_session
from src.database.models import Doctor as DBDoctor


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
        
        doctors = self.config.get_doctors()
        if not doctors:
            self.logger.error("❌ هیچ دکتری در تنظیمات یافت نشد")
            return
        
        self.logger.info(f"👨‍⚕️ {len(doctors)} دکتر در حال نظارت:")
        for doctor in doctors:
            if doctor.is_active:
                self.logger.info(f"  ✅ {doctor.name} - {doctor.specialty}")
            else:
                self.logger.info(f"  ⏸️ {doctor.name} - غیرفعال")
        
        self.running = True
        
        # شروع همزمان ربات و نظارت
        await asyncio.gather(
            self.telegram_bot.start_polling(),
            self.monitor_loop()
        )
    
    async def _load_doctors_to_db(self):
        """بارگذاری دکترها در دیتابیس"""
        try:
            config_doctors = self.config.get_doctors()
            
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
    
    async def monitor_loop(self):
        """حلقه اصلی نظارت"""
        active_doctors = [d for d in self.config.get_doctors() if d.is_active]
        
        while self.running:
            try:
                self.logger.info("🔍 شروع دور جدید بررسی...")
                
                # بررسی همه دکترها
                for doctor in active_doctors:
                    await self.check_doctor(doctor)
                
                # صبر تا دور بعدی
                self.logger.info(f"⏰ صبر {self.config.check_interval} ثانیه تا دور بعدی...")
                await asyncio.sleep(self.config.check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("⏹️ دریافت سیگنال توقف...")
                break
            except Exception as e:
                self.logger.error(f"❌ خطا در حلقه نظارت: {e}")
                await asyncio.sleep(60)  # صبر بیشتر در صورت خطا
    
    async def check_doctor(self, doctor):
        """بررسی نوبت‌های یک دکتر"""
        try:
            api = PazireshAPI(doctor, timeout=self.config.api_timeout)
            appointments = api.get_available_appointments(days_ahead=self.config.days_ahead)
            
            if appointments:
                self.logger.info(f"🎯 {len(appointments)} نوبت برای {doctor.name} پیدا شد!")
                
                # اطلاع‌رسانی تلگرام
                await self.notify_appointments(doctor, appointments)
            else:
                self.logger.debug(f"📅 هیچ نوبتی برای {doctor.name} موجود نیست")
                
        except Exception as e:
            self.logger.error(f"❌ خطا در بررسی {doctor.name}: {e}")
    
    async def notify_appointments(self, doctor, appointments):
        """اطلاع‌رسانی نوبت‌های جدید"""
        try:
            if self.telegram_bot:
                await self.telegram_bot.send_appointment_alert(doctor, appointments)
            
            # نمایش در لاگ
            self.logger.info(f"📢 اطلاع‌رسانی {len(appointments)} نوبت برای {doctor.name}")
            for apt in appointments[:3]:
                self.logger.info(f"  ⏰ {apt.time_str}")
                
        except Exception as e:
            self.logger.error(f"❌ خطا در اطلاع‌رسانی: {e}")
    
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