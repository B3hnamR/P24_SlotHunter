#!/usr/bin/env python3
"""
تست import های پروژه
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """تست تمام import های اصلی"""
    print("🔍 تست import های پروژه...")
    
    try:
        print("📦 تست utils...")
        from src.utils.config import Config
        from src.utils.logger import setup_logger
        print("  ✅ utils - موفق")
        
        print("📦 تست api...")
        from src.api.models import Doctor, Appointment
        from src.api.paziresh_client import PazireshAPI
        print("  ✅ api - موفق")
        
        print("📦 تست database...")
        from src.database.models import User, Doctor as DBDoctor, Subscription
        from src.database.database import init_database, db_session
        print("  ✅ database - موفق")
        
        print("📦 تست telegram...")
        from src.telegram.bot import SlotHunterBot
        from src.telegram.handlers import TelegramHandlers
        from src.telegram.messages import MessageFormatter
        print("  ✅ telegram - موفق")
        
        print("📦 تست main...")
        from src.main import SlotHunter
        print("  ✅ main - موفق")
        
        print("\n🎉 تمام import ها موفق بودند!")
        return True
        
    except ImportError as e:
        print(f"\n❌ خطای import: {e}")
        return False
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🚀 پروژه آماده اجرا است!")
    else:
        print("\n⚠️ مشکلی در import ها وجود دارد.")
        sys.exit(1)