#!/usr/bin/env python3
"""
تست فایل .env
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config

def test_env():
    """تست متغیرهای محیطی"""
    print("🔍 تست فایل .env...")
    
    config = Config()
    
    print(f"📱 Bot Token: {config.telegram_bot_token}")
    print(f"👤 Admin Chat ID: {config.admin_chat_id}")
    print(f"⏱️ Check Interval: {config.check_interval}")
    print(f"📝 Log Level: {config.log_level}")
    
    if config.telegram_bot_token and config.telegram_bot_token != "${TELEGRAM_BOT_TOKEN}":
        print("✅ توکن ربات صحیح است")
    else:
        print("❌ توکن ربات صحیح نیست")
    
    if config.admin_chat_id and config.admin_chat_id != 0:
        print("✅ Chat ID صحیح است")
    else:
        print("❌ Chat ID صحیح نیست")

if __name__ == "__main__":
    test_env()