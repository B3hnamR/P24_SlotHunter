#!/usr/bin/env python3
"""
تست import main.py برای بررسی حل شدن مشکل
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_main_imports():
    """تست imports که در main.py استفاده می‌شوند"""
    print("🔍 Testing Main.py Imports")
    print("=" * 40)
    
    try:
        print("📦 Testing src.utils.config...")
        from src.utils.config import Config
        print("✅ Config imported")
        
        print("📦 Testing src.utils.logger...")
        from src.utils.logger import setup_logger
        print("✅ setup_logger imported")
        
        print("📦 Testing src.api.paziresh_client...")
        from src.api.paziresh_client import PazireshAPI
        print("✅ PazireshAPI imported")
        
        print("📦 Testing src.telegram_bot.bot...")
        from src.telegram_bot.bot import SlotHunterBot
        print("✅ SlotHunterBot imported")
        
        print("📦 Testing src.database.database...")
        from src.database.database import db_session, DatabaseManager
        print("✅ db_session and DatabaseManager imported")
        
        print("📦 Testing src.database.models...")
        from src.database.models import Doctor as DBDoctor
        print("✅ DBDoctor imported")
        
        print("📦 Testing src.utils.logger notify function...")
        from src.utils.logger import notify_admin_critical_error
        print("✅ notify_admin_critical_error imported")
        
        print("\n🎉 All main.py imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_instance():
    """تست ایجاد instance های اصلی"""
    print("\n🔧 Testing Instance Creation")
    print("-" * 30)
    
    try:
        from src.utils.config import Config
        from src.database.database import DatabaseManager
        
        # تست config
        config = Config()
        print("✅ Config instance created")
        
        # تست database manager
        db_manager = DatabaseManager(config.database_url)
        print("✅ DatabaseManager instance created")
        
        print(f"\n📋 Configuration Summary:")
        print(f"  📱 Bot Token: {'✅ Set' if config.telegram_bot_token else '❌ Not set'}")
        print(f"  👤 Admin Chat ID: {config.admin_chat_id}")
        print(f"  ⏱️ Check Interval: {config.check_interval}s")
        print(f"  💾 Database: {config.database_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Instance creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Main Import Test")
    print("=" * 50)
    
    success = True
    
    if not test_main_imports():
        success = False
    
    if not test_config_instance():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Main imports are working!")
        print("🚀 Ready to start the service")
    else:
        print("❌ Import issues found")
    
    sys.exit(0 if success else 1)