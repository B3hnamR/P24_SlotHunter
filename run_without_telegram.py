#!/usr/bin/env python3
"""
اجرای P24_SlotHunter بدون ربات تلگرام (فقط API monitoring)
"""
import sys
import asyncio
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.api.paziresh_client import PazireshAPI
from src.database.database import init_database, db_session
from src.database.models import Doctor as DBDoctor


class SimpleSlotHunter:
    """نسخه ساده نوبت‌یاب بدون تلگرام"""
    
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger(
            level=self.config.log_level,
            log_file=self.config.log_file
        )
        self.running = False
        
    async def start(self):
        """شروع نوبت‌یاب ساده"""
        self.logger.info("🚀 شروع Simple P24_SlotHunter (بدون تلگرام)")
        
        # راه‌اندازی دیتابیس
        try:
            init_database()
            self.logger.info("✅ دیتابیس راه‌اندازی شد")
        except Exception as e:
            self.logger.error(f"❌ خطا در راه‌اندازی دیتابیس: {e}")
            return
        
        # بارگذاری دکترها در دیتابیس
        await self._load_doctors_to_db()
        
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
        
        # شروع نظارت
        await self.monitor_loop()
    
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
                
                # نمایش جزئیات در لاگ
                self.logger.info(f"📢 جزئیات نوبت‌های {doctor.name}:")
                
                # گروه‌بندی بر اساس تاریخ
                dates_dict = {}
                for apt in appointments:
                    date_str = apt.start_datetime.strftime('%Y/%m/%d')
                    if date_str not in dates_dict:
                        dates_dict[date_str] = []
                    dates_dict[date_str].append(apt)
                
                # نمایش نوبت‌ها
                for date_str, date_appointments in sorted(dates_dict.items()):
                    self.logger.info(f"  📅 {date_str}: {len(date_appointments)} نوبت")
                    for apt in date_appointments[:3]:  # نمایش 3 نوبت اول
                        time_str = apt.start_datetime.strftime('%H:%M')
                        self.logger.info(f"    ⏰ {time_str} (نوبت #{apt.workhour_turn_num})")
                    if len(date_appointments) > 3:
                        self.logger.info(f"    ... و {len(date_appointments) - 3} نوبت دیگر")
                
                # لینک رزرو
                self.logger.info(f"🔗 لینک رزرو: https://www.paziresh24.com/dr/{doctor.slug}/")
                
            else:
                self.logger.debug(f"📅 هیچ نوبتی برای {doctor.name} موجود نیست")
                
        except Exception as e:
            self.logger.error(f"❌ خطا در بررسی {doctor.name}: {e}")
    
    async def stop(self):
        """توقف نوبت‌یاب"""
        self.logger.info("🛑 در حال توقف...")
        self.running = False


async def main():
    """تابع اصلی"""
    hunter = SimpleSlotHunter()
    try:
        await hunter.start()
    except KeyboardInterrupt:
        await hunter.stop()
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")


if __name__ == "__main__":
    print("🚀 شروع Simple P24_SlotHunter...")
    print("📝 این نسخه بدون ربات تلگرام کار می‌کند")
    print("🔍 فقط نوبت‌ها را پیدا کرده و در لاگ نمایش می‌دهد")
    print("برای توقف Ctrl+C را فشار دهید")
    print("-" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 برنامه متوقف شد")
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        sys.exit(1)