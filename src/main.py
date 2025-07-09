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


class SlotHunter:
    """کلاس اصلی نوبت‌یاب"""
    
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger(
            level=self.config.log_level,
            log_file=self.config.log_file
        )
        self.running = False
        
    async def start(self):
        """شروع نوبت‌یاب"""
        self.logger.info("🚀 شروع P24_SlotHunter")
        
        # بررسی تنظیمات
        if not self.config.telegram_bot_token:
            self.logger.error("❌ توکن ربات تلگرام تنظیم نشده است")
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
        
        # شروع حلقه نظارت
        await self.monitor_loop()
    
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
                
                # اینجا باید اطلاع‌رسانی تلگرام اضافه شود
                await self.notify_appointments(doctor, appointments)
            else:
                self.logger.debug(f"📅 هیچ نوبتی برای {doctor.name} موجود نیست")
                
        except Exception as e:
            self.logger.error(f"❌ خطا در بررسی {doctor.name}: {e}")
    
    async def notify_appointments(self, doctor, appointments):
        """اطلاع‌رسانی نوبت‌های جدید"""
        # TODO: پیاده‌سازی ربات ��لگرام
        self.logger.info(f"📢 اطلاع‌رسانی {len(appointments)} نوبت برای {doctor.name}")
        
        # نمایش چند نوبت اول
        for apt in appointments[:3]:
            self.logger.info(f"  ⏰ {apt.time_str}")
    
    def stop(self):
        """توقف نوبت‌یاب"""
        self.logger.info("🛑 در حال توقف...")
        self.running = False


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
        hunter.stop()
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")


if __name__ == "__main__":
    asyncio.run(main())