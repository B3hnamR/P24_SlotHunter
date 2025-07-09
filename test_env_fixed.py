#!/usr/bin/env python3
"""
تست فایل .env اصلاح شده
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_env_direct():
    """تست مستقیم فایل .env"""
    print("🔍 تست مستقیم فایل .env...")
    
    # بارگذاری .env
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    admin_chat_id = os.getenv('ADMIN_CHAT_ID')
    check_interval = os.getenv('CHECK_INTERVAL')
    log_level = os.getenv('LOG_LEVEL')
    
    print(f"📱 Bot Token: {bot_token[:10] if bot_token else 'None'}...")
    print(f"👤 Admin Chat ID: {admin_chat_id}")
    print(f"⏱️ Check Interval: {check_interval}")
    print(f"📝 Log Level: {log_level}")
    
    return bot_token, admin_chat_id

def test_config_class():
    """تست کلاس Config"""
    print("\n🔍 تست کلاس Config...")
    
    from src.utils.config import Config
    
    config = Config()
    
    print(f"📱 Bot Token: {config.telegram_bot_token[:10] if config.telegram_bot_token else 'None'}...")
    print(f"👤 Admin Chat ID: {config.admin_chat_id}")
    print(f"⏱️ Check Interval: {config.check_interval}")
    print(f"📝 Log Level: {config.log_level}")
    
    if config.telegram_bot_token and not config.telegram_bot_token.startswith('${'):
        print("✅ توکن ربات صحیح است")
    else:
        print("❌ توکن ربات صحیح نیست")
    
    if config.admin_chat_id and config.admin_chat_id != 0:
        print("✅ Chat ID صحیح است")
    else:
        print("❌ Chat ID صحیح نیست")

if __name__ == "__main__":
    test_env_direct()
    test_config_class()