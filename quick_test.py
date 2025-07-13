#!/usr/bin/env python3
"""
تست سریع معماری جدید
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent))

def test_new_architecture():
    """تست معماری جدید"""
    print("🧪 Testing New Architecture")
    print("=" * 30)
    
    try:
        # تست imports
        print("📦 Testing imports...")
        from src.telegram_bot.bot import NewSlotHunterBot
        from src.telegram_bot import SlotHunterBot
        from src.telegram_bot.unified_handlers import UnifiedTelegramHandlers
        from src.utils.config import Config
        from src.database.database import DatabaseManager
        print("✅ All imports successful")
        
        # تست config
        print("⚙️ Testing config...")
        config = Config()
        print(f"✅ Config loaded - Bot token: {'Set' if config.telegram_bot_token else 'Not set'}")
        
        # تست database manager
        print("💾 Testing database...")
        db_manager = DatabaseManager(config.database_url)
        print("✅ Database manager created")
        
        # تست bot creation (بدون initialize)
        print("🤖 Testing bot creation...")
        bot = NewSlotHunterBot(config.telegram_bot_token, db_manager)
        print("✅ Bot instance created")
        
        # تست handlers
        print("🔧 Testing handlers...")
        handlers = UnifiedTelegramHandlers(db_manager)
        print("✅ Handlers created")
        
        print("\n🎉 All tests passed! New architecture is ready.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_architecture()
    if success:
        print("\n🚀 Ready to start service!")
        print("Run: ./server_manager.sh start")
    else:
        print("\n❌ Fix issues before starting service")
    
    sys.exit(0 if success else 1)