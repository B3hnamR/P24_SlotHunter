#!/usr/bin/env python3
"""
تست نهایی برای بررسی آمادگی سیستم
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_system():
    print("🔍 Final System Test")
    print("=" * 50)
    
    try:
        # تست imports
        print("📦 Testing imports...")
        from src.utils.config import Config
        from src.api.paziresh_client import PazireshAPI
        from src.api.models import Doctor
        from src.database.models import User, Doctor as DBDoctor
        from src.telegram_bot.bot import SlotHunterBot
        print("✅ All imports successful")
        
        # تست config
        print("\n⚙️ Testing configuration...")
        config = Config()
        print(f"📱 Bot Token: {'✅ Set' if config.telegram_bot_token else '❌ Not set'}")
        print(f"👤 Admin Chat ID: {config.admin_chat_id}")
        print(f"⏱️ Check Interval: {config.check_interval}s")
        print(f"🌐 API Base URL: {config.api_base_url}")
        print(f"💾 Database URL: {config.database_url}")
        
        # بررسی تنظیمات ضروری
        issues = []
        if not config.telegram_bot_token:
            issues.append("❌ TELEGRAM_BOT_TOKEN not set")
        if config.admin_chat_id == 0:
            issues.append("❌ ADMIN_CHAT_ID not set")
            
        if issues:
            print("\n⚠️ Configuration Issues:")
            for issue in issues:
                print(f"  {issue}")
            print("\n💡 Please check your .env file")
        else:
            print("✅ Configuration looks good")
        
        # تست ایجاد API client
        print("\n🔌 Testing API client...")
        if config.get_doctors():
            doctor = config.get_doctors()[0]
            api = PazireshAPI(doctor, base_url=config.api_base_url)
            print("✅ API client created successfully")
        else:
            print("ℹ️ No doctors configured (this is normal for initial setup)")
        
        print("\n" + "=" * 50)
        if not issues:
            print("🎉 System is ready to start!")
            print("\n�� Next step: Run './server_manager.sh start'")
        else:
            print("🔧 Please fix configuration issues first")
            
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)