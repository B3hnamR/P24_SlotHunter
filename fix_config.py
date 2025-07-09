#!/usr/bin/env python3
"""
اصلاح فایل config.yaml برای استفاده از مقادیر واقعی
"""
import os
from pathlib import Path

def fix_config():
    """اصلاح فایل config.yaml"""
    
    # خواندن فایل .env
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ فایل .env یافت نشد")
        return
    
    env_vars = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    print("📋 متغیرهای محیطی یافت شده:")
    for key, value in env_vars.items():
        if 'TOKEN' in key:
            print(f"  {key}: {value[:10]}...")
        else:
            print(f"  {key}: {value}")
    
    # خواندن فایل config.yaml
    config_file = Path("config/config.yaml")
    if not config_file.exists():
        print("❌ فایل config.yaml یافت نشد")
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # جایگزینی متغیرها
    original_content = content
    
    for key, value in env_vars.items():
        placeholder = f"${{{key}}}"
        if placeholder in content:
            content = content.replace(placeholder, value)
            print(f"✅ جایگزین شد: {placeholder} -> {value[:10]}...")
    
    # ذخیره فایل جدید
    if content != original_content:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ فایل config.yaml به‌روزرسانی شد")
    else:
        print("ℹ️ نیازی به تغییر نبود")

if __name__ == "__main__":
    print("🔧 اصلاح فایل config.yaml...")
    fix_config()
    print("🎉 تمام!")