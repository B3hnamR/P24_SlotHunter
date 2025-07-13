#!/usr/bin/env python3
"""
تست imports برای بررسی حل شدن مشکل
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_all_imports():
    """تست همه imports مهم"""
    print("🔍 Testing All Critical Imports")
    print("=" * 50)
    
    imports_to_test = [
        ("src.utils.config", "Config"),
        ("src.utils.logger", "setup_logger"),
        ("src.api.models", "Doctor"),
        ("src.api.paziresh_client", "PazireshAPI"),
        ("src.database.models", "User"),
        ("src.database.database", "DatabaseManager"),
        ("src.database.database", "db_session"),
        ("src.telegram_bot.bot", "SlotHunterBot"),
    ]
    
    failed_imports = []
    
    for module_name, class_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"❌ {module_name}.{class_name} - {e}")
            failed_imports.append(f"{module_name}.{class_name}")
    
    if failed_imports:
        print(f"\n❌ Failed imports: {len(failed_imports)}")
        for failed in failed_imports:
            print(f"  - {failed}")
        return False
    else:
        print(f"\n✅ All {len(imports_to_test)} imports successful!")
        return True

def test_config_creation():
    """تست ایجاد config"""
    print("\n🔧 Testing Config Creation")
    print("-" * 30)
    
    try:
        from src.utils.config import Config
        config = Config()
        
        print(f"✅ Config created successfully")
        print(f"📱 Bot Token: {'Set' if config.telegram_bot_token else 'Not set'}")
        print(f"👤 Admin Chat ID: {config.admin_chat_id}")
        print(f"🌐 API Base URL: {config.api_base_url}")
        print(f"💾 Database URL: {config.database_url}")
        
        return True
    except Exception as e:
        print(f"❌ Config creation failed: {e}")
        return False

def test_database_manager():
    """تست database manager"""
    print("\n💾 Testing Database Manager")
    print("-" * 30)
    
    try:
        from src.database.database import DatabaseManager
        from src.utils.config import Config
        
        config = Config()
        db_manager = DatabaseManager(config.database_url)
        
        print("✅ DatabaseManager created successfully")
        print(f"📍 Database URL: {db_manager.database_url}")
        
        return True
    except Exception as e:
        print(f"❌ DatabaseManager creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 P24_SlotHunter Import Test Suite")
    print("=" * 60)
    
    success = True
    
    # تست imports
    if not test_all_imports():
        success = False
    
    # تست config
    if not test_config_creation():
        success = False
    
    # تست database
    if not test_database_manager():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! System is ready to start.")
        print("\n🚀 You can now run: ./server_manager.sh start")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    sys.exit(0 if success else 1)