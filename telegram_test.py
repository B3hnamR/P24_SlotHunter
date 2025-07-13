#!/usr/bin/env python3
"""
تست ساده اتصال تلگرام (باید در virtual environment اجرا شود)
"""
import asyncio
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent))

async def simple_telegram_test():
    """تست ساده تلگرام"""
    print("🔍 Simple Telegram Test")
    print("=" * 30)
    
    try:
        # بررسی modules
        print("📦 Checking modules...")
        
        try:
            import httpx
            print("✅ httpx available")
        except ImportError:
            print("❌ httpx not available")
            print("💡 Make sure virtual environment is activated:")
            print("   source venv/bin/activate")
            return False
        
        try:
            from src.utils.config import Config
            print("✅ Config available")
        except ImportError as e:
            print(f"❌ Config import failed: {e}")
            return False
        
        # تست config
        config = Config()
        print(f"🤖 Bot Token: {'✅ Set' if config.telegram_bot_token else '❌ Not set'}")
        print(f"👤 Admin Chat ID: {config.admin_chat_id}")
        
        if not config.telegram_bot_token:
            print("❌ Bot token not configured")
            return False
        
        # تست API مستقیم
        print("\n📡 Testing Telegram API...")
        
        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/getMe"
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data['result']
                    print(f"✅ Bot: @{bot_info.get('username', 'unknown')}")
                    print(f"📝 Name: {bot_info.get('first_name', 'unknown')}")
                    return True
                else:
                    print(f"❌ API Error: {data.get('description', 'Unknown')}")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_webhook():
    """بررسی webhook"""
    print("\n🔗 Checking Webhook...")
    
    try:
        from src.utils.config import Config
        import httpx
        
        config = Config()
        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/getWebhookInfo"
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    webhook_info = data['result']
                    webhook_url = webhook_info.get('url', '')
                    
                    if webhook_url:
                        print(f"⚠️ Webhook set: {webhook_url}")
                        print("🔧 Removing webhook...")
                        
                        # حذف webhook
                        delete_url = f"https://api.telegram.org/bot{config.telegram_bot_token}/deleteWebhook"
                        delete_response = await client.post(delete_url)
                        
                        if delete_response.status_code == 200:
                            print("✅ Webhook removed")
                        else:
                            print("❌ Failed to remove webhook")
                    else:
                        print("✅ No webhook set (good for polling)")
                    
                    return True
        
        return False
        
    except Exception as e:
        print(f"❌ Webhook check failed: {e}")
        return False

def check_environment():
    """بررسی محیط"""
    print("🔍 Environment Check")
    print("-" * 20)
    
    # بررسی virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment active")
    else:
        print("❌ Virtual environment not active")
        print("💡 Run: source venv/bin/activate")
        return False
    
    # بررسی Python version
    print(f"🐍 Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    return True

async def main():
    print("🧪 P24_SlotHunter Telegram Test")
    print("=" * 40)
    
    # بررسی محیط
    if not check_environment():
        return
    
    # تست تلگرام
    telegram_ok = await simple_telegram_test()
    
    # بررسی webhook
    if telegram_ok:
        await check_webhook()
    
    print("\n" + "=" * 40)
    if telegram_ok:
        print("🎉 Telegram connection is working!")
        print("\n💡 The conflict error in logs is likely temporary")
        print("   and should resolve automatically.")
    else:
        print("❌ Telegram connection issues")
        print("\n🔧 Troubleshooting:")
        print("1. Check bot token in .env file")
        print("2. Ensure virtual environment is active")
        print("3. Check internet connection")

if __name__ == "__main__":
    asyncio.run(main())