#!/usr/bin/env python3
"""
Debug ربات تلگرام
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent))

def check_recent_logs():
    """بررسی لاگ‌های اخیر"""
    print("🔍 Checking Recent Logs")
    print("=" * 30)
    
    log_file = Path("logs/slothunter.log")
    
    if not log_file.exists():
        print("❌ Log file not found")
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # آخرین 50 خط
        recent_lines = lines[-50:]
        
        print("📋 Recent log entries:")
        print("-" * 50)
        
        for line in recent_lines:
            line = line.strip()
            if line:
                # رنگ‌بندی بر اساس نوع لاگ
                if "ERROR" in line:
                    print(f"🔴 {line}")
                elif "WARNING" in line:
                    print(f"🟡 {line}")
                elif "INFO" in line:
                    print(f"🔵 {line}")
                else:
                    print(f"⚪ {line}")
        
        print("-" * 50)
        
        # شمارش خطاها
        error_count = sum(1 for line in recent_lines if "ERROR" in line)
        warning_count = sum(1 for line in recent_lines if "WARNING" in line)
        
        print(f"📊 Summary: {error_count} errors, {warning_count} warnings")
        
    except Exception as e:
        print(f"❌ Error reading log file: {e}")

def check_database():
    """بررسی دیتابیس"""
    print("\n💾 Checking Database")
    print("=" * 20)
    
    try:
        from src.utils.config import Config
        from src.database.database import DatabaseManager
        import asyncio
        
        async def check_db():
            config = Config()
            db_manager = DatabaseManager(config.database_url)
            
            try:
                await db_manager._setup_database()
                print("✅ Database connection OK")
                
                # بررسی جداول
                from src.database.models import User, Doctor, Subscription
                
                async with db_manager.session_scope() as session:
                    # شمارش رکوردها
                    from sqlalchemy import select, func
                    
                    user_count = await session.scalar(select(func.count(User.id)))
                    doctor_count = await session.scalar(select(func.count(Doctor.id)))
                    sub_count = await session.scalar(select(func.count(Subscription.id)))
                    
                    print(f"👥 Users: {user_count}")
                    print(f"👨‍⚕️ Doctors: {doctor_count}")
                    print(f"📝 Subscriptions: {sub_count}")
                
                await db_manager.close()
                return True
                
            except Exception as e:
                print(f"❌ Database error: {e}")
                return False
        
        return asyncio.run(check_db())
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def check_handlers():
    """بررسی handlers"""
    print("\n🔧 Checking Handlers")
    print("=" * 20)
    
    try:
        from src.telegram_bot.handlers import TelegramHandlers
        from src.telegram_bot.callback_handlers import TelegramCallbackHandlers
        from src.telegram_bot.admin_handlers import TelegramAdminHandlers
        
        print("✅ TelegramHandlers imported")
        print("✅ TelegramCallbackHandlers imported")
        print("✅ TelegramAdminHandlers imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Handler import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🐛 P24_SlotHunter Debug Tool")
    print("=" * 40)
    
    # بررسی لاگ‌ها
    check_recent_logs()
    
    # بررسی دیتابیس
    db_ok = check_database()
    
    # بررسی handlers
    handlers_ok = check_handlers()
    
    print("\n" + "=" * 40)
    print("📋 Debug Summary:")
    print(f"  💾 Database: {'✅ OK' if db_ok else '❌ Error'}")
    print(f"  🔧 Handlers: {'✅ OK' if handlers_ok else '❌ Error'}")
    
    if not (db_ok and handlers_ok):
        print("\n🔧 Issues found - check the errors above")
    else:
        print("\n✅ Basic components look OK")
        print("💡 Check the recent logs for runtime errors")

if __name__ == "__main__":
    main()