#!/usr/bin/env python3
"""
پاک‌سازی و سازماندهی فایل‌های roadmap
"""
import os
from pathlib import Path

def cleanup_roadmap_files():
    """حذف فایل‌های roadmap قدیمی"""
    
    # فایل‌های قابل حذف
    files_to_remove = [
        "ROADMAP_COMMERCIAL.md",
        "ROADMAP_TECHNICAL.md", 
        "ROADMAP_SUMMARY.md",
        "NEW_FEATURES.md"
    ]
    
    print("🗑️ حذف فایل‌های roadmap قدیمی...")
    
    removed_count = 0
    for file_name in files_to_remove:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"  ✅ حذف شد: {file_name}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ خطا در حذف {file_name}: {e}")
        else:
            print(f"  ⚠️ یافت نشد: {file_name}")
    
    print(f"\n📊 خلاصه:")
    print(f"  🗑️ فایل‌های حذف شده: {removed_count}")
    print(f"  📁 فایل‌های جدید: docs/roadmap/")
    print(f"  📋 ساختار جدید:")
    print(f"    - docs/roadmap/SUMMARY.md")
    print(f"    - docs/roadmap/COMMERCIAL.md") 
    print(f"    - docs/roadmap/TECHNICAL.md")
    print(f"    - docs/roadmap/FEATURES.md")
    
    print(f"\n✅ سازماندهی roadmap تمام شد!")

if __name__ == "__main__":
    cleanup_roadmap_files()