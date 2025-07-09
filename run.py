#!/usr/bin/env python3
"""
اجرای ساده P24_SlotHunter
"""
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به Python path
sys.path.insert(0, str(Path(__file__).parent))

# اجرای main
if __name__ == "__main__":
    try:
        # تست import ها
        from src.main import main
        import asyncio
        
        print("🚀 شروع P24_SlotHunter...")
        print("برای توقف Ctrl+C را فشار دهید")
        print("-" * 50)
        
        asyncio.run(main())
        
    except ImportError as e:
        print(f"\n❌ خطای import: {e}")
        print("💡 لطفاً ابتدا فایل test_imports.py را اجرا کنید")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 برنامه متوقف شد")
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)