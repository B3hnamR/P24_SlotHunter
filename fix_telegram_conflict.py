#!/usr/bin/env python3
"""
حل مشکل Telegram Conflict
"""
import asyncio
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent))

async def test_telegram_connection():
    """تست اتصال تلگرام"""
    print("🔍 Testing Telegram Connection")
    print("=" * 40)
    
    try:
        from src.utils.config import Config
        from telegram import Bot
        
        config = Config()
        
        if not config.telegram_bot_token:
            print("❌ Bot token not configured")
            return False
        
        print(f"🤖 Bot Token: {config.telegram_bot_token[:10]}...")
        print(f"👤 Admin Chat ID: {config.admin_chat_id}")
        
        # تست اتصال
        bot = Bot(token=config.telegram_bot_token)
        
        print("📡 Testing bot connection...")
        me = await bot.get_me()
        print(f"✅ Bot connected: @{me.username}")
        print(f"📝 Bot name: {me.first_name}")
        
        # تست ا��سال پیام به ادمین
        if config.admin_chat_id:
            try:
                await bot.send_message(
                    chat_id=config.admin_chat_id,
                    text="🧪 Test message from P24_SlotHunter\n\nBot is working correctly!"
                )
                print("✅ Test message sent to admin")
            except Exception as e:
                print(f"⚠️ Could not send test message: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Telegram connection failed: {e}")
        return False

async def check_webhook_status():
    """بررسی وضعیت webhook"""
    print("\n🔗 Checking Webhook Status")
    print("-" * 30)
    
    try:
        from src.utils.config import Config
        from telegram import Bot
        
        config = Config()
        bot = Bot(token=config.telegram_bot_token)
        
        webhook_info = await bot.get_webhook_info()
        
        if webhook_info.url:
            print(f"⚠️ Webhook is set: {webhook_info.url}")
            print("🔧 Removing webhook to use polling...")
            await bot.delete_webhook()
            print("✅ Webhook removed")
        else:
            print("✅ No webhook set (good for polling)")
        
        return True
        
    except Exception as e:
        print(f"❌ Webhook check failed: {e}")
        return False

def check_running_processes():
    """بررسی process های در حال اجرا"""
    print("\n🔍 Checking Running Processes")
    print("-" * 30)
    
    import subprocess
    
    try:
        # جستجوی process های python
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        
        python_processes = []
        for line in result.stdout.split('\n'):
            if 'python' in line and 'P24_SlotHunter' in line:
                python_processes.append(line.strip())
        
        if python_processes:
            print(f"🔍 Found {len(python_processes)} related processes:")
            for i, proc in enumerate(python_processes, 1):
                print(f"  {i}. {proc}")
        else:
            print("✅ No conflicting processes found")
        
        return len(python_processes)
        
    except Exception as e:
        print(f"❌ Process check failed: {e}")
        return 0

async def main():
    print("🔧 P24_SlotHunter Telegram Conflict Resolver")
    print("=" * 50)
    
    # بررسی process ها
    process_count = check_running_processes()
    
    # بررسی webhook
    await check_webhook_status()
    
    # تست اتصال
    connection_ok = await test_telegram_connection()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"  🔍 Running processes: {process_count}")
    print(f"  📡 Telegram connection: {'✅ OK' if connection_ok else '❌ Failed'}")
    
    if connection_ok:
        print("\n🎉 Telegram bot is working correctly!")
        print("\n💡 The conflict error might be temporary.")
        print("   The service should recover automatically.")
    else:
        print("\n❌ Telegram connection issues found")
        print("   Please check bot token and network connection")
    
    print("\n🚀 Service status: Check with './server_manager.sh status'")

if __name__ == "__main__":
    asyncio.run(main())