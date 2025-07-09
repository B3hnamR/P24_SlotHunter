#!/usr/bin/env python3
"""
بررسی وابستگی‌های پروژه
"""
import sys
from pathlib import Path

print("🔍 بررسی وابستگی‌های پروژه...")
print(f"🐍 Python version: {sys.version}")
print()

# لیست کتابخانه‌های مورد نیاز
required_packages = [
    'requests',
    'aiohttp', 
    'telegram',
    'sqlalchemy',
    'yaml',
    'dotenv'
]

missing_packages = []
installed_packages = []

for package in required_packages:
    try:
        if package == 'telegram':
            import telegram
            installed_packages.append(f"✅ python-telegram-bot: {telegram.__version__}")
        elif package == 'yaml':
            import yaml
            installed_packages.append(f"✅ pyyaml: {yaml.__version__}")
        elif package == 'dotenv':
            import dotenv
            try:
                version = dotenv.__version__
            except AttributeError:
                try:
                    # تلاش با pkg_resources
                    import pkg_resources
                    version = pkg_resources.get_distribution('python-dotenv').version
                except:
                    try:
                        # تلاش با importlib.metadata
                        import importlib.metadata
                        version = importlib.metadata.version('python-dotenv')
                    except:
                        version = "نصب شده"
            installed_packages.append(f"✅ python-dotenv: {version}")
        else:
            module = __import__(package)
            version = getattr(module, '__version__', 'نامشخص')
            installed_packages.append(f"✅ {package}: {version}")
    except ImportError:
        missing_packages.append(f"❌ {package}")
    except Exception as e:
        # در صورت هر خطای دیگر
        installed_packages.append(f"⚠️ {package}: نصب شده (خطا در تشخیص نسخه)")

print("📦 وضعیت کتابخانه‌ها:")
for pkg in installed_packages:
    print(f"  {pkg}")

if missing_packages:
    print("\n⚠️ کتابخانه‌های کم:")
    for pkg in missing_packages:
        print(f"  {pkg}")
    print("\n💡 برای نصب:")
    print("pip install -r requirements.txt")
else:
    print("\n🎉 تمام کتابخانه‌ها نصب شده‌اند!")

# بررسی فایل‌های مهم
print("\n📁 بررسی فایل‌ها:")
important_files = [
    '.env',
    'config/config.yaml',
    'logs',
    'data'
]

for file_path in important_files:
    path = Path(file_path)
    if path.exists():
        if path.is_file():
            print(f"  ✅ {file_path} (فایل)")
        else:
            print(f"  ✅ {file_path} (پوشه)")
    else:
        print(f"  ❌ {file_path} (وجود ندارد)")

print("\n🚀 آماده برای تست!")