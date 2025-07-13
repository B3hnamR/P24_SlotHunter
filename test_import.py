#!/usr/bin/env python3
"""
تست import برای بررسی حل شدن circular import
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("🔍 Testing imports...")
    
    # تست import config
    from src.utils.config import Config
    print("✅ Config import successful")
    
    # تست import API
    from src.api.paziresh_client import PazireshAPI
    print("✅ PazireshAPI import successful")
    
    # تست import models
    from src.api.models import Doctor
    print("✅ Doctor model import successful")
    
    # تست ایجاد instance
    config = Config()
    print("✅ Config instance created successfully")
    
    # تست تنظیمات
    print(f"📱 Bot Token: {'✅ Set' if config.telegram_bot_token else '❌ Not set'}")
    print(f"👤 Admin Chat ID: {config.admin_chat_id}")
    print(f"⏱️ Check Interval: {config.check_interval}s")
    
    print("\n🎉 All imports successful! Circular import issue resolved.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)