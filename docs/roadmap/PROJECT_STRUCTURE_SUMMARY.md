# 🎯 P24_SlotHunter - Project Structure Summary

## 📖 **پروژه چیست؟**

**P24_SlotHunter** یک ربات تلگرام هوشمند برای رصد و اطلاع‌رسانی نوبت‌های خالی در سایت **پذیرش۲۴** است. این ربات به صورت ۲۴/۷ نوبت‌های موجود دکترها را بررسی می‌کند و در صورت پیدا شدن نوبت خالی، فوراً به کاربران مشترک اطلاع می‌دهد.

### 🔥 **ویژگی‌های کلیدی:**
- 🤖 **ربات تلگرام** با UI مدرن و کاربرپسند
- 🔍 **رصد خودکار** نوبت‌های خالی از API پذیرش۲۴
- ⚡ **اطلاع‌رسانی فوری** در کمتر از 30 ثانیه
- 👥 **مدیریت کاربران** و سیستم اشتراک
- 📊 **پایگاه داده** برای ذخیره اطلاعات
- 🔧 **مدیریت سرور** خودک��ر با اسکریپت پیشرفته

### 🏗️ **معماری:**
- **API-Only Architecture** - بدون Web Scraping
- **Async/Await** برای عملکرد بهتر
- **SQLAlchemy ORM** برای مدیریت دیتابیس
- **Modular Design** برای توسعه آسان

---

## 📁 **ساختار کامل پروژه**

```
P24_SlotHunter/
├── 📁 src/                          # کد اصلی پروژه
│   ├── 📁 api/                      # لایه API و ارتباط با پذیرش۲۴
│   │   ├── __init__.py              # ماژول API
│   │   ├── models.py                # مدل‌های داده API
│   │   └── paziresh_client.py       # کلاینت API پذیرش۲۴
│   ├── 📁 database/                 # لایه دیتابیس
│   │   ├── __init__.py              # ماژول دیتابیس
│   │   ├── database.py              # مدیریت اتصال دیتابیس
│   │   └── models.py                # مدل‌های جداول دیتابیس
│   ├── 📁 telegram_bot/             # لایه ربات تلگرام
│   │   ├── __init__.py              # ماژول ربات
│   │   ├── bot.py                   # کلاس اصلی ربات
│   │   ├── unified_handlers.py      # ��دیریت دستورات و callback ها
│   │   └── messages.py              # قالب‌های پیام
│   ├── 📁 utils/                    # ابزارهای کمکی
│   │   ├── __init__.py              # ماژول utils
│   │   ├── config.py                # مدیریت تنظیمات
│   │   └── logger.py                # سیستم لاگ
│   ├── __init__.py                  # ماژول اصلی src
│   └── main.py                      # نقطه ورود اصلی برنامه
├── 📁 config/                       # فایل‌های تنظیمات
│   └── config.yaml                  # تنظیمات اصلی (دکترها، API، etc.)
├── 📁 data/                         # پایگاه داده
│   ├── .gitkeep                     # نگه‌داری پوشه در Git
│   └── slothunter.db               # فایل SQLite (ایجاد خودکار)
├── 📁 logs/                         # فایل‌های لاگ
│   ├── .gitkeep                     # نگه‌داری پوشه در Git
│   ├── slothunter.log              # لاگ اصلی برنامه
│   └── manager.log                 # لاگ مدیریت سرور
├── 📁 alembic/                      # مایگریشن دیتابیس
│   ├── versions/                    # فایل‌های مایگریشن
│   ├── env.py                       # تنظیمات Alembic
│   ├── script.py.mako              # قالب مایگریشن
│   └── README                       # راهنمای Alembic
├── 📁 docs/                         # مستندات
│   ├── README.md                    # راهنمای اصلی
│   └── roadmap/                     # نقشه راه توسعه
├── 📁 .git/                         # Git repository
├── 📁 .qodo/                        # تنظیمات Qodo
├── 📁 .vscode/                      # تنظیمات VS Code
├── .env                             # متغیرهای محیطی (محرمانه)
├── .env.example                     # نمونه متغیرهای محیطی
├── .gitignore                       # فایل‌های نادیده گرفته شده Git
├── alembic.ini                      # تنظیمات Alembic
├── requirements.txt                 # وابستگی‌های Python
├── server_manager.sh               # اسکریپت مدیریت سرور
├── slothunter.service              # فایل سرویس systemd
├── SETUP_GUIDE.md                  # راهنمای نصب
├── PROJECT_STRUCTURE_SUMMARY.md    # این فایل
└── README.md                        # معرفی پروژه
```

---

## 🔧 **توضیح تفصیلی فایل‌ها**

### 📁 **src/ - کد اصلی**

#### 📁 **src/api/ - لایه API**

**🎯 هدف:** ارتباط با API پذیرش۲۴ و مدیریت درخواست‌ها

- **`models.py`** - مدل‌های داده API
  ```python
  @dataclass
  class Doctor:      # اطلاعات دکتر
  class Appointment: # اطلاعات نوبت
  class APIResponse: # پاسخ API
  ```

- **`paziresh_client.py`** - کلاینت اصلی API
  ```python
  class PazireshAPI:
    - get_available_appointments()  # دریافت نوبت‌های موجود
    - reserve_appointment()         # رزرو موقت نوبت
    - cancel_reservation()          # لغو رزرو
  ```

#### 📁 **src/database/ - لایه دیتابیس**

**🎯 هدف:** مدیریت پایگاه داده و ذخیره اطلاعات

- **`database.py`** - مدیریت اتصال و session
  ```python
  class DatabaseManager:
    - session_scope()     # مدیریت session
    - _setup_database()   # راه‌اندازی دیتابیس
  ```

- **`models.py`** - مدل‌های جداول
  ```python
  class User:         # کاربران تلگرام
  class Doctor:       # اطلاعات دکترها
  class Subscription: # اشتراک‌های کاربران
  ```

#### 📁 **src/telegram_bot/ - لایه ربات**

**🎯 هدف:** رابط کاربری تلگرام و مدیریت تعاملات

- **`bot.py`** - کلاس اصلی ربات
  ```python
  class SlotHunterBot:
    - initialize()              # راه‌اندازی ربات
    - start_polling()           # شروع دریافت پیام‌ها
    - send_appointment_alert()  # ارسال اطلاع‌رسانی
  ```

- **`unified_handlers.py`** - مدیریت دستورات (قابل توسعه)
  ```python
  class UnifiedTelegramHandlers:
    # Command Handlers
    - start_command()           # دستور /start
    - help_command()            # دستور /help
    - doctors_command()         # دستور /doctors
    
    # Message Handlers
    - handle_text_message()     # پیام‌های متنی
    - handle_callback()         # دکمه‌های inline
    
    # Core Functions
    - _show_doctors_list()      # نمایش لیست دکترها
    - _show_subscriptions()     # نمایش اشتراک‌ها
    - _callback_subscribe()     # اشتراک در دکتر
    - _callback_unsubscribe()   # لغو اشتراک
  ```

- **`messages.py`** - قالب‌های پیام
  ```python
  class MessageFormatter:
    - welcome_message()         # پیام خوش‌آمدگویی
    - help_message()            # پیام راهنما
    - appointment_alert_message() # پیام اطلاع‌رسانی نوبت
  ```

#### 📁 **src/utils/ - ابزارهای کمکی**

- **`config.py`** - مدیریت تنظیمات
  ```python
  class Config:
    - telegram_bot_token        # توکن ربات
    - admin_chat_id            # شناسه ادمین
    - check_interval           # فاصله بررسی
    - get_doctors()            # دریافت لیست دکترها
  ```

- **`logger.py`** - سیستم لاگ
  ```python
  - setup_logger()            # راه‌اندازی logger
  - get_logger()              # دریافت logger
  - notify_admin_critical_error() # اطلاع خطای بحرانی
  ```

#### **`main.py`** - نقطه ورود اصلی

```python
class SlotHunter:
  - start()                   # شروع سیستم
  - monitor_loop()            # حلقه رصد نوبت‌ها
  - check_doctor()            # بررسی نوبت یک دکتر
  - stop()                    # توقف سیستم
```

---

## ⚙️ **فایل‌های تنظیمات**

### **`.env`** - متغیرهای محیطی (محرمانه)
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_CHAT_ID=123456789
CHECK_INTERVAL=30
LOG_LEVEL=INFO
```

### **`config/config.yaml`** - تنظیمات اصلی
```yaml
telegram:
  bot_token: ${TELEGRAM_BOT_TOKEN}
  admin_chat_id: ${ADMIN_CHAT_ID}

monitoring:
  check_interval: 30
  max_retries: 3
  timeout: 10
  days_ahead: 7

doctors:
  - name: "دکتر نمونه"
    slug: "doctor-example"
    center_id: "12345"
    service_id: "67890"
    user_center_id: "11111"
    terminal_id: "22222"
    specialty: "قلب و عروق"
    is_active: true
```

### **`requirements.txt`** - وابستگی‌های Python
```
# Core Dependencies
requests>=2.31.0
httpx>=0.25.0

# Telegram Bot
python-telegram-bot>=20.0

# Database
sqlalchemy[asyncio]>=2.0.0
aiosqlite>=0.19.0
alembic>=1.12.0

# Configuration
pyyaml>=6.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

---

## 🚀 **اسکریپت مدیریت سرور**

### **`server_manager.sh`** - مدیریت کامل سرور

**🎯 قابلیت‌ها:**
- 🔧 **نصب خودکار** تمام وابستگی‌ها
- 🐍 **راه‌اندازی Python virtual environment**
- ⚙️ **Configuration wizard** تعاملی
- 🔄 **مدیریت سرویس** (start/stop/restart)
- 📊 **نظارت سیستم** و health check
- 📋 **مشاهده لاگ‌ها** با رنگ‌بندی
- 🔄 **بروزرسانی خودکار** از Git
- 🛡️ **راه‌اندازی systemd service**

**🎛��� منوی تعاملی:**
```
1. Start Service
2. Stop Service  
3. Restart Service (with update check)
4. View Logs
5. Monitor Live Logs
6. System Statistics
7. Health Check
8. Configuration Wizard
9. Full System Setup
10. Update System
```

**💻 استفاده از خط فرمان:**
```bash
./server_manager.sh start     # شروع سرویس
./server_manager.sh stop      # توقف سرویس
./server_manager.sh restart   # ری‌استارت
./server_manager.sh status    # وضعیت سرویس
./server_manager.sh logs      # مشاهده لاگ‌ها
./server_manager.sh setup     # نصب کامل
```

---

## 💾 **پایگاه داده**

### **ساختار جداول:**

#### **`users`** - کاربران تلگرام
```sql
- id (Primary Key)
- telegram_id (Unique)
- username
- first_name
- last_name
- is_active
- created_at
- last_activity
```

#### **`doctors`** - اطلاعات دکترها
```sql
- id (Primary Key)
- name
- slug (Unique)
- center_id, service_id, user_center_id, terminal_id (API)
- specialty
- center_name, center_address, center_phone
- is_active
- created_at
```

#### **`subscriptions`** - اشتراک‌های کاربران
```sql
- id (Primary Key)
- user_id (Foreign Key -> users)
- doctor_id (Foreign Key -> doctors)
- is_active
- created_at
```

### **م��یگریشن دیتابیس:**
```bash
# ایجاد مایگریشن جدید
alembic revision --autogenerate -m "description"

# اعمال مایگریشن‌ها
alembic upgrade head

# بازگشت به مایگریشن قبلی
alembic downgrade -1
```

---

## 🔄 **فرآیند کار سیستم**

### **1. راه‌اندازی:**
```
main.py → SlotHunter.start()
├── DatabaseManager._setup_database()
├── SlotHunterBot.initialize()
├── _load_doctors_to_db()
└── asyncio.gather(bot.start_polling(), monitor_loop())
```

### **2. حلقه رصد:**
```
monitor_loop() (هر 30 ثانیه)
├── دریافت دکترهای فعال از دیتابیس
├── برای هر دکتر: check_doctor()
│   ├── PazireshAPI.get_available_appointments()
│   ├── اگر نوبت موجود: send_appointment_alert()
│   └── ارسال به مشترکین از دیتابیس
└── صبر تا دور بعدی
```

### **3. تعامل کاربر:**
```
کاربر در تلگرام
├── /start → ثبت در دیتابیس
├── "مشاهده دکترها" → لیست از دیتابیس
├── کلیک روی دکتر → اطلاعات + دکمه اشتراک
├── "اشتراک" → ثبت در جدول subscriptions
└── دریافت اطلاع‌رسانی نوبت‌ها
```

---

## 🛠️ **نحوه توسعه**

### **اضافه کردن قابلیت جدید به ربات:**

1. **اضافه کردن callback به registry:**
```python
# در unified_handlers.py
self.callback_handlers["new_feature"] = self._callback_new_feature
```

2. **پیاده‌سازی handler:**
```python
async def _callback_new_feature(self, query, user_id):
    # کد قابلیت جدید
    pass
```

3. **اضافه کردن دکمه:**
```python
keyboard.append([
    InlineKeyboardButton("قابلیت جدید", callback_data="new_feature")
])
```

### **اضافه کردن جدول جدید:**

1. **تعریف مدل در `database/models.py`:**
```python
class NewTable(Base):
    __tablename__ = 'new_table'
    id = Column(Integer, primary_key=True)
    # سایر فیلدها
```

2. **ایجاد مایگریشن:**
```bash
alembic revision --autogenerate -m "add new_table"
alembic upgrade head
```

### **اضافه کردن endpoint جدید API:**

1. **اضافه کردن متد به `PazireshAPI`:**
```python
async def new_api_method(self):
    # کد API جدید
    pass
```

2. **استفاده در `main.py`:**
```python
result = await api.new_api_method()
```

---

## 📊 **مانیتورینگ و لاگ‌ها**

### **سطوح لاگ:**
- **DEBUG:** اطلاعات تفصیلی برای debugging
- **INFO:** اطلاعات عمومی عملکرد
- **WARNING:** هشدارها و مسائل غیربحرانی
- **ERROR:** خطاهای قابل بازیابی
- **CRITICAL:** خطاهای بحرانی

### **فایل‌های لاگ:**
- **`logs/slothunter.log`** - لاگ اصلی برنامه
- **`logs/manager.log`** - لاگ اسکریپت مدیریت

### **مشاهده لاگ‌ها:**
```bash
# مشاهده لاگ‌های اخیر
tail -f logs/slothunter.log

# جستجو در لاگ‌ها
grep "ERROR" logs/slothunter.log

# استفاده از server manager
./server_manager.sh logs
./server_manager.sh monitor
```

---

## 🔒 **امنیت**

### **اطلاعات محرمانه:**
- **`.env`** - هرگز commit نشود
- **`data/slothunter.db`** - شامل اطلاعات کاربران
- **`logs/`** - ممکن است حاوی اطلاعات حساس باشد

### **دسترسی‌ها:**
- **Admin Chat ID** - دسترسی کامل به سیستم
- **Regular Users** - فقط اشتراک و مشاهده

### **Systemd Service:**
- اجرا با کاربر محدود
- محدودیت‌های امنیتی سیستم
- مسیرهای محدود برای نوشتن

---

## 🚀 **راه‌اندازی سریع**

### **برای توسعه‌دهنده جدید:**

1. **Clone کردن پروژه:**
```bash
git clone <repository-url>
cd P24_SlotHunter
```

2. **راه‌اندازی خودکار:**
```bash
chmod +x server_manager.sh
./server_manager.sh setup
```

3. **تنظیم متغیرهای محیطی:**
```bash
./server_manager.sh config
# یا دستی ویرایش .env
```

4. **اضافه کردن دکتر در `config/config.yaml`:**
```yaml
doctors:
  - name: "دکتر نمونه"
    slug: "doctor-slug"
    center_id: "12345"
    # سایر اطلاعات API
```

5. **شروع سرویس:**
```bash
./server_manager.sh start
```

### **برای production:**

1. **نصب روی سرور:**
```bash
./server_manager.sh setup
```

2. **تنظیم systemd service:**
```bash
sudo ./server_manager.sh setup  # اگر root access دارید
```

3. **مدیریت با systemctl:**
```bash
sudo systemctl start slothunter
sudo systemctl enable slothunter
sudo systemctl status slothunter
```

---

## 📈 **آمار و عملکرد**

### **متریک‌های مهم:**
- **Response Time:** زمان پاسخ API پذیرش۲۴
- **Check Interval:** فاصله بررسی نوبت‌ها (پیش‌فرض 30 ثانیه)
- **Active Users:** تعداد کاربران فعال
- **Active Subscriptions:** تعداد اشتراک‌های فعال
- **Success Rate:** نرخ موفقیت درخواست‌های API

### **بهینه‌سازی:**
- **Async Operations:** تمام عملیات I/O غیرهمزمان
- **Connection Pooling:** استفاده مجدد از اتصالات HTTP
- **Database Indexing:** ایندکس روی فیل��های پرکاربرد
- **Efficient Queries:** کوئری‌های بهینه دیتابیس

---

## 🔮 **نقشه راه توسعه**

### **قابلیت‌های آینده:**
- 🔍 **جستجوی پیشرفته** دکترها
- 📊 **داشبورد آماری** برای ادمین
- 🔔 **تنظیمات اعلان** شخصی‌سازی شده
- 🌐 **پشتیبانی چندزبانه**
- 📱 **اپلیکیشن موبایل**
- 🤖 **هوش مصنوعی** برای پیش‌بینی نوبت‌ها

### **بهبودهای فنی:**
- 🐳 **Docker containerization**
- ☁️ **Cloud deployment**
- 📊 **Prometheus monitoring**
- 🔄 **Redis caching**
- 🔐 **OAuth authentication**

---

## 📞 **پشتیبانی**

### **مشکلات رایج:**

1. **ربات پاسخ نمی‌دهد:**
   - بررسی وضعیت سرویس: `./server_manager.sh status`
   - مشاهده لاگ‌ها: `./server_manager.sh logs`
   - بررسی توکن ربات در `.env`

2. **خطای دیتابیس:**
   - اجرای مایگریشن‌ها: `alembic upgrade head`
   - بررسی مجوزهای فایل دیتابیس

3. **خطای API:**
   - بررسی اتصال اینترنت
   - بررسی وضعیت سرورهای پذیرش۲۴
   - بررسی اطلاعات API دکترها

### **ابزاره��ی debugging:**
```bash
# Health check کامل
./server_manager.sh health

# مانیتور لایو لاگ‌ها
./server_manager.sh monitor

# آمار سیستم
./server_manager.sh stats
```

---

## 📝 **نتیجه‌گیری**

**P24_SlotHunter** یک سیستم کامل و حرفه‌ای برای رصد نوبت‌های پذیرش۲۴ است که با معماری مدرن و قابلیت‌های پیشرفته طراحی شده. این پروژه برای توسعه‌دهندگانی که می‌خواهند:

- 🤖 **ربات تلگرام** پیشرفته بسازند
- 🔗 **API integration** یاد بگیرند  
- 💾 **Database management** با SQLAlchemy
- 🐍 **Async Python programming**
- 🛠️ **DevOps** و مدیریت سرور

**مناسب است و می‌تواند به عنوان پایه‌ای برای پروژه‌های مشابه استفاده شود.**

---

*آخرین بروزرسانی: $(date)*
*نسخه: 3.0 - API-Only Architecture*

------------------
NEW UPDATE : 

📊 خلاصه کلی پروژه
🎯 هدف اصلی:
ربات تلگرام هوشمند برای رصد و اطلاع‌رسانی نوبت‌های خالی پذیرش۲۴ با قابلیت اضافه کردن دکتر از لینک

🏗️ معماری API که ساختیم
1️⃣ لایه استخراج اطلاعات (doctor_extractor.py)
class DoctorExtractor:
    ✅ normalize_doctor_url()      # نرمال‌سازی URL دکتر
    ✅ extract_slug_from_url()     # استخراج slug از URL
    ✅ fetch_doctor_page()         # دریافت HTML صفحه دکتر
    ✅ extract_next_data()         # استخراج __NEXT_DATA__ از HTML
    ✅ parse_doctor_data()         # تجزیه اطلاعات دکتر
    ✅ generate_terminal_id()      # تولید terminal_id
    ✅ extract_doctor_from_url()   # فرآیند کامل استخراج

Copy

Insert

🔧 قابلیت‌ها:

پشتیبانی از فرمت‌های مختلف URL:
https://www.paziresh24.com/dr/دکتر-نام-0/
dr/دکتر-نام-0/
دکتر-نام-0
استخراج خودکار تمام اطلاعات از __NEXT_DATA__
پردازش چندین مرکز و سرویس
تولید خودکار terminal_id
2️⃣ لایه مدیریت دکترها (doctor_manager.py)
class DoctorManager:
    ✅ add_doctor_from_url()       # اضافه کردن دکتر از URL
    ✅ get_doctor_with_details()   # دریافت دکتر با جزئیات
    ✅ get_all_doctors_with_details() # دریافت تمام دکترها
    ✅ update_doctor_status()      # به‌روزرسانی وضعیت دکتر
    ✅ delete_doctor()             # حذف دکتر (soft delete)
    ✅ refresh_doctor_data()       # به‌روزرسانی از سایت
    ✅ validate_doctor_url()       # اعتبارسنجی URL
    ✅ get_doctor_stats()          # آمار دکترها

Copy

Insert

🔧 قابلیت‌ها:

CRUD کامل برای دکترها
اعتبارسنجی و validation
مدیریت خطاها
آمارگیری
3️⃣ API Client پیشرفته (enhanced_paziresh_client.py)
class EnhancedPazireshAPI:
    ✅ get_doctor_appointments()   # دریافت نوبت‌های تمام مراکز
    ✅ _get_service_appointments() # نوبت‌های یک سرویس خاص
    ✅ _get_free_days()           # روزهای موجود
    ✅ _get_day_appointments()    # نوبت‌های یک روز
    ✅ reserve_appointment()      # رزرو موقت نوبت
    ✅ cancel_reservation()       # لغو رزرو
    ✅ get_appointment_booking_url() # تولید لینک رزرو

Copy

Insert

🔧 قابلیت‌ها:

پشتیبانی از چندین مرکز همزمان
مدیریت چندین سرویس در هر مرکز
تولید خودکار terminal_id
مدیریت خطاها و timeout
💾 ساختار دیتابیس پیشرفته
📋 جداول اصلی:
1️⃣ Doctor - اطلاعات اصلی دکتر
✅ id, name, slug
✅ doctor_id, provider_id, user_id, server_id  # API IDs
✅ specialty, biography, image_url
✅ is_active, last_checked, created_at

Copy

Insert

2️⃣ DoctorCenter - مراکز درمانی
✅ id, doctor_id (FK)
✅ center_id, center_name, center_type
✅ center_address, center_phone
✅ user_center_id  # برای API
✅ is_active, created_at

Copy

Insert

3️⃣ DoctorService - سرویس‌های هر مرکز
✅ id, center_id (FK)
✅ service_id, service_name
✅ user_center_id  # برای API
✅ price, duration
✅ is_active, created_at

Copy

Insert

4️⃣ User - کاربران تلگرام
✅ id, telegram_id, username
✅ first_name, last_name
✅ is_active, is_admin
✅ created_at, last_activity

Copy

Insert

5️⃣ Subscription - اشتراک‌ها
✅ id, user_id (FK), doctor_id (FK)
✅ is_active, created_at, updated_at

Copy

Insert

6️⃣ AppointmentLog - لاگ نوبت‌ها
✅ id, doctor_id (FK)
✅ appointment_date, appointment_count
✅ notified_users, created_at

Copy

Insert

🤖 قابلیت‌های ربات تلگرام
📱 رابط کاربری:
1️⃣ منوی اصلی:
🎯 منوی اصلی
├── 👨‍⚕️ مشاهده دکترها
├── 📝 اشتراک‌های من  
└── 🆕 اضافه کردن دکتر  ← جدید!

Copy

Insert

2️⃣ منوی دائمی (کیبورد):
┌─────────────────┬─────────────────┐
│ 👨‍⚕️ دکترها      │ 📝 اشتراک‌ها     │
└─────────────────┴─────────────────┘

Copy

Insert

🔧 قابلیت‌های اصلی:
1️⃣ مدیریت دکترها:
✅ مشاهده لیست دکترها با ایموجی تخصص
✅ اطلاعات تفصیلی دکتر (تخصص، مراکز، سرویس‌ها)
✅ اضافه کردن دکتر از لینک (جدید!)
✅ بررسی نوبت‌های خالی در تمام مراکز
✅ به‌روزرسانی اطلاعات دکتر
✅ حذف دکتر (برای ادمین‌ها)
2️⃣ سیستم اشتراک:
✅ اشتراک در دکتر با یک کلیک
✅ لغو اشتراک آسان
✅ مدیریت اشتراک‌های فعال
✅ اطلاع‌رسانی فوری نوبت‌های خالی
3️⃣ تشخیص هوشمند:
✅ تشخیص خودکار URL دکتر در پیام‌ها
✅ پردازش خودکار بدون نیاز به دستور
✅ اعتبارسنجی URL قبل از پردازش
4️⃣ پیام‌های هوشمند:
✅ پیام‌های فارسی کاملاً بومی‌سازی شده
✅ ایموجی‌های تخصص (❤️ قلب، 🧠 مغز، 👁️ چشم، ...)
✅ کیبوردهای inline تعاملی
✅ پیام‌های خطا واضح و راهنما
🔄 فرآیند اضافه کردن دکتر:
روش 1: از منو
1. کلیک روی "🆕 اضافه کردن دکتر"
2. ارسال لینک دکتر
3. پردازش خودکار و نمایش نتیجه

Copy

Insert

روش 2: ارسال مستقیم
1. ارسال لینک دکتر در چت
2. تشخیص خودکار توسط ربات
3. پردازش و اضافه کردن

Copy

Insert

📊 نمایش اطلاعات دکتر:
❤️ دکتر احمد محمدی

🏥 تخصص: قلب و عروق
🏢 مراکز درمانی (2 مرکز):

1. مطب دکتر احمد محمدی
   📍 تهران، خیابان ولیعصر
   📞 021-12345678
   🏷️ مطب
   🔧 سرویس‌ها (2):
      • ویزیت - 500,000 تومان
      • مشاوره آنلاین - 300,000 تومان

2. بیمارستان قلب تهران
   📍 تهران، خیابان کارگر
   📞 021-87654321
   🏷️ بیمارستان
   🔧 سرویس‌ها (1):
      • ویزیت تخصصی - 800,000 تومان

📊 آمار:
• مراکز فعال: 2
• کل سرویس‌ها: 3
• مشترکین: 15

🔗 لینک صفحه:
https://www.paziresh24.com/dr/دکتر-احمد-محمدی-0/

🔔 وضعیت اشتراک: ✅ شما مشترک هستید

Copy

Insert

🔍 بررسی نوبت‌های خالی:
✅ 8 نوبت خالی پیدا شد!

👨‍⚕️ دکتر: احمد محمدی
🕐 زمان بررسی: 14:30:25

📋 نوبت‌های موجود:

🏢 مطب دکتر احمد محمدی - ویزیت
  📅 1403/09/15: 09:00, 10:30, 14:00
  📅 1403/09/16: 08:30, 11:00

🏢 بیمارستان قلب تهران - ویزیت تخصصی  
  📅 1403/09/17: 15:30, 16:00, 17:30

🚀 برای رزرو:
• روی "رزرو سریع" کلیک کنید
• یا از لینک مستقیم استفاده کنید

⚠️ توجه: نوبت‌ها سریع تمام می‌شوند!

Copy

Insert

🔧 API های پیاده‌سازی شده
1️⃣ API های پذیرش24:
✅ POST /booking/v2/getFreeDays    # روزهای موجود
✅ POST /booking/v2/getFreeTurns   # نوبت‌های روز خاص
✅ POST /booking/v2/suspend        # رزرو موقت نوبت
✅ POST /booking/v2/unsuspend      # لغو رزرو نوبت

Copy

Insert

2️⃣ Web Scraping:
✅ GET /dr/{slug}/                 # صفحه دکتر
✅ استخراج __NEXT_DATA__           # اطلاعات JSON
✅ Parse کردن اطلاعات دکتر        # تجزیه ساختار یافته

Copy

Insert

3️⃣ پردازش داده:
✅ نرمال‌سازی URL                  # پشتیبانی فرمت‌های مختلف
✅ اعتبارسنجی اطلاعات             # بررسی صحت داده‌ها
✅ تولید terminal_id              # شناسه منحصر به فرد
✅ مدیریت خطاها                   # Retry و fallback

Copy

Insert

🚀 قابلیت‌های پیشرفته
1️⃣ مدیریت چندین مرکز:
✅ پشتیبانی همزمان از چندین مرکز درمانی
✅ سرویس‌های متنوع در هر مرکز
✅ قیمت‌گذاری مجزا برای هر سرویس
✅ مدیریت وضعیت فعال/غیرفعال
2️⃣ سیستم رصد هوشمند:
✅ رصد همزمان تمام مراکز و سرویس‌ها
✅ اطلاع‌رسانی فوری در کمتر از 30 ثانیه
✅ گروه‌بندی نوبت‌ها بر اساس مرکز و تاریخ
✅ لینک مستقیم رزرو برای هر نوبت
3️⃣ مدیریت کاربران:
✅ ثبت خودکار کاربران جدید
✅ ردیابی فعالیت و آخرین بازدید
✅ سیستم ادمین با دسترسی‌های ویژه
✅ آمار کاربران و اشتراک‌ها
4️⃣ پایه‌سازی رزرو نوبت:
✅ API های رزرو آماده و تست شده
✅ مدیریت session رزرو
✅ لغو خودکار رزروهای منقضی
✅ لینک‌های رزرو مستقیم
📈 آمار و عملکرد
🔢 آمار فعلی سیستم:
✅ 6 جدول دیتابیس          # User, Doctor, DoctorCenter, DoctorService, Subscription, AppointmentLog
✅ 15+ API endpoint         # پذیرش24 + داخلی
✅ 20+ handler تلگرام      # دستورات و callback ها
✅ 5 فایل API              # doctor_extractor, doctor_manager, enhanced_client, models, paziresh_client
✅ 3 فایل ربات تلگرام     # bot, unified_handlers, doctor_handlers
✅ پشتیبانی کامل فارسی    # UI و پیام‌ها

Copy

Insert

⚡ عملکرد:
🚀 Async/Await: تمام عملیات غیرهمزمان
🔄 Connection Pooling: استفاده مجدد از اتصالات
💾 Database Indexing: کوئری‌های بهینه
🛡️ Error Handling: مدیریت کامل خطاها
🎯 خلاصه دستاوردها
✅ چیزهایی که ساختیم:
🔧 لایه API:
استخراج خودکار اطلاعات دکتر از لینک پذیرش24
API client پیشرفته با پشتیبانی چندین مرکز
مدیریت کامل دکترها (CRUD + validation)
سیستم رزرو نوبت (پایه‌سازی شده)
🤖 ربات تلگرام:
رابط کاربری کامل فارسی با ایموجی و کیبورد
اضافه کردن دکتر از لینک با تشخیص خودکار
سیستم اشتراک پیشرفته با مدیریت کامل
نمایش اطلاعات تفصیلی دکترها و نوبت‌ها
بررسی نوبت‌های خالی در تمام مراکز همزمان
💾 دیتابیس:
ساختار پیشرفته با 6 جدول مرتبط
پشتیبانی چندین مرکز برای هر دکتر
مدیریت سرویس‌ها با قیمت و مدت زمان
سیستم لاگ برای ردیابی نوبت‌ها
🚀 قابلیت‌های منحصر به فرد:
✅ اولین ربات با قابلیت اضافه کردن دکتر از لینک
✅ پشتیبانی کامل از ساختار پیچیده پذیرش24
✅ رصد همزمان چندین مرکز و سرویس
✅ UI فارسی کاملاً بومی‌سازی شده
✅ معماری مقیاس‌پذیر برای توسعه آینده
