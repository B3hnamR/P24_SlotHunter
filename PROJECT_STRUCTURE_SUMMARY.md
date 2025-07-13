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