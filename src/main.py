#!/usr/bin/env python3
"""
فایل اصلی P24_SlotHunter - نسخه بهینه شده برای جلوگیری از Rate Limiting
"""
import asyncio
import signal
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.api.enhanced_paziresh_client import EnhancedPazireshAPI
from src.telegram_bot.bot import SlotHunterBot
from src.database.database import DatabaseManager
from src.database.models import Doctor as DBDoctor, DoctorCenter, DoctorService, Subscription
from src.utils.logger import notify_admin_critical_error
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import httpx

class SlotHunter:
    """کلاس اصلی نوبت‌یاب - نسخه بهینه شده"""
    
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
        self.logger.info("🚀 شروع P24_SlotHunter - نسخه بهینه شده")
        
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
            async with self.db_manager.session_scope() as session:
                db_doctors_count = await session.scalar(select(func.count(DBDoctor.id)))
                active_doctors_count = await session.scalar(
                    select(func.count(DBDoctor.id)).filter(DBDoctor.is_active == True)
                )
                
                if db_doctors_count == 0:
                    self.logger.warning("⚠️ هیچ دکتری در دیتابیس یافت نشد")
                    self.logger.info("💡 دکترها را از طریق ربات تلگرام اضافه کنید")
                else:
                    self.logger.info(f"👨‍⚕️ {db_doctors_count} دکتر در دیتابیس ({active_doctors_count} فعال)")
        except Exception as e:
            self.logger.error(f"❌ خطا در بررسی دکترها: {e}")
        
        self.running = True
        self.http_client = httpx.AsyncClient(timeout=self.config.api_timeout)
        
        # نمایش تنظیمات بهینه سازی
        self.logger.info(f"⚙️ تنظیمات بهینه سازی:")
        self.logger.info(f"   🕐 فاصله بررسی: {self.config.check_interval} ثانیه")
        self.logger.info(f"   📅 روزهای بررسی: {self.config.days_ahead} روز")
        self.logger.info(f"   ⏱️ تاخیر بین درخواست‌ها: {self.config.request_delay} ثانیه")
        
        # شروع همزمان ربات و نظارت
        try:
            await asyncio.gather(
                self.telegram_bot.start_polling(),
                self.monitor_loop()
            )
        finally:
            if self.http_client:
                await self.http_client.aclose()
    
    async def monitor_loop(self):
        """حلقه اصلی نظارت - نسخه بهینه شده"""
        while self.running:
            try:
                # دریافت دکترهای فعال با مراکز و سرویس‌هایشان
                async with self.db_manager.session_scope() as session:
                    result = await session.execute(
                        select(DBDoctor)
                        .options(
                            selectinload(DBDoctor.centers).selectinload(DoctorCenter.services),
                            selectinload(DBDoctor.subscriptions)
                        )
                        .filter(DBDoctor.is_active == True)
                    )
                    active_doctors = result.scalars().all()
                
                if active_doctors:
                    self.logger.info(f"🔍 شروع دور جدید بررسی {len(active_doctors)} دکتر...")
                    
                    # بررسی همه دکترها
                    for doctor in active_doctors:
                        # فقط دکترهایی که مشترک دارند را بررسی کن
                        active_subscriptions = [sub for sub in doctor.subscriptions if sub.is_active]
                        if active_subscriptions:
                            await self.check_doctor(doctor)
                        else:
                            self.logger.debug(f"⏭️ {doctor.name} مشترک ندارد، رد شد")
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
        """بررسی نوبت‌های یک دکتر - نسخه بهینه شده"""
        try:
            if not doctor.centers:
                self.logger.warning(f"⚠️ {doctor.name} هیچ مرکزی ندارد")
                return
            
            # استفاده از API پیشرفته با تنظیمات بهینه
            api = EnhancedPazireshAPI(
                doctor, 
                client=self.http_client,
                timeout=self.config.api_timeout,
                base_url=self.config.api_base_url,
                request_delay=self.config.request_delay
            )
            appointments = await api.get_all_available_appointments(days_ahead=self.config.days_ahead)
            
            if appointments:
                self.logger.info(f"🎯 {len(appointments)} نوبت برای {doctor.name} پیدا شد!")
                
                # نمایش در لاگ
                for apt in appointments[:3]:
                    self.logger.info(f"  ⏰ {apt.time_str}")
                
                # اطلاع‌رسانی با ربات تلگرام
                if self.telegram_bot:
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
        
        if self.http_client:
            await self.http_client.aclose()


def signal_handler(signum, frame):
    """مدیریت سیگنال‌های سیستم - توقف تمیز"""
    print("\n🛑 دریافت سیگنال توقف، در حال توقف...")
    # پرتاب KeyboardInterrupt تا بلاک except در main اجرا شود و hunter.stop() فراخوانی گردد
    raise KeyboardInterrupt()


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
            await notify_admin_critical_error(f"خطای غیرمنتظره: {e}")
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())