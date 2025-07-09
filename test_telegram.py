#!/usr/bin/env python3
"""
تست ربات تلگرام
"""
import sys
import asyncio
from pathlib import Path

# اضافه کردن مسیر src به Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.telegram.bot import SlotHunterBot
from src.database.database import init_database
from src.api.models import Doctor, Appointment
from datetime import datetime


async def test_telegram_bot():
    """تست ربات تلگرام"""
    
    # تنظیم logger
    logger = setup_logger("TestTelegram", level="INFO")
    
    # بارگذاری تنظیمات
    config = Config()
    
    if not config.telegram_bot_token:
        logger.error("❌ توکن ربات تلگرام تنظیم نشده است")
        logger.info("💡 فایل .env بسازید و TELEGRAM_BOT_TOKEN را تنظیم کنید")
        return
    
    logger.info("🚀 شروع تست ربات تلگرام")
    
    try:
        # راه‌اندازی دیتابیس
        init_database()
        logger.info("✅ دیتابیس راه‌اندازی شد")
        
        # ایجاد ربات
        bot = SlotHunterBot(config.telegram_bot_token)
        await bot.initialize()
        logger.info("✅ ربات تلگرام راه‌اندازی شد")
        
        # تست ارسال پیام نمونه (اگر admin_chat_id تنظیم شده باشد)
        if config.admin_chat_id:
            test_message = """
🧪 **تست ربات P24_SlotHunter**

✅ ربات با موفقیت راه‌اندازی شد!
🔧 تمام سیستم‌ها عملیاتی هستند.

⏰ زمان تست: """ + datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            
            await bot.send_admin_message(test_message, config.admin_chat_id)
            logger.info("✅ پیام تست به ادمین ارسال شد")
        
        # تست پیام اطلاع‌رسانی نوبت (نمونه)
        sample_doctor = Doctor(
            name="دکتر تست",
            slug="test-doctor",
            center_id="test-center",
            service_id="test-service",
            user_center_id="test-user-center",
            terminal_id="test-terminal",
            specialty="تست",
            center_name="مرکز تست",
            center_address="آدرس تست",
            center_phone="09123456789"
        )
        
        sample_appointments = [
            Appointment(
                from_time=int(datetime.now().timestamp()) + 3600,  # 1 ساعت بعد
                to_time=int(datetime.now().timestamp()) + 3900,    # 1 ساعت و 5 دقیقه بعد
                workhour_turn_num=1
            ),
            Appointment(
                from_time=int(datetime.now().timestamp()) + 7200,  # 2 ساعت بعد
                to_time=int(datetime.now().timestamp()) + 7500,    # 2 ساعت و 5 دقیقه بعد
                workhour_turn_num=2
            )
        ]
        
        logger.info("📋 نمونه پیام اطلاع‌رسانی:")
        from src.telegram.messages import MessageFormatter
        sample_message = MessageFormatter.appointment_alert_message(sample_doctor, sample_appointments)
        print("\n" + "="*50)
        print(sample_message)
        print("="*50 + "\n")
        
        # دریافت آمار ربات
        stats = await bot.get_bot_stats()
        logger.info(f"📊 آمار ربات: {stats}")
        
        logger.info("🎉 تست ربات با موفقیت انجام شد!")
        logger.info("💡 حالا می‌توانید ربات را در تلگرام تست کنید:")
        logger.info("   1. به ربات پیام /start بفرستید")
        logger.info("   2. دستور /doctors را امتحان کنید")
        logger.info("   3. از /help برای راهنما استفاده کنید")
        
        # توقف ربات
        await bot.stop()
        
    except Exception as e:
        logger.error(f"❌ خطا در تست ربات: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_telegram_bot())