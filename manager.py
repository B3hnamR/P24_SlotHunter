#!/usr/bin/env python3
"""
🎯 P24_SlotHunter Manager
مدیریت کامل پروژه نوبت‌یاب پذیرش۲۴

استفاده:
    python manager.py --help
    python manager.py setup
    python manager.py run
    python manager.py config
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import json


class P24Manager:
    """مدیر کامل پروژه P24_SlotHunter"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.env_file = self.project_root / ".env"
        self.config_file = self.project_root / "config" / "config.yaml"
        
    def print_banner(self):
        """نمایش بنر پروژه"""
        print("=" * 60)
        print("🎯 P24_SlotHunter Manager")
        print("مدیریت کامل پروژه نوبت‌یاب پذیرش��۴")
        print("=" * 60)
    
    def check_python(self):
        """بررسی نسخه Python"""
        if sys.version_info < (3, 9):
            print("❌ Python 3.9+ مورد نیاز است")
            print(f"نسخه فعلی: {sys.version}")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} - مناسب")
        return True
    
    def setup_venv(self):
        """راه‌اندازی Virtual Environment"""
        print("\n🔧 راه‌اندازی Virtual Environment...")
        
        if self.venv_path.exists():
            print("⚠️ Virtual Environment موجود است")
            response = input("آیا می‌خواهید مجدداً ایجاد کنید؟ (y/N): ")
            if response.lower() != 'y':
                return True
            
            # حذف venv قدیمی
            import shutil
            shutil.rmtree(self.venv_path)
        
        try:
            # ایجاد venv
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
            print("✅ Virtual Environment ایجاد شد")
            
            # فعال‌سازی و نصب dependencies
            self.install_dependencies()
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ خطا در ایجاد Virtual Environment: {e}")
            return False
    
    def get_venv_python(self):
        """دریافت مسیر Python در venv"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "python.exe"
        else:  # Linux/Mac
            return self.venv_path / "bin" / "python"
    
    def get_venv_pip(self):
        """دریافت مسیر pip در venv"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "pip.exe"
        else:  # Linux/Mac
            return self.venv_path / "bin" / "pip"
    
    def install_dependencies(self):
        """نصب dependencies"""
        print("\n📦 نصب dependencies...")
        
        if not self.venv_path.exists():
            print("❌ Virtual Environment موجود نیست. ابتدا setup اجرا کنید")
            return False
        
        try:
            pip_path = self.get_venv_pip()
            
            # به‌روزرسانی pip
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
            
            # نصب requirements
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
                print("✅ Dependencies نصب شدند")
            else:
                print("⚠️ فایل requirements.txt یافت نشد")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ خطا در نصب dependencies: {e}")
            return False
    
    def check_dependencies(self):
        """بررسی dependencies"""
        print("\n🔍 بررسی dependencies...")
        
        if not self.venv_path.exists():
            print("❌ Virtual Environment موجود نیست")
            return False
        
        try:
            python_path = self.get_venv_python()
            result = subprocess.run([
                str(python_path), 
                str(self.project_root / "check_dependencies.py")
            ], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print("خطاها:", result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ خطا در بررسی dependencies: {e}")
            return False
    
    def setup_env_file(self):
        """تنظیم فایل .env"""
        print("\n🔧 تن��یم فایل .env...")
        
        if self.env_file.exists():
            print("✅ فایل .env موجود است")
            response = input("آیا می‌خواهید مجدداً تنظیم کنید؟ (y/N): ")
            if response.lower() != 'y':
                return True
        
        print("\n📱 تنظیم ربات تلگرام:")
        print("1. به @BotFather پیام دهید")
        print("2. دستور /newbot را ارسال کنید")
        print("3. نام و username ربات را وارد کنید")
        print("4. توکن دریافتی را در ادامه وارد کنید")
        print()
        
        bot_token = input("🤖 توکن ربات تلگرام: ").strip()
        if not bot_token:
            print("⚠️ بدون توکن، ربات تلگرام کار نخواهد کرد")
            bot_token = ""
        
        print("\n👤 دریافت Chat ID:")
        print("به @userinfobot پیام دهید تا Chat ID خود را دریافت کنید")
        
        chat_id = input("👤 Chat ID شما: ").strip()
        if not chat_id:
            print("⚠️ بدون Chat ID، اطلاع‌رسانی کار نخواهد کرد")
            chat_id = ""
        
        check_interval = input("⏱️ فاصله بررسی (ثانیه) [30]: ").strip() or "30"
        log_level = input("📝 سطح لاگ (DEBUG/INFO/WARNING/ERROR) [INFO]: ").strip() or "INFO"
        
        # ایجاد محتوای .env
        env_content = f"""# متغیرهای محیطی P24_SlotHunter
# این فایل را در git commit نکنید!

# توکن ربات تلگرام (از @BotFather دریافت کنید)
TELEGRAM_BOT_TOKEN={bot_token}

# شناسه چت ادمین (برای دریافت گزارش‌ها)
ADMIN_CHAT_ID={chat_id}

# تنظیمات اختیاری
CHECK_INTERVAL={check_interval}
LOG_LEVEL={log_level}
"""
        
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("✅ فایل .env ایجاد شد")
            return True
        except Exception as e:
            print(f"❌ خطا در ایجاد فایل .env: {e}")
            return False
    
    def test_config(self):
        """تست تنظیمات"""
        print("\n🧪 تست تنظیمات...")
        
        if not self.venv_path.exists():
            print("❌ Virtual Environment موجود نیست")
            return False
        
        try:
            python_path = self.get_venv_python()
            result = subprocess.run([
                str(python_path), 
                str(self.project_root / "test_config.py")
            ], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print("خطاها:", result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ خطا در تست تنظیمات: {e}")
            return False
    
    def test_api(self):
        """تست API"""
        print("\n🧪 تست API پذیرش۲۴...")
        
        if not self.venv_path.exists():
            print("❌ Virtual Environment موجود نیست")
            return False
        
        try:
            python_path = self.get_venv_python()
            result = subprocess.run([
                str(python_path), 
                str(self.project_root / "test_api.py")
            ], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print("خطاها:", result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ خطا در تست API: {e}")
            return False
    
    def run_project(self, mode="full"):
        """اجرا�� پروژه"""
        if mode == "full":
            print("\n🚀 اجرای کامل P24_SlotHunter...")
        else:
            print("\n🚀 اجرای P24_SlotHunter (بدون تلگرام)...")
        
        if not self.venv_path.exists():
            print("❌ Virtual Environment موجود نیست. ابتدا setup اجرا کنید")
            return False
        
        try:
            python_path = self.get_venv_python()
            
            if mode == "full":
                # اجرای کامل با تلگرام
                subprocess.run([str(python_path), str(self.project_root / "src" / "main.py")])
            else:
                # اجرای بدون تلگرام
                subprocess.run([str(python_path), str(self.project_root / "run_without_telegram.py")])
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 برنامه متوقف شد")
            return True
        except Exception as e:
            print(f"❌ خطا در اجرای پروژه: {e}")
            return False
    
    def show_status(self):
        """نمایش وضعیت پروژه"""
        print("\n📊 وضعیت پروژه:")
        
        # بررسی Python
        python_ok = self.check_python()
        
        # بررسی Virtual Environment
        venv_ok = self.venv_path.exists()
        print(f"🐍 Virtual Environment: {'✅ موجود' if venv_ok else '❌ موجود نیست'}")
        
        # بررسی فایل .env
        env_ok = self.env_file.exists()
        print(f"⚙️ فایل .env: {'✅ موجود' if env_ok else '❌ موجود نیست'}")
        
        # بررسی فایل config
        config_ok = self.config_file.exists()
        print(f"📋 فایل config: {'✅ موجود' if config_ok else '❌ موجود نیست'}")
        
        # بررسی پوشه‌ها
        logs_ok = (self.project_root / "logs").exists()
        data_ok = (self.project_root / "data").exists()
        print(f"📁 پوشه logs: {'✅ موجود' if logs_ok else '❌ موجود نیست'}")
        print(f"💾 پوشه data: {'✅ موجود' if data_ok else '❌ موجود نیست'}")
        
        # خلاصه
        all_ok = all([python_ok, venv_ok, env_ok, config_ok, logs_ok, data_ok])
        print(f"\n🎯 وضعیت کلی: {'✅ آماده' if all_ok else '⚠️ نیاز به تنظیم'}")
        
        if not all_ok:
            print("\n💡 برای تنظیم کامل:")
            print("python manager.py setup")
    
    def clean_project(self):
        """پاک‌سازی فایل‌های اضافی"""
        print("\n🧹 پاک‌سازی فایل‌های اضافی...")
        
        # فایل‌های قابل حذف
        files_to_remove = [
            "check_dependencies_safe.py",
            "test_imports.py", 
            "run_without_telegram.py",
            "setup_venv.sh",
            "STATUS.md",
            "TEST_GUIDE.md",
            "TELEGRAM_SETUP.md",
            "run.py"
        ]
        
        removed_count = 0
        for file_name in files_to_remove:
            file_path = self.project_root / file_name
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"🗑️ حذف شد: {file_name}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ خطا در حذف {file_name}: {e}")
        
        print(f"\n✅ {removed_count} فایل اضافی حذف شد")
    
    def setup_complete(self):
        """راه‌اندازی کامل پروژه"""
        self.print_banner()
        
        print("🔧 شروع راه‌اندازی کامل...")
        
        # بررسی Python
        if not self.check_python():
            return False
        
        # ر��ه‌اندازی Virtual Environment
        if not self.setup_venv():
            return False
        
        # بررسی dependencies
        if not self.check_dependencies():
            return False
        
        # تنظیم فایل .env
        if not self.setup_env_file():
            return False
        
        # تست تنظیمات
        if not self.test_config():
            print("⚠️ مشکلی در تنظیمات وجود دارد")
        
        # تست API
        if not self.test_api():
            print("⚠️ مشکلی در API وجود دارد")
        
        print("\n🎉 راه‌اندازی کامل شد!")
        print("\n🚀 برای اجرای پروژه:")
        print("python manager.py run")
        
        return True


def main():
    """تابع اصلی"""
    parser = argparse.ArgumentParser(
        description="🎯 P24_SlotHunter Manager - مدیریت کامل پروژه",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
مثال‌های استفاده:
  python manager.py setup          راه‌اندازی کامل پروژه
  python manager.py run            اجرای کامل پروژه
  python manager.py run --no-telegram    اجرای بدون تلگرام
  python manager.py config         تنظیم مجدد .env
  python manager.py status         نمایش وضعیت
  python manager.py test           تست کامل
  python manager.py clean          پاک‌سازی فایل‌های اضافی
        """
    )
    
    parser.add_argument('command', choices=[
        'setup', 'run', 'config', 'status', 'test', 'clean'
    ], help='دستور مورد نظر')
    
    parser.add_argument('--no-telegram', action='store_true',
                       help='اجرای بدون ربات تلگرام')
    
    args = parser.parse_args()
    
    manager = P24Manager()
    
    try:
        if args.command == 'setup':
            manager.setup_complete()
        
        elif args.command == 'run':
            mode = "simple" if args.no_telegram else "full"
            manager.run_project(mode)
        
        elif args.command == 'config':
            manager.print_banner()
            manager.setup_env_file()
        
        elif args.command == 'status':
            manager.print_banner()
            manager.show_status()
        
        elif args.command == 'test':
            manager.print_banner()
            manager.check_dependencies()
            manager.test_config()
            manager.test_api()
        
        elif args.command == 'clean':
            manager.print_banner()
            manager.clean_project()
    
    except KeyboardInterrupt:
        print("\n🛑 عملیات متوقف شد")
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()