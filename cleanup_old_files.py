#!/usr/bin/env python3
"""
پاک‌سازی فایل‌های قدیمی و اضافی
"""
import os
import shutil
from pathlib import Path

def cleanup_project():
    """پاک‌سازی پروژه"""
    project_root = Path(__file__).parent
    
    print("🧹 شروع پاک‌سازی فایل‌های اضافی...")
    
    # فایل‌های قابل حذف
    files_to_remove = [
        "check_dependencies_safe.py",
        "test_imports.py", 
        "run_without_telegram.py",
        "setup_venv.sh",
        "STATUS.md",
        "TEST_GUIDE.md",
        "TELEGRAM_SETUP.md",
        "run.py",
        "cleanup_old_files.py"  # خودش را هم حذف کند
    ]
    
    # پوشه‌های قابل حذف
    dirs_to_remove = [
        "src/telegram"  # پوشه قدیمی telegram
    ]
    
    removed_count = 0
    
    # حذف فایل‌ها
    for file_name in files_to_remove:
        file_path = project_root / file_name
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"🗑️ فایل حذف شد: {file_name}")
                removed_count += 1
            except Exception as e:
                print(f"❌ خطا در حذف {file_name}: {e}")
    
    # حذف پوشه‌ها
    for dir_name in dirs_to_remove:
        dir_path = project_root / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"🗑️ پوشه حذف شد: {dir_name}")
                removed_count += 1
            except Exception as e:
                print(f"❌ خطا در حذف {dir_name}: {e}")
    
    # executable کردن فایل p24
    p24_file = project_root / "p24"
    if p24_file.exists():
        try:
            os.chmod(p24_file, 0o755)
            print("✅ فایل p24 executable شد")
        except Exception as e:
            print(f"⚠️ خطا در executable کردن p24: {e}")
    
    print(f"\n✅ پاک‌سازی تمام شد! {removed_count} آیتم حذف شد")
    print("\n🚀 حالا می‌توانید از دستورات زیر استفاده کنید:")
    print("python manager.py setup")
    print("python manager.py run")
    print("./p24 run")

if __name__ == "__main__":
    cleanup_project()