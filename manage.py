#!/usr/bin/env python3
"""
اسکریپت مدیریت P24_SlotHunter
مدیریت کامل ربات روی سرور لینوکس
"""
import os
import sys
import json
import time
import signal
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class Colors:
    """رنگ‌های terminal"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class SlotHunterManager:
    """مدیر اصلی P24_SlotHunter"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.pid_file = self.project_dir / "slothunter.pid"
        self.log_file = self.project_dir / "logs" / "slothunter.log"
        self.env_file = self.project_dir / ".env"
        self.config_file = self.project_dir / "config" / "config.yaml"
        
        # ایجاد پوشه‌های مورد نیاز
        (self.project_dir / "logs").mkdir(exist_ok=True)
        (self.project_dir / "data").mkdir(exist_ok=True)
    
    def print_header(self):
        """نمایش header"""
        print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    P24_SlotHunter Manager                    ║
║                  ربات نوبت‌گیری پذیرش۲۴                    ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}""")
    
    def print_menu(self):
        """نمایش منوی اصلی"""
        print(f"""
{Colors.BOLD}📋 منوی مدیریت:{Colors.END}

{Colors.GREEN}1.{Colors.END} 🚀 راه‌اندازی اولیه (Setup)
{Colors.GREEN}2.{Colors.END} ▶️  شروع ربات (Start)
{Colors.GREEN}3.{Colors.END} ⏹️  توقف ربات (Stop)
{Colors.GREEN}4.{Colors.END} 🔄 ری‌استارت ربات (Restart)
{Colors.GREEN}5.{Colors.END} 📊 وضعیت ربات (Status)
{Colors.GREEN}6.{Colors.END} 📈 مانیتورینگ (Monitor)
{Colors.GREEN}7.{Colors.END} 📋 مشاهده لاگ‌ها (Logs)
{Colors.GREEN}8.{Colors.END} ⚙️  تنظیمات (Settings)
{Colors.GREEN}9.{Colors.END} 🧹 پاک‌سازی (Cleanup)
{Colors.GREEN}0.{Colors.END} 🚪 خروج (Exit)

{Colors.YELLOW}انتخاب کنید:{Colors.END} """, end="")
    
    def setup(self):
        """راه‌اندازی اولیه"""
        print(f"\n{Colors.BOLD}🚀 راه‌اندازی اولیه P24_SlotHunter{Colors.END}\n")
        
        # بررسی Python
        if sys.version_info < (3, 9):
            print(f"{Colors.RED}❌ Python 3.9+ مورد نیاز است. نسخه فعلی: {sys.version}{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}✅ Python {sys.version.split()[0]} تایید شد{Colors.END}")
        
        # نصب dependencies
        print(f"\n{Colors.BLUE}📦 نصب کتابخانه‌های مورد نیاز...{Colors.END}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True)
            print(f"{Colors.GREEN}✅ کتابخانه‌ها نصب شدند{Colors.END}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ خطا در نصب کتابخانه‌ها: {e}{Colors.END}")
            return False
        
        # تنظیم متغیرهای محیطی
        if not self.setup_environment():
            return False
        
        # تنظیم دکترها
        if not self.setup_doctors():
            return False
        
        # تست اتصال
        if not self.test_connection():
            return False
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 راه‌اندازی با موفقیت انجام شد!{Colors.END}")
        print(f"{Colors.CYAN}💡 حالا می‌توانید با گزینه 2 ربات را شروع کنید.{Colors.END}")
        return True
    
    def setup_environment(self) -> bool:
        """تنظیم متغیرهای محیطی"""
        print(f"\n{Colors.BLUE}⚙️ تنظیم متغیرهای محیطی{Colors.END}")
        
        # خواندن تنظیمات فعلی
        current_env = {}
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        current_env[key] = value
        
        # دریافت توکن ربات
        bot_token = current_env.get('TELEGRAM_BOT_TOKEN', '')
        if not bot_token:
            print(f"\n{Colors.YELLOW}🤖 تنظیم ربات تلگرام:{Colors.END}")
            print("1. به @BotFather در تلگرام پیام دهید")
            print("2. دستور /newbot را بفرستید")
            print("3. نام و username ربات را انتخاب کنید")
            print("4. توکن دریافتی را وارد کنید")
            
            while True:
                bot_token = input(f"\n{Colors.CYAN}توکن ربات تلگرام: {Colors.END}").strip()
                if bot_token and len(bot_token) > 40:
                    break
                print(f"{Colors.RED}❌ توکن نامعتبر است. دوباره تلاش کنید.{Colors.END}")
        
        # دریافت Chat ID ادمین
        admin_chat_id = current_env.get('ADMIN_CHAT_ID', '')
        if not admin_chat_id:
            print(f"\n{Colors.YELLOW}👤 تنظیم ادمین:{Colors.END}")
            print("1. به @userinfobot در تلگرام پیام دهید")
            print("2. شناسه خود را دریافت کنید")
            print("3. شناسه را وارد کنید")
            
            while True:
                admin_chat_id = input(f"\n{Colors.CYAN}شناسه چت ادمین: {Colors.END}").strip()
                if admin_chat_id and admin_chat_id.isdigit():
                    break
                print(f"{Colors.RED}❌ شناسه نامعتبر است. باید عدد باشد.{Colors.END}")
        
        # دریافت تنظیمات اختیاری
        check_interval = current_env.get('CHECK_INTERVAL', '30')
        check_interval = input(f"\n{Colors.CYAN}فاصله بررسی (ثانیه) [{check_interval}]: {Colors.END}").strip() or check_interval
        
        log_level = current_env.get('LOG_LEVEL', 'INFO')
        print(f"\n{Colors.CYAN}سطح لاگ:{Colors.END}")
        print("1. DEBUG (جزئیات کامل)")
        print("2. INFO (عادی)")
        print("3. WARNING (فقط هشدارها)")
        print("4. ERROR (فقط خطاها)")
        
        level_choice = input(f"انتخاب [2]: ").strip() or "2"
        log_levels = {"1": "DEBUG", "2": "INFO", "3": "WARNING", "4": "ERROR"}
        log_level = log_levels.get(level_choice, "INFO")
        
        # ذخیره در فایل .env
        env_content = f"""# متغیرهای محیطی P24_SlotHunter
# تولید شده در: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# توکن ربات تلگرام
TELEGRAM_BOT_TOKEN={bot_token}

# شناسه چت ادمین
ADMIN_CHAT_ID={admin_chat_id}

# تنظیمات عملکرد
CHECK_INTERVAL={check_interval}
LOG_LEVEL={log_level}
"""
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        print(f"{Colors.GREEN}✅ متغیرهای محیطی ذخیره شدند{Colors.END}")
        return True
    
    def setup_doctors(self) -> bool:
        """تنظیم دکترها"""
        print(f"\n{Colors.BLUE}👨‍⚕️ تنظیم دکترها{Colors.END}")
        
        # بررسی وجود تنظیمات فعلی
        if self.config_file.exists():
            choice = input(f"{Colors.YELLOW}فایل تنظیمات موجود است. آیا می‌خواهید دکتر جدید اضافه کنید؟ (y/N): {Colors.END}").strip().lower()
            if choice != 'y':
                print(f"{Colors.CYAN}💡 از تنظیمات موجود استفاده می‌شود.{Colors.END}")
                return True
        
        print(f"\n{Colors.CYAN}💡 برای افزودن دکتر جدید، اطلاعات زیر را از Network tab مرورگر دریافت کنید:{Colors.END}")
        print("1. به صفحه دکتر در پذیرش۲۴ بروید")
        print("2. F12 را فشار دهید و Network tab را باز کنید")
        print("3. روی 'دریافت نوبت' کلیک کنید")
        print("4. درخواست getFreeDays را پیدا کنید")
        print("5. اطلاعات مورد نیاز را کپی کنید")
        
        input(f"\n{Colors.YELLOW}آماده هستید؟ Enter را فشار دهید...{Colors.END}")
        
        # دریافت اطلاعات دکتر
        doctor_name = input(f"\n{Colors.CYAN}نام دکتر: {Colors.END}").strip()
        doctor_slug = input(f"{Colors.CYAN}Slug دکتر (از URL): {Colors.END}").strip()
        center_id = input(f"{Colors.CYAN}Center ID: {Colors.END}").strip()
        service_id = input(f"{Colors.CYAN}Service ID: {Colors.END}").strip()
        user_center_id = input(f"{Colors.CYAN}User Center ID: {Colors.END}").strip()
        terminal_id = input(f"{Colors.CYAN}Terminal ID: {Colors.END}").strip()
        specialty = input(f"{Colors.CYAN}تخصص: {Colors.END}").strip()
        center_name = input(f"{Colors.CYAN}نام مرکز: {Colors.END}").strip()
        center_address = input(f"{Colors.CYAN}آدرس مرکز: {Colors.END}").strip()
        center_phone = input(f"{Colors.CYAN}تلفن مرکز: {Colors.END}").strip()
        
        # ایجاد فایل config
        config_content = f"""# تنظیمات P24_SlotHunter
# تولید شده در: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# تنظیمات ربات تلگرام
telegram:
  bot_token: "${{TELEGRAM_BOT_TOKEN}}"
  admin_chat_id: "${{ADMIN_CHAT_ID}}"

# تنظیمات نظارت
monitoring:
  check_interval: 30
  max_retries: 3
  timeout: 10
  days_ahead: 7

# تنظیمات لاگ
logging:
  level: INFO
  file: logs/slothunter.log
  max_size: 10MB
  backup_count: 5

# لیست دکترها
doctors:
  - name: "{doctor_name}"
    slug: "{doctor_slug}"
    center_id: "{center_id}"
    service_id: "{service_id}"
    user_center_id: "{user_center_id}"
    terminal_id: "{terminal_id}"
    specialty: "{specialty}"
    center_name: "{center_name}"
    center_address: "{center_address}"
    center_phone: "{center_phone}"
    is_active: true
"""
        
        # ایجاد پوشه config
        self.config_file.parent.mkdir(exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"{Colors.GREEN}✅ تنظیمات دکتر ذخیره شد{Colors.END}")
        return True
    
    def test_connection(self) -> bool:
        """تست اتصال"""
        print(f"\n{Colors.BLUE}🧪 تست اتصال...{Colors.END}")
        
        try:
            # تست API
            result = subprocess.run([sys.executable, "test_api.py"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ تست API موفق{Colors.END}")
            else:
                print(f"{Colors.RED}❌ تست API ناموفق: {result.stderr}{Colors.END}")
                return False
            
            # تست ربات تلگرام
            result = subprocess.run([sys.executable, "test_telegram.py"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ تست ربات تلگرام موفق{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️ تست ربات تلگرام: {result.stderr}{Colors.END}")
                print(f"{Colors.CYAN}💡 ربات ممکن است کار کند، اما تست کامل نشد.{Colors.END}")
            
            return True
            
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}❌ تست به دلیل timeout ناموفق بود{Colors.END}")
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ خطا در تست: {e}{Colors.END}")
            return False
    
    def start(self):
        """شروع ربات"""
        if self.is_running():
            print(f"{Colors.YELLOW}⚠️ ربات در حال اجرا است (PID: {self.get_pid()}){Colors.END}")
            return
        
        print(f"{Colors.BLUE}▶️ شروع ربات...{Colors.END}")
        
        try:
            # اجرای ربات در background
            process = subprocess.Popen(
                [sys.executable, "src/main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.project_dir
            )
            
            # ذخیره PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # صبر کوتاه برای اطمینان از شروع
            time.sleep(3)
            
            if process.poll() is None:
                print(f"{Colors.GREEN}✅ ربات با موفقیت شروع شد (PID: {process.pid}){Colors.END}")
                print(f"{Colors.CYAN}📋 برای مشاهده وضعیت از گزینه 5 استفاده کنید{Colors.END}")
            else:
                stdout, stderr = process.communicate()
                print(f"{Colors.RED}❌ ربات شروع نشد:{Colors.END}")
                print(f"{Colors.RED}{stderr.decode()}{Colors.END}")
                
        except Exception as e:
            print(f"{Colors.RED}❌ خطا در ش��وع ربات: {e}{Colors.END}")
    
    def stop(self):
        """توقف ربات"""
        if not self.is_running():
            print(f"{Colors.YELLOW}⚠️ ربات در حال اجرا نیست{Colors.END}")
            return
        
        pid = self.get_pid()
        print(f"{Colors.BLUE}⏹️ توقف ربات (PID: {pid})...{Colors.END}")
        
        try:
            # ارسال سیگنال SIGTERM
            os.kill(pid, signal.SIGTERM)
            
            # صبر برای توقف
            for _ in range(10):
                if not self.is_running():
                    break
                time.sleep(1)
            
            if self.is_running():
                # اگر هنوز اجرا می‌شود، SIGKILL بفرست
                os.kill(pid, signal.SIGKILL)
                time.sleep(2)
            
            # پاک کردن PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            print(f"{Colors.GREEN}✅ ربات متوقف شد{Colors.END}")
            
        except ProcessLookupError:
            print(f"{Colors.YELLOW}⚠️ پروسه یافت نشد، PID file پاک شد{Colors.END}")
            if self.pid_file.exists():
                self.pid_file.unlink()
        except Exception as e:
            print(f"{Colors.RED}❌ خطا در توقف ربات: {e}{Colors.END}")
    
    def restart(self):
        """ری‌استارت ربات"""
        print(f"{Colors.BLUE}🔄 ری‌استارت ربات...{Colors.END}")
        self.stop()
        time.sleep(2)
        self.start()
    
    def status(self):
        """نمایش وضعیت ربات"""
        print(f"\n{Colors.BOLD}📊 وضعیت P24_SlotHunter{Colors.END}\n")
        
        # وضعیت اجرا
        if self.is_running():
            pid = self.get_pid()
            try:
                process = psutil.Process(pid)
                uptime = datetime.now() - datetime.fromtimestamp(process.create_time())
                memory = process.memory_info().rss / 1024 / 1024  # MB
                cpu = process.cpu_percent()
                
                print(f"{Colors.GREEN}🟢 وضعیت: در حال اجرا{Colors.END}")
                print(f"🆔 PID: {pid}")
                print(f"⏰ مدت اجرا: {str(uptime).split('.')[0]}")
                print(f"💾 حافظه: {memory:.1f} MB")
                print(f"🖥️ CPU: {cpu:.1f}%")
                
            except psutil.NoSuchProcess:
                print(f"{Colors.RED}🔴 وضعیت: متوقف (PID نامعتبر){Colors.END}")
                if self.pid_file.exists():
                    self.pid_file.unlink()
        else:
            print(f"{Colors.RED}🔴 وضعیت: متوقف{Colors.END}")
        
        # وضعیت فایل‌ها
        print(f"\n{Colors.BOLD}📁 فایل‌ها:{Colors.END}")
        files_status = [
            (".env", self.env_file),
            ("config.yaml", self.config_file),
            ("لاگ", self.log_file),
            ("PID", self.pid_file)
        ]
        
        for name, path in files_status:
            if path.exists():
                size = path.stat().st_size
                if size > 1024 * 1024:
                    size_str = f"{size / 1024 / 1024:.1f} MB"
                elif size > 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size} B"
                print(f"✅ {name}: موجود ({size_str})")
            else:
                print(f"❌ {name}: موجود نیست")
        
        # آخرین لاگ‌ها
        if self.log_file.exists():
            print(f"\n{Colors.BOLD}📋 آخرین لاگ‌ها:{Colors.END}")
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:
                        print(f"  {line.strip()}")
            except Exception as e:
                print(f"❌ خطا در خواندن لاگ: {e}")
    
    def monitor(self):
        """مانیتورینگ زنده"""
        print(f"\n{Colors.BOLD}📈 مانیتورینگ زنده P24_SlotHunter{Colors.END}")
        print(f"{Colors.CYAN}برای خروج Ctrl+C را فشار دهید{Colors.END}\n")
        
        try:
            while True:
                # پاک کردن صفحه
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print(f"{Colors.BOLD}📈 مانیتورینگ زنده - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")
                
                if self.is_running():
                    pid = self.get_pid()
                    try:
                        process = psutil.Process(pid)
                        
                        # اطلاعات پروسه
                        uptime = datetime.now() - datetime.fromtimestamp(process.create_time())
                        memory = process.memory_info().rss / 1024 / 1024
                        cpu = process.cpu_percent()
                        
                        print(f"{Colors.GREEN}🟢 وضعیت: در حال اجرا{Colors.END}")
                        print(f"🆔 PID: {pid}")
                        print(f"⏰ مدت اجرا: {str(uptime).split('.')[0]}")
                        print(f"💾 حافظه: {memory:.1f} MB")
                        print(f"🖥️ CPU: {cpu:.1f}%")
                        
                        # نمودار حافظه ساده
                        memory_bar = "█" * int(memory / 10) + "░" * (20 - int(memory / 10))
                        print(f"📊 حافظه: [{memory_bar}] {memory:.1f} MB")
                        
                        # آخرین لاگ‌ها
                        if self.log_file.exists():
                            print(f"\n{Colors.BOLD}📋 آخرین لاگ‌ها:{Colors.END}")
                            with open(self.log_file, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                for line in lines[-3:]:
                                    timestamp = line.split(' - ')[0] if ' - ' in line else ''
                                    message = line.split(' - ', 2)[-1].strip() if ' - ' in line else line.strip()
                                    print(f"  {Colors.CYAN}{timestamp}{Colors.END} {message}")
                        
                    except psutil.NoSuchProcess:
                        print(f"{Colors.RED}🔴 پروسه یافت نشد{Colors.END}")
                else:
                    print(f"{Colors.RED}🔴 ربات متوقف است{Colors.END}")
                
                # صبر 5 ثانیه
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}مانیتورینگ متوقف شد{Colors.END}")
    
    def show_logs(self):
        """نمایش لاگ‌ها"""
        if not self.log_file.exists():
            print(f"{Colors.YELLOW}⚠️ فایل لاگ موجود نیست{Colors.END}")
            return
        
        print(f"\n{Colors.BOLD}📋 لاگ‌های P24_SlotHunter{Colors.END}")
        print(f"{Colors.CYAN}آخرین 50 خط:{Colors.END}\n")
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-50:]:
                    # رنگ‌بندی بر اساس سطح لاگ
                    if 'ERROR' in line:
                        print(f"{Colors.RED}{line.strip()}{Colors.END}")
                    elif 'WARNING' in line:
                        print(f"{Colors.YELLOW}{line.strip()}{Colors.END}")
                    elif 'INFO' in line:
                        print(f"{Colors.GREEN}{line.strip()}{Colors.END}")
                    else:
                        print(line.strip())
        except Exception as e:
            print(f"{Colors.RED}❌ خطا در خواندن لاگ: {e}{Colors.END}")
    
    def settings(self):
        """تنظیمات"""
        print(f"\n{Colors.BOLD}⚙️ تنظیمات P24_SlotHunter{Colors.END}\n")
        
        print("1. 🔧 ویرایش متغیرهای محیطی")
        print("2. 👨‍⚕️ مدیریت دکترها")
        print("3. 📊 تنظیمات نظارت")
        print("4. 🔙 بازگشت")
        
        choice = input(f"\n{Colors.CYAN}انتخاب کنید: {Colors.END}").strip()
        
        if choice == "1":
            self.edit_environment()
        elif choice == "2":
            self.manage_doctors()
        elif choice == "3":
            self.monitoring_settings()
    
    def edit_environment(self):
        """ویرایش متغیرهای محیطی"""
        print(f"\n{Colors.BLUE}🔧 ویرایش متغیرهای محیطی{Colors.END}")
        
        if not self.env_file.exists():
            print(f"{Colors.RED}❌ فایل .env موجود نیست{Colors.END}")
            return
        
        # نمایش تنظیمات فعلی
        with open(self.env_file, 'r') as f:
            content = f.read()
        
        print(f"\n{Colors.CYAN}تنظیمات فعلی:{Colors.END}")
        for line in content.split('\n'):
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                if 'TOKEN' in key:
                    value = value[:10] + "..." if len(value) > 10 else value
                print(f"  {key} = {value}")
        
        print(f"\n{Colors.YELLOW}آیا می‌خواهید تنظیمات را دوباره انجام دهید؟ (y/N): {Colors.END}", end="")
        if input().strip().lower() == 'y':
            self.setup_environment()
    
    def manage_doctors(self):
        """مدیریت دکترها"""
        print(f"\n{Colors.BLUE}👨‍⚕️ مدیریت دکترها{Colors.END}")
        
        if not self.config_file.exists():
            print(f"{Colors.RED}❌ فایل تنظیمات موجود نیست{Colors.END}")
            return
        
        print("1. 📋 نمایش دکترهای فعلی")
        print("2. ➕ افزودن دکتر جدید")
        print("3. 🔙 بازگشت")
        
        choice = input(f"\n{Colors.CYAN}انتخاب کنید: {Colors.END}").strip()
        
        if choice == "1":
            # نمایش دکترها
            try:
                import yaml
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                doctors = config.get('doctors', [])
                if doctors:
                    print(f"\n{Colors.CYAN}دکترهای ثبت شده:{Colors.END}")
                    for i, doctor in enumerate(doctors, 1):
                        status = "✅ فعال" if doctor.get('is_active', True) else "⏸️ غیرفعال"
                        print(f"{i}. {doctor['name']} - {doctor.get('specialty', 'نامشخص')} ({status})")
                else:
                    print(f"{Colors.YELLOW}⚠️ هیچ دکتری ثبت نشده{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}❌ خطا در خواندن تنظیمات: {e}{Colors.END}")
        
        elif choice == "2":
            self.setup_doctors()
    
    def monitoring_settings(self):
        """تنظیمات نظارت"""
        print(f"\n{Colors.BLUE}📊 تنظیمات نظارت{Colors.END}")
        print(f"{Colors.CYAN}💡 برای تغییر این تنظیمات، فایل config/config.yaml را ویرایش کنید{Colors.END}")
    
    def cleanup(self):
        """پاک‌سازی"""
        print(f"\n{Colors.BOLD}🧹 پاک‌سازی P24_SlotHunter{Colors.END}\n")
        
        print("1. 🗑️ پاک کردن لاگ‌ها")
        print("2. 🗑️ پاک کردن دیتابیس")
        print("3. 🗑️ پاک کردن همه (Reset کامل)")
        print("4. 🔙 بازگشت")
        
        choice = input(f"\n{Colors.CYAN}انتخاب کنید: {Colors.END}").strip()
        
        if choice == "1":
            if self.log_file.exists():
                self.log_file.unlink()
                print(f"{Colors.GREEN}✅ لاگ‌ها پاک شدند{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️ فایل لاگ موجود نیست{Colors.END}")
        
        elif choice == "2":
            db_file = self.project_dir / "data" / "slothunter.db"
            if db_file.exists():
                confirm = input(f"{Colors.RED}⚠️ آیا مطمئن هستید؟ تمام داده‌ها پاک خواهد شد! (yes/no): {Colors.END}")
                if confirm.lower() == "yes":
                    db_file.unlink()
                    print(f"{Colors.GREEN}✅ دیتابیس پاک شد{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️ فایل دیتابیس موجود نیست{Colors.END}")
        
        elif choice == "3":
            confirm = input(f"{Colors.RED}⚠️ آیا مطمئن هستید؟ تمام تنظیمات و داده‌ها پاک خواهد شد! (yes/no): {Colors.END}")
            if confirm.lower() == "yes":
                files_to_remove = [self.log_file, self.pid_file, 
                                 self.project_dir / "data" / "slothunter.db"]
                
                for file_path in files_to_remove:
                    if file_path.exists():
                        file_path.unlink()
                
                print(f"{Colors.GREEN}✅ پاک‌سازی کامل انجام شد{Colors.END}")
    
    def is_running(self) -> bool:
        """بررسی اجرا بودن ربات"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # بررسی وجود پروسه
            return psutil.pid_exists(pid)
        except (ValueError, FileNotFoundError):
            return False
    
    def get_pid(self) -> Optional[int]:
        """دریافت PID ربات"""
        if not self.pid_file.exists():
            return None
        
        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            return None
    
    def run(self):
        """اجرای منوی اصلی"""
        while True:
            self.print_header()
            self.print_menu()
            
            choice = input().strip()
            
            if choice == "1":
                self.setup()
            elif choice == "2":
                self.start()
            elif choice == "3":
                self.stop()
            elif choice == "4":
                self.restart()
            elif choice == "5":
                self.status()
            elif choice == "6":
                self.monitor()
            elif choice == "7":
                self.show_logs()
            elif choice == "8":
                self.settings()
            elif choice == "9":
                self.cleanup()
            elif choice == "0":
                print(f"\n{Colors.CYAN}👋 خداحافظ!{Colors.END}")
                break
            else:
                print(f"\n{Colors.RED}❌ انتخاب نامعتبر{Colors.END}")
            
            if choice != "6":  # مانیتورینگ خودش صفحه را پاک می‌کند
                input(f"\n{Colors.YELLOW}برای ادامه Enter را فشار دهید...{Colors.END}")


def main():
    """تابع اصلی"""
    try:
        manager = SlotHunterManager()
        manager.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}👋 خداحافظ!{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ خطای غیرمنتظره: {e}{Colors.END}")


if __name__ == "__main__":
    main()