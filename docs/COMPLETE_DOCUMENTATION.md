# 📚 P24_SlotHunter - مستندات کامل پروژه

**ربات هوشمند نوبت‌یابی پذیرش۲۴** - سیستم رصد خودکار نوبت‌های خالی و اطلاع‌رسانی فوری

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![API](https://img.shields.io/badge/API-Only-green.svg)]()

---

## 📖 فهرست مطالب

1. [معرفی پروژه](#-معرفی-پروژه)
2. [ساختار پروژه](#-ساختار-پروژه)
3. [معماری سیستم](#-معماری-سیستم)
4. [API Documentation](#-api-documentation)
5. [راه‌اندازی](#-راه‌اندازی)
6. [تنظیمات](#-تنظیمات)
7. [ربات تلگرام](#-ربات-تلگرام)
8. [دیتابیس](#-دیتابیس)
9. [مدیریت سرور](#-مدیریت-سرور)
10. [عیب‌ی��بی](#-عیب‌یابی)
11. [امنیت](#-امنیت)
12. [توسعه](#-توسعه)

---

## 🎯 معرفی پروژه

### ویژگی‌های کلیدی:
- 🤖 **ربات تلگرام** با رابط کاربری ساده و دوستانه
- 🔍 **رصد خودکار** نوبت‌های خالی ۲۴/۷ بدون وقفه
- ⚡ **اطلاع‌رسانی فوری** در کمتر از 90 ثانیه
- 🚀 **API-Only** - بدون Web Scraping، استفاده مستقیم از API
- 👥 **پشتیبانی چندین دکتر** همزمان
- 📊 **مدیریت کاربران** و اشتراک‌ها
- 🛡️ **بهینه‌سازی Rate Limiting** برای جلوگیری از مسدود شدن
- 🔄 **Auto-restart** در صورت خطا
- 📱 **Multi-center support** برای دکترهای چندمرکزی

### تکنولوژی‌های استفاده شده:
- **Python 3.9+** - زبان برنامه‌نویسی اصلی
- **SQLAlchemy** - ORM برای مدیریت دیتابیس
- **python-telegram-bot** - کتابخانه ربات تلگرام
- **httpx** - HTTP client async
- **SQLite** - دیتابیس محلی
- **YAML** - فرمت فایل تنظیمات
- **systemd** - مدیریت سرویس در لینوکس

---

## 📁 ساختار پروژه

```
P24_SlotHunter/
├── 📁 src/                          # کد اصلی پروژه
│   ├── 📄 main.py                   # نقطه ورود اصلی
│   ├── 📁 api/                      # ماژول‌های API
│   │   ├── 📄 __init__.py
│   │   ├── 📄 models.py             # مدل‌های داده API
│   │   ├── 📄 enhanced_paziresh_client.py  # کلاینت اصلی API
│   │   ├── 📄 doctor_extractor.py   # استخراج اطلاعات دکتر
│   │   └── 📄 doctor_manager.py     # مدیریت دکترها
│   ├── 📁 telegram_bot/             # ربات تلگرام
│   │   ├── 📄 __init__.py
│   │   ├── 📄 bot.py                # کلاس اصلی ربات
│   │   ├── 📄 unified_handlers.py   # مدیریت پیام‌ها
│   │   ├── 📄 doctor_handlers.py    # مدیریت دکترها
│   │   └── 📄 messages.py           # قالب‌های پیام
│   ├── 📁 database/                 # مدیریت دیتابیس
│   │   ├── 📄 __init__.py
│   │   ├── 📄 database.py           # اتصال دیتابیس
│   │   └── 📄 models.py             # مدل‌های جداول
│   └── 📁 utils/                    # ابزارهای کمکی
│       ├── 📄 __init__.py
│       ├── 📄 config.py             # مدیریت تنظیمات
│       └── 📄 logger.py             # سیستم لاگ
├── 📁 config/                       # فایل‌های تنظیمات
│   └── 📄 config.yaml               # تنظیمات اصلی
├── 📁 data/                         # دیتابیس و داده‌ها
│   └── 📄 slothunter.db             # فایل دیتابیس SQLite
├── 📁 logs/                         # فایل‌های لاگ
│   └── 📄 slothunter.log            # لاگ اصلی
├── 📁 docs/                         # مستندات
│   ├── 📄 README.md
│   ├── 📄 SETUP_GUIDE.md
│   └── 📁 roadmap/                  # نقشه راه توسعه
├── 📁 alembic/                      # مایگریشن دیتابیس
│   └── 📁 versions/
├── 📄 .env                          # متغیرهای محیطی
├── 📄 .env.example                  # نمونه متغیرهای محیطی
├── 📄 requirements.txt              # وابستگی‌های Python
├── 📄 server_manager.sh             # اسکریپت مدیریت سرور
├── 📄 slothunter.service            # فایل سرویس systemd
├── 📄 alembic.ini                   # تنظیمات Alembic
└── 📄 README.md                     # راهنمای اصلی
```

---

## 🏗️ معماری سیستم

### نمودار معماری:
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │   Main Monitor  │    │  Paziresh24 API │
│                 │    │                 │    │                 │
│ • User Interface│◄──►│ • Doctor Check  │◄──►│ • Appointments  │
│ • Subscriptions │    │ • Notifications │    │ • Rate Limiting │
│ • Admin Panel   │    │ • Error Handle  │    │ • Multi-center  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        SQLite Database                         │
│                                                                 │
│ • Users & Subscriptions  • Doctors & Centers  • Logs & Stats   │
└─────────────────────────────────────────────────────────────────┘
```

### جریان کار (Workflow):
1. **راه‌اندازی:** سیستم دیتابیس و ربات تلگرام را راه‌اندازی می‌کند
2. **مانیتورینگ:** هر 90 ثانیه دکترهای فعال را بررسی می‌کند
3. **API Call:** از API پذیرش۲۴ نوبت‌های خالی را دریافت می‌کند
4. **پردازش:** نوبت‌ها را تحلیل و فیلتر می‌کند
5. **اطلاع‌رسانی:** به مشترکین از طریق تلگرام اطلاع می‌دهد
6. **لاگ:** تمام فعالیت‌ها را ثبت می‌کند

---

## 🔌 API Documentation

### کلاس EnhancedPazireshAPI

#### پارامترهای ورودی:
```python
EnhancedPazireshAPI(
    doctor: Doctor,                    # شیء دکتر
    client: httpx.AsyncClient = None,  # HTTP client (اختیاری)
    timeout: int = 15,                 # timeout درخواست
    base_url: str = None,              # URL پایه API
    request_delay: float = 1.5         # تاخیر بین درخواست‌ه��
)
```

#### متدهای اصلی:

##### 1. `get_all_available_appointments(days_ahead: int = 5)`
دریافت تمام نوبت‌های موجود برای دکتر

**پارامترها:**
- `days_ahead`: تعداد روزهای آینده برای بررسی (پیش‌فرض: 5)

**خروجی:**
```python
List[Appointment]  # لیست نوبت‌های موجود
```

**مثال:**
```python
api = EnhancedPazireshAPI(doctor)
appointments = await api.get_all_available_appointments(days_ahead=7)
for apt in appointments:
    print(f"نوبت: {apt.time_str}")
```

##### 2. `reserve_appointment(center, service, appointment)`
رزرو موقت نوبت

**پارامترها:**
- `center`: شیء مرکز درمانی
- `service`: شیء سرویس
- `appointment`: شیء نوبت

**خروجی:**
```python
APIResponse  # پاسخ API شامل وضعیت رزرو
```

##### 3. `cancel_reservation(center, request_code)`
لغو رزرو نوبت

### مدل‌های داده:

#### کلاس Appointment:
```python
@dataclass
class Appointment:
    from_time: int          # زمان شروع (Unix timestamp)
    to_time: int            # زمان پایان (Unix timestamp)
    workhour_turn_num: int  # شماره نوبت
    doctor_slug: str = ""   # شناسه دکتر
    center_name: str = ""   # نام مرکز
    service_name: str = ""  # نام سرویس
    
    @property
    def start_datetime(self) -> datetime:
        """تبدیل timestamp به datetime"""
        return datetime.fromtimestamp(self.from_time)
    
    @property
    def time_str(self) -> str:
        """نمایش زمان به صورت رشته"""
        return self.start_datetime.strftime('%Y/%m/%d %H:%M')
```

#### کلاس APIResponse:
```python
@dataclass
class APIResponse:
    status: int                    # کد وضعیت (1 = موفق)
    message: str                   # پیام پاسخ
    data: Optional[dict] = None    # داده‌های اضافی
    error: Optional[str] = None    # پیام خطا
    
    @property
    def is_success(self) -> bool:
        """بررسی موفقیت درخواست"""
        return self.status == 1
```

### Rate Limiting و بهینه‌سازی:

#### تنظیمات پیش‌فرض:
- **فاصله بررسی:** 90 ثانیه
- **تاخیر بین درخواست‌ها:** 1.5 ثانیه
- **روزهای بررسی:** 5 روز
- **محدودیت نوبت‌ها:** 50 نوبت در هر بررسی

#### مدیریت خطای 429:
```python
except httpx.HTTPStatusError as e:
    if e.response.status_code == 429:
        logger.warning("Rate limit hit, waiting 5 seconds...")
        await asyncio.sleep(5)
```

---

## 🚀 راه‌اندازی

### پیش‌نیازها:
- **سیستم عامل:** Ubuntu 18.04+ یا CentOS 7+
- **Python:** 3.9 یا بالاتر
- **حافظه:** حداقل 512MB RAM
- **فضای دیسک:** حداقل 1GB
- **اتصال اینترنت:** پایدار برای API calls

### روش 1: راه‌اندازی خودکار (پیشنهادی)

```bash
# 1. دانلود پروژه
git clone https://github.com/your-username/P24_SlotHunter.git
cd P24_SlotHunter

# 2. اجرای اسکریپت راه‌اندازی
chmod +x server_manager.sh
./server_manager.sh setup

# 3. تنظیم متغیرهای محیطی
./server_manager.sh config

# 4. شروع سرویس
./server_manager.sh start
```

### روش 2: راه‌اندازی دستی

```bash
# 1. ایجاد virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. نصب وابستگی‌ها
pip install -r requirements.txt

# 3. تنظیم متغیرهای محیطی
cp .env.example .env
nano .env

# 4. راه‌اندازی دیتابیس
python -c "
from src.database.database import DatabaseManager
from src.utils.config import Config
import asyncio

async def setup():
    config = Config()
    db = DatabaseManager(config.database_url)
    await db._setup_database()
    print('Database setup complete')

asyncio.run(setup())
"

# 5. اجرای برنامه
python src/main.py
```

### تست راه‌اندازی:

```bash
# بررسی وضعیت سرویس
./server_manager.sh status

# مشاهده لاگ‌ها
./server_manager.sh logs

# تست ربات تلگرام
# به ربات پیام /start بدهید
```

---

## ⚙️ تنظیمات

### فایل .env:
```bash
# ربات تلگرام
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_CHAT_ID=your_chat_id_here

# دیتابیس
DATABASE_URL=sqlite+aiosqlite:///data/slothunter.db

# API
API_BASE_URL=https://apigw.paziresh24.com/booking/v2

# مانیتورینگ
CHECK_INTERVAL=90        # فاصله بررسی (ثانیه)
LOG_LEVEL=INFO          # سطح لاگ

# بهینه‌سازی
REQUEST_DELAY=1.5       # تاخیر بین درخواست‌ها
DAYS_AHEAD=5           # روزهای بررسی
```

### فایل config/config.yaml:
```yaml
# تنظیمات دیتابیس
database:
  url: "sqlite+aiosqlite:///data/slothunter.db"

# تنظیمات API
api:
  base_url: "https://apigw.paziresh24.com/booking/v2"

# تنظیمات تلگرام
telegram:
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  admin_chat_id: ${ADMIN_CHAT_ID}

# تنظیمات مانیتورینگ
monitoring:
  check_interval: 90      # فاصله بررسی (ثانیه)
  max_retries: 3          # تعداد تلاش مجدد
  timeout: 15             # timeout درخواست
  days_ahead: 5           # روزهای بررسی
  request_delay: 1.5      # تاخیر بین درخواست‌ها

# تنظیمات لاگ
logging:
  level: "INFO"
  file: "logs/slothunter.log"
  max_size: "10MB"
  backup_count: 5

# لیست دکترها (اضافه شده توسط ربات)
doctors: []
```

### دریافت توکن ربات تلگرام:

1. **ایجاد ربات:**
   - به [@BotFather](https://t.me/BotFather) پیام دهید
   - دستور `/newbot` را ارسال کنید
   - نام ربات را انتخاب کنید (مثال: SlotHunter Bot)
   - username ربات را انتخاب کنید (مثال: @my_slothunter_bot)
   - توکن دریافتی را کپی کنید

2. **دریافت Chat ID:**
   - به [@userinfobot](https://t.me/userinfobot) پیام دهید
   - Chat ID خود را کپی کنید

3. **تنظیم در .env:**
   ```bash
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ADMIN_CHAT_ID=123456789
   ```

---

## 🤖 ربات تلگرام

### دستورات کاربر:

#### `/start`
شروع ربات و نمایش منوی اصلی
```
🎯 سلام! خوش آمدید

به ربات نوبت‌یاب پذیرش۲۴ خوش آمدید!

🔥 امکانات:
• 👨‍⚕️ مشاهده دکترها - لیست دکترهای موجود
• 📝 اشتراک در دکتر - برای رصد نوبت‌های خالی

💡 نکته: ربات ۲۴/۷ نوبت‌های خالی را رصد می‌کند!
```

#### `/help`
نمایش ��اهنمای کامل
```
📚 راهنمای ربات نوبت‌یاب

🎯 قابلیت‌های اصلی:
👨‍⚕️ مشاهده دکترها
📝 اشتراک در دکتر
🆕 اضافه کردن دکتر

💡 نکات:
• نوبت‌ها سریع تمام می‌شوند، آماده باشید!
• می‌توانید در چندین دکتر همزمان مشترک شوید
```

#### `/doctors`
مشاهده لیست دکترهای موجود

### منوی دائمی:
- **👨‍⚕️ دکترها** - مشاهده و مدیریت دکترها
- **📝 اشتراک‌ها** - مدیریت اشتراک‌های شخصی

### قابلیت‌های پیشرفته:

#### اضافه کردن دکتر:
1. روی "🆕 اضافه کردن دکتر" کلیک کنید
2. لینک صفحه دکتر در پذیرش۲۴ را ارسال کنید
3. ربات خودکار اطلاعات را استخراج می‌کند
4. دکتر به سیستم اضافه می‌شود

**فرمت‌های قابل قبول:**
- `https://www.paziresh24.com/dr/دکتر-نام-خانوادگی-0/`
- `dr/دکتر-نام-خانوادگی-0/`
- `دکتر-نام-خانوادگی-0`

#### مدیریت اشتراک‌ها:
- **اشتراک:** روی نام دکتر کلیک کنید و "📝 اشتراک" را بزنید
- **لغو اشتراک:** از منوی "📝 اشتراک‌ها" دکتر مورد نظر را لغو کنید
- **مشاهده وضعیت:** تعداد اشتراک‌های فعال نمایش داده می‌شود

#### اطلاع‌رسانی نوبت:
```
🎯 نوبت خالی پیدا شد!

👨‍⚕️ دکتر: دکتر احمد محمدی
🏥 مرکز: کلینیک تخصصی قلب
📍 آدرس: تهران، خیابان ولیعصر

📅 نوبت‌های موجود:
🗓️ 2024/12/15:
   ⏰ 08:00 (نوبت #1)
   ⏰ 08:30 (نوبت #2)
   ⏰ 09:00 (نوبت #3)

🔗 لینک رزرو:
https://www.paziresh24.com/dr/doctor-slug/

⚡ سریع عمل کنید! نوبت‌ها ممکن است زود تمام شوند.
```

### کلاس‌های اصلی:

#### SlotHunterBot:
```python
class SlotHunterBot:
    def __init__(self, token: str, db_manager):
        self.token = token
        self.db_manager = db_manager
        self.application = None
        self.handlers = UnifiedTelegramHandlers(db_manager)
    
    async def initialize(self):
        """راه‌اندازی ربات"""
        
    async def start_polling(self):
        """شروع polling"""
        
    async def send_appointment_alert(self, doctor, appointments):
        """ارسال اطلاع‌رسانی نوبت"""
```

#### UnifiedTelegramHandlers:
```python
class UnifiedTelegramHandlers:
    async def start_command(self, update, context):
        """دستور /start"""
        
    async def handle_text_message(self, update, context):
        """مدیریت پیام‌های متنی"""
        
    async def handle_callback(self, update, context):
        """مدیریت callback ها"""
```

---

## 🗄️ دیتابیس

### ساختار جداول:

#### جدول Users:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP
);
```

#### جدول Doctors:
```sql
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    doctor_id VARCHAR(100),
    specialty VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### جدول DoctorCenters:
```sql
CREATE TABLE doctor_centers (
    id INTEGER PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id),
    center_id VARCHAR(100) NOT NULL,
    center_name VARCHAR(200) NOT NULL,
    center_address TEXT,
    center_phone VARCHAR(20),
    user_center_id VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### جدول DoctorServices:
```sql
CREATE TABLE doctor_services (
    id INTEGER PRIMARY KEY,
    center_id INTEGER REFERENCES doctor_centers(id),
    service_id VARCHAR(100) NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    user_center_id VARCHAR(100) NOT NULL,
    price INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### جدول Subscriptions:
```sql
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    doctor_id INTEGER REFERENCES doctors(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, doctor_id)
);
```

#### جدول AppointmentLogs:
```sql
CREATE TABLE appointment_logs (
    id INTEGER PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id),
    appointment_count INTEGER,
    check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);
```

### مدل‌های SQLAlchemy:

#### User Model:
```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime)
    
    # روابط
    subscriptions = relationship("Subscription", back_populates="user")
    
    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
```

#### Doctor Model:
```python
class Doctor(Base):
    __tablename__ = 'doctors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    doctor_id = Column(String(100))
    specialty = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    centers = relationship("DoctorCenter", back_populates="doctor")
    subscriptions = relationship("Subscription", back_populates="doctor")
```

### عملیات دیتابیس:

#### اضافه کردن کاربر:
```python
async def add_user(telegram_id: int, username: str = None, 
                  first_name: str = None, last_name: str = None):
    async with db_manager.session_scope() as session:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        session.add(user)
        await session.commit()
        return user
```

#### اضافه کردن اشتراک:
```python
async def subscribe_user(user_id: int, doctor_id: int):
    async with db_manager.session_scope() as session:
        subscription = Subscription(
            user_id=user_id,
            doctor_id=doctor_id
        )
        session.add(subscription)
        await session.commit()
        return subscription
```

#### دریافت اشتراک‌های فعال:
```python
async def get_active_subscriptions(doctor_id: int):
    async with db_manager.session_scope() as session:
        result = await session.execute(
            select(Subscription)
            .options(selectinload(Subscription.user))
            .filter(
                Subscription.doctor_id == doctor_id,
                Subscription.is_active == True
            )
        )
        return result.scalars().all()
```

---

## 🖥️ مدیریت سرور

### اسکریپت server_manager.sh:

#### دستورات اصلی:
```bash
./server_manager.sh setup      # راه‌اندازی اولیه
./server_manager.sh start      # شروع سرویس
./server_manager.sh stop       # توقف سرویس
./server_manager.sh restart    # ری‌استارت
./server_manager.sh status     # وضعیت سرویس
./server_manager.sh logs       # مشاهده لاگ‌ها
./server_manager.sh health     # بررسی سلامت
./server_manager.sh config     # تنظیمات
./server_manager.sh backup     # پشتیبان‌گیری
./server_manager.sh restore    # بازیابی
```

#### منوی تعاملی:
```bash
./server_manager.sh

P24_SlotHunter Management Menu
==============================

1. 🚀 Start Service
2. 🛑 Stop Service  
3. 🔄 Restart Service
4. 📊 Service Status
5. 📋 Live Logs
6. 🏥 Health Check
7. ⚙️  Configuration
8. 💾 Backup Data
9. 🔧 Advanced Options
0. ❌ Exit

Your choice:
```

#### تنظیمات systemd:
```ini
[Unit]
Description=P24_SlotHunter - Paziresh24 Appointment Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/P24_SlotHunter
Environment=PATH=/home/ubuntu/P24_SlotHunter/venv/bin
ExecStart=/home/ubuntu/P24_SlotHunter/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### مانیتورینگ و لاگ‌ها:

#### ساختار لاگ:
```
2024-12-15 10:30:15 - SlotHunter - INFO - 🚀 شروع P24_SlotHunter
2024-12-15 10:30:16 - SlotHunter - INFO - ✅ دیتابیس راه‌اندازی شد
2024-12-15 10:30:17 - SlotHunter - INFO - ✅ ربات تلگرام راه‌اندازی شد
2024-12-15 10:30:18 - SlotHunter - INFO - 👨‍⚕️ 3 دکتر در دیتابیس (2 فعال)
2024-12-15 10:30:19 - SlotHunter - INFO - 🔍 شروع دور جدید بررسی 2 دکتر...
2024-12-15 10:30:25 - SlotHunter - INFO - 🎯 15 نوبت برای دکتر احمدی پیدا شد!
2024-12-15 10:30:26 - SlotHunter - INFO - 📤 پیام به 3/3 مشترک ارسال شد
```

#### سطوح لاگ:
- **DEBUG:** اطلاعات تفصیلی برای عیب‌یابی
- **INFO:** اطلاعات عمومی عملکرد
- **WARNING:** هشدارها و مشکلات جزئی
- **ERROR:** خطاهای قابل بازیابی
- **CRITICAL:** خطاهای جدی که نیاز به مداخله دارند

#### مانیتورینگ سلامت:
```bash
# بررسی وضعیت سرویس
systemctl status slothunter

# مشاهده لاگ‌های زنده
journalctl -u slothunter -f

# بررسی استفاده منابع
ps aux | grep python
df -h
free -h
```

---

## 🔧 عیب‌یابی

### مشکلات رایج و راه‌حل‌ها:

#### 1. ربات پاسخ نمی‌دهد:
```bash
# بررسی وضعیت سرویس
./server_manager.sh status

# مشاهده لاگ‌های خطا
./server_manager.sh logs | grep ERROR

# ری‌استارت سرویس
./server_manager.sh restart
```

**علل احتمالی:**
- توکن ربات نادرست
- مشکل اتصال اینترنت
- خطا در کد

#### 2. خطای Rate Limiting (429):
```
⚠️ Rate limit hit, waiting 5 seconds...
```

**راه‌حل:**
```bash
# افزایش فاصله بررسی در .env
CHECK_INTERVAL=120

# افزایش تاخیر بین درخواست‌ها
REQUEST_DELAY=2.0

# کاهش روزهای بررسی
DAYS_AHEAD=3
```

#### 3. خطای دیتابیس:
```
sqlite3.OperationalError: database is locked
```

**راه‌حل:**
```bash
# توقف سرویس
./server_manager.sh stop

# حذف فایل lock
rm data/slothunter.db-wal
rm data/slothunter.db-shm

# ری‌استارت
./server_manager.sh start
```

#### 4. خ��ای Virtual Environment:
```
ModuleNotFoundError: No module named 'telegram'
```

**راه‌حل:**
```bash
# فعال‌سازی محیط مجازی
source venv/bin/activate

# نصب مجدد وابستگی‌ها
pip install -r requirements.txt

# ری‌استارت سرویس
./server_manager.sh restart
```

#### 5. خطای Memory:
```
MemoryError: Unable to allocate memory
```

**راه‌حل:**
```bash
# بررسی استفاده حافظه
free -h

# ری‌استارت سیستم
sudo reboot

# کاهش تعداد دکترهای فعال
```

### ابزارهای عیب‌یابی:

#### بررسی لاگ‌ها:
```bash
# لاگ‌های کلی
tail -f logs/slothunter.log

# لاگ‌های systemd
journalctl -u slothunter -f

# لاگ‌های خطا
grep ERROR logs/slothunter.log
```

#### تست اتصال API:
```bash
# تست دستی API
curl -X POST "https://apigw.paziresh24.com/booking/v2/getFreeDays" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "center_id=12345&service_id=67890"
```

#### تست ربات تلگرام:
```bash
# تست توکن
curl "https://api.telegram.org/bot<TOKEN>/getMe"

# ارسال پیام تست
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=Test"
```

---

## 🔒 امنیت

### بهترین شیوه‌های امنیتی:

#### 1. مدیریت متغیرهای محیطی:
```bash
# استفاده از .env برای اطلاعات حساس
TELEGRAM_BOT_TOKEN=your_secret_token
ADMIN_CHAT_ID=your_chat_id

# عدم commit کردن .env
echo ".env" >> .gitignore
```

#### 2. محدودیت دسترسی فایل‌ها:
```bash
# تنظیم مجوزهای مناسب
chmod 600 .env
chmod 755 server_manager.sh
chmod -R 750 src/
```

#### 3. لاگ امن:
```python
# عدم لاگ اطلاعات حساس
logger.info(f"User {user.first_name} subscribed")  # ✅
logger.info(f"Token: {token}")  # ❌
```

#### 4. اعتبارسنجی ورودی:
```python
def validate_doctor_url(url: str) -> bool:
    """اعتبارسنجی URL دکتر"""
    pattern = r'https?://(?:www\.)?paziresh24\.com/dr/[^/]+/?'
    return re.match(pattern, url) is not None
```

#### 5. محدودیت Rate Limiting:
```python
# تنظیمات محافظانه برای جلوگیری از بن شدن
CHECK_INTERVAL = 90  # حداقل 90 ثانیه
REQUEST_DELAY = 1.5  # حداقل 1.5 ثانیه بین درخواست‌ها
```

### تنظیمات Firewall:
```bash
# باز کردن پورت‌های ضروری
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP (اختیاری)
sudo ufw allow 443   # HTTPS (اختیاری)

# بستن پورت‌های غیرضروری
sudo ufw deny 3306   # MySQL
sudo ufw deny 5432   # PostgreSQL
```

### پشتیبان‌گیری امن:
```bash
# پشتیبان‌گیری رمزنگاری شده
./server_manager.sh backup
gpg --symmetric --cipher-algo AES256 backup_*.tar.gz
```

---

## 🚀 توسعه

### محیط توسعه:

#### نصب برای توسعه:
```bash
# کلون پروژه
git clone https://github.com/your-username/P24_SlotHunter.git
cd P24_SlotHunter

# ایجاد محیط مجازی
python3 -m venv venv
source venv/bin/activate

# نصب وابستگی‌های توسعه
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8

# تنظیم pre-commit hooks
pip install pre-commit
pre-commit install
```

#### ساختار کد:

##### استایل کد:
```python
# استفاده از Black برای فرمت کردن
black src/

# بررسی کیفیت کد با flake8
flake8 src/

# Type hints
from typing import List, Optional, Dict

async def get_appointments(doctor_id: int) -> List[Appointment]:
    """دریافت نوبت‌های دکتر"""
    pass
```

##### الگوهای طراحی:
- **Repository Pattern** برای دسترسی به داده
- **Factory Pattern** برای ایجاد API clients
- **Observer Pattern** برای اطلاع‌رسانی
- **Singleton Pattern** برای مدیریت تنظیمات

#### تست‌ها:

##### تست واحد:
```python
import pytest
from src.api.enhanced_paziresh_client import EnhancedPazireshAPI

@pytest.mark.asyncio
async def test_api_client():
    """تست کلاینت API"""
    # Mock doctor object
    doctor = MockDoctor()
    
    # ایجاد کلاینت
    api = EnhancedPazireshAPI(doctor)
    
    # تست متد
    appointments = await api.get_all_available_appointments()
    
    # بررسی نتیجه
    assert isinstance(appointments, list)
```

##### اجرای تست‌ها:
```bash
# اجرای تمام تست‌ها
pytest

# اجرای تست‌های خاص
pytest tests/test_api.py

# تست با coverage
pytest --cov=src tests/
```

### اضافه کردن ویژگی جدید:

#### 1. ایجاد branch جدید:
```bash
git checkout -b feature/new-feature
```

#### 2. پیاده‌سازی ویژگی:
```python
# src/new_module/new_feature.py
class NewFeature:
    """ویژگی جدید"""
    
    def __init__(self):
        pass
    
    async def process(self):
        """پردازش ویژگی"""
        pass
```

#### 3. اضافه کردن تست:
```python
# tests/test_new_feature.py
import pytest
from src.new_module.new_feature import NewFeature

@pytest.mark.asyncio
async def test_new_feature():
    feature = NewFeature()
    result = await feature.process()
    assert result is not None
```

#### 4. به‌روزرسانی مستندات:
```markdown
## ویژگی جدید

### استفاده:
```python
from src.new_module.new_feature import NewFeature

feature = NewFeature()
await feature.process()
```
```

#### 5. ایجاد Pull Request:
```bash
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

### رهنمودهای مشارکت:

#### کیفیت کد:
- استفاده از Type Hints
- نوشتن Docstrings
- پیروی از PEP 8
- تست‌نویسی برای کد جدید

#### Git Workflow:
- استفاده از Conventional Commits
- ایجاد branch برای هر ویژگی
- Code review قبل از merge
- حفظ تاریخچه تمیز

#### مستندسازی:
- به‌روزرسانی README
- اضافه کردن مثال‌ها
- توضیح API جدید
- ترجمه به زبان‌های مختلف

---

## 📊 عملکرد و آمار

### متریک‌های کلیدی:

#### سرعت پردازش:
- **بررسی هر دکتر:** < 10 ثانیه
- **اطلاع‌ر��انی:** < 5 ثانیه
- **پاسخ ربات:** < 2 ثانیه

#### استفاده منابع:
- **RAM:** 50-100 MB
- **CPU:** < 5% در حالت عادی
- **دیسک:** < 100 MB برای دیتابیس
- **شبکه:** 1-5 MB در ساعت

#### آمار API:
- **درخواست‌ها در ساعت:** ~200 (بهینه شده)
- **نرخ موفقیت:** > 95%
- **Rate Limiting:** < 1% از درخواست‌ها

### بهینه‌سازی‌ها:

#### کاهش درخواست‌های API:
```python
# قبل از بهینه‌سازی: 840 درخواست در ساعت
CHECK_INTERVAL = 30  # هر 30 ثانیه
DAYS_AHEAD = 7       # 7 روز

# بعد از بهینه‌سازی: 200 درخواست در ساعت (76% کاهش)
CHECK_INTERVAL = 90  # هر 90 ثانیه
DAYS_AHEAD = 5       # 5 روز
REQUEST_DELAY = 1.5  # تاخیر بین درخواست‌ها
```

#### کش کردن نتایج:
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_cached_appointments(doctor_id: str, date: str):
    """کش نوبت‌ها برای 5 دقیقه"""
    pass
```

---

## 🔮 نقشه راه توسعه

### نسخه فعلی (v1.0):
- ✅ ربات تلگرام پایه
- ✅ رصد نوبت‌های خالی
- ✅ مدیریت چندین دکتر
- ✅ اطلاع‌رسانی فوری
- ✅ بهینه‌سازی Rate Limiting

### نسخه بعدی (v1.1):
- 🔄 رابط وب ادمین
- 🔄 آمار و گزارش‌گیری
- 🔄 پشتیبانی از چندین شهر
- 🔄 فیلتر نوبت‌ها بر اساس زمان
- 🔄 اطلاع‌رسانی صوتی

### نسخه آینده (v2.0):
- 📋 رزرو خودکار نوبت
- 📋 پشتیبانی از سایر سایت‌ها
- 📋 اپلیکیشن موبایل
- 📋 هوش مصنوعی برای پیش‌بینی
- 📋 API عمومی

---

## 📞 پشتیبانی و تماس

### راه‌های ارتباطی:
- 🐛 **گزارش باگ:** [GitHub Issues](https://github.com/your-username/P24_SlotHunter/issues)
- 💡 **پیشنهادات:** [GitHub Discussions](https://github.com/your-username/P24_SlotHunter/discussions)
- 📧 **ایمیل:** your-email@example.com
- 💬 **تلگرام:** @your_username

### مشارکت:
- 🤝 **Fork** کنید و **Pull Request** ایجاد کنید
- 📝 **مستندات** را بهبود دهید
- 🧪 **تست** بنویسید
- 🌍 **ترجمه** کنید

### حمایت مالی:
- ☕ **Buy me a coffee:** [link]
- 💳 **PayPal:** [link]
- 🪙 **Crypto:** [addresses]

---

## 📄 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. برای جزئیات بیشتر فایل [LICENSE](LICENSE) را مطالعه کنید.

### خلاصه لایسنس:
- ✅ استفاده تجاری مجاز
- ✅ تغییر و توزیع مجاز
- ✅ استفاده خصوصی مجاز
- ❌ هیچ ضمانتی ارائه نمی‌شود
- ❌ مسئولیتی بر عهده سازنده نیست

---

## ⚠️ اخلاق و مسئولیت

### استفاده مسئولانه:
- 🚫 **سرور را overload نکنید** - از تنظیمات پیش‌فرض استفاده کنید
- 🚫 **برای اهداف تجاری استفاده نکنید** - فقط استفاده شخصی
- 🚫 **اطلاعات شخصی را ذخیره نکنید** - حریم خصوصی را رعایت کنید
- ✅ **قوانین پذیرش۲۴ را رعایت کنید**
- ✅ **فقط برای نیازهای واقعی استفاده کنید**

### محدودیت‌ها:
- این ابزار فقط برای تسهیل دسترسی به نوبت‌های موجود است
- هیچ تضمینی برای دریافت نوبت وجود ندارد
- استفاده از این ابزار به مسئولیت خود کاربر است
- سازنده هیچ مسئولیتی در قبال عواقب استفاده ندارد

---

**ساخته شده با ❤️ برای بهبود دسترسی به خدمات پزشکی**

*آخرین به‌روزرسانی: دسامبر 2024*