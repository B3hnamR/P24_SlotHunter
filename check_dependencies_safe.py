#!/usr/bin/env python3
"""
بررسی ایمن وابستگی‌های پروژه
"""
import sys
import importlib
from pathlib import Path

def get_package_version(package_name, import_name=None):
    """دریافت ایمن نسخه کتابخانه"""
    if import_name is None:
        import_name = package_name
    
    try:
        # تلاش برای import
        module = importlib.import_module(import_name)
        
        # تلاش برای دریافت version
        if hasattr(module, '__version__'):
            return module.__version__
        
        # تلاش با pkg_resources
        try:
            import pkg_resources
            return pkg_resources.get_distribution(package_name).version
        except:
            pass
        
        # تلاش با importlib.metadata (Python 3.8+)
        try:
            import importlib.metadata
            return importlib.metadata.version(package_name)
        except:
            pass
        
        return "نصب شده (نسخه نامشخص)"
        
    except ImportError:
        return None

def main():
    print("🔍 بررسی وابستگی‌های پروژه P24_SlotHunter...")
    print(f"🐍 Python version: {sys.version}")
    print()

    # لیست کتابخانه‌های مورد نیاز
    required_packages = [
        ('requests', 'requests'),
        ('aiohttp', 'aiohttp'), 
        ('python-telegram-bot', 'telegram'),
        ('sqlalchemy', 'sqlalchemy'),
        ('pyyaml', 'yaml'),
        ('python-dotenv', 'dotenv')
    ]

    installed_packages = []
    missing_packages = []

    print("📦 بررسی کتابخانه‌ها...")
    
    for package_name, import_name in required_packages:
        version = get_package_version(package_name, import_name)
        
        if version:
            installed_packages.append(f"✅ {package_name}: {version}")
        else:
            missing_packages.append(f"❌ {package_name}")

    # نمایش نتایج
    if installed_packages:
        print("\n✅ کتابخانه‌های نصب شده:")
        for pkg in installed_packages:
            print(f"  {pkg}")

    if missing_packages:
        print("\n❌ کتابخانه‌های کم:")
        for pkg in missing_packages:
            print(f"  {pkg}")
        print("\n💡 برای نصب:")
        print("pip install -r requirements.txt")
    else:
        print("\n🎉 تمام کتابخانه‌ها نصب شده‌اند!")

    # بررسی فایل‌های مهم
    print("\n📁 بررسی فایل‌ها:")
    important_files = [
        ('.env', 'فایل تنظیمات محیطی'),
        ('config/config.yaml', 'فایل تنظیمات اصلی'),
        ('logs', 'پوشه لاگ‌ها'),
        ('data', 'پوشه دیتابیس'),
        ('src', 'پوشه کد منبع'),
        ('requirements.txt', 'فایل dependencies')
    ]

    for file_path, description in important_files:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                print(f"  ✅ {file_path} ({description}) - فایل")
            else:
                print(f"  ✅ {file_path} ({description}) - پوشه")
        else:
            print(f"  ❌ {file_path} ({description}) - وجود ندارد")

    # بررسی Python version
    print(f"\n🐍 بررسی نسخه Python:")
    if sys.version_info >= (3, 9):
        print(f"  ✅ Python {sys.version_info.major}.{sys.version_info.minor} - مناسب")
    else:
        print(f"  ⚠️ Python {sys.version_info.major}.{sys.version_info.minor} - نسخه 3.9+ توصیه می‌شود")

    # خلاصه نهایی
    print("\n" + "="*50)
    total_packages = len(required_packages)
    installed_count = len(installed_packages)
    
    if missing_packages:
        print(f"⚠️ وضعیت: {installed_count}/{total_packages} کتابخانه نصب شده")
        print("🔧 اقدام مورد نیاز: نصب کتابخانه‌های کم")
    else:
        print("🎉 وضعیت: همه چیز آماده!")
        print("🚀 می‌توانید تست‌ها را شروع کنید")

if __name__ == "__main__":
    main()