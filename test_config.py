#!/usr/bin/env python3
"""
تست تنظیمات پروژه
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_config():
    """تست تنظیمات"""
    print("🔧 تست تنظیمات پروژه...")
    
    try:
        from src.utils.config import Config
        
        # ایجاد config
        config = Config()
        
        print("✅ Config کلاس بارگذاری شد")
        
        # بررسی تنظیمات اصلی
        print(f"📱 Bot Token: {'✅ تنظیم شده' if config.telegram_bot_token else '❌ تنظیم نشده'}")
        print(f"👤 Admin Chat ID: {'✅ تنظیم شده' if config.admin_chat_id else '❌ تنظیم نشده'}")
        print(f"⏱️ Check Interval: {config.check_interval} ثانیه")
        print(f"📅 Days Ahead: {config.days_ahead} روز")
        print(f"📝 Log Level: {config.log_level}")
        
        # بررسی دکترها
        doctors = config.get_doctors()
        print(f"👨‍⚕️ تعداد دکترها: {len(doctors)}")
        
        if doctors:
            print("📋 لیست دکترها:")
            for i, doctor in enumerate(doctors, 1):
                status = "✅ فعال" if doctor.is_active else "⏸️ غیرفعال"
                print(f"  {i}. {doctor.name} - {status}")
        
        print("\n🎉 تنظیمات با موفقیت بارگذاری شد!")
        return True
        
    except Exception as e:
        print(f"❌ خطا در بارگذاری تنظیمات: {e}")
        return False

def test_logger():
    """تست سیستم لاگ"""
    print("\n📝 تست سیستم لاگ...")
    
    try:
        from src.utils.logger import setup_logger
        
        # ایجاد logger
        logger = setup_logger("TestLogger", level="INFO", log_file="logs/test.log")
        
        # تست لاگ‌ها
        logger.info("✅ تست INFO log")
        logger.warning("⚠️ تست WARNING log")
        logger.error("❌ تست ERROR log")
        
        print("✅ Logger با موفقیت تنظیم شد")
        print("📁 لاگ‌ها در پوشه logs ذخیره می‌شوند")
        return True
        
    except Exception as e:
        print(f"❌ خطا در تنظیم logger: {e}")
        return False

def test_database():
    """تست دیتابیس"""
    print("\n💾 تست دیتابیس...")
    
    try:
        from src.database.database import init_database, db_session
        from src.database.models import User, Doctor, Subscription
        
        # راه‌اندازی دیتابیس
        init_database()
        print("✅ دیتابیس راه‌اندازی شد")
        
        # تست session
        with db_session() as session:
            # شمارش جداول
            user_count = session.query(User).count()
            doctor_count = session.query(Doctor).count()
            subscription_count = session.query(Subscription).count()
            
            print(f"👥 کاربران: {user_count}")
            print(f"👨‍⚕️ دکترها: {doctor_count}")
            print(f"📝 اشتراک‌ها: {subscription_count}")
        
        print("✅ دیتابیس آماده است")
        return True
        
    except Exception as e:
        print(f"❌ خطا در دیتابیس: {e}")
        return False

if __name__ == "__main__":
    print("🧪 شروع تست‌های پروژه P24_SlotHunter")
    print("=" * 50)
    
    # اجرای تست‌ها
    config_ok = test_config()
    logger_ok = test_logger()
    db_ok = test_database()
    
    print("\n" + "=" * 50)
    print("📊 خلاصه نتایج:")
    print(f"🔧 Config: {'✅ موفق' if config_ok else '❌ ناموفق'}")
    print(f"📝 Logger: {'✅ موفق' if logger_ok else '❌ ناموفق'}")
    print(f"💾 Database: {'✅ موفق' if db_ok else '❌ ناموفق'}")
    
    if all([config_ok, logger_ok, db_ok]):
        print("\n🎉 همه تست‌ها موفق! پروژه آماده اجرا است.")
    else:
        print("\n⚠️ برخی تست‌ها ناموفق. لطفاً مشکلات را برطرف کنید.")