# P24_SlotHunter - نقشه راه توسعه پروژه

## 📋 خلاصه پروژه

**هدف:** توسعه ربات هوشمند برای نظارت خودکار بر نوبت‌های خالی دکترهای مشخص در سایت پذیرش۲۴ و اطلاع‌رسانی فوری از طریق تلگرام

**محدوده:** ۲-۳ دکتر (برای حداکثر سرعت و کارایی)  
**سرعت مورد انتظار:** ۹ از ۱۰ (زمان پردازش: ۱-۳ ثانیه)  

---

## 🛠 تکنولوژی‌های اصلی

### Core Technologies
- **زبان برنامه‌نویسی:** Python 3.9+
- **Web Scraping:** Playwright (پیشنهاد جدید) / Selenium WebDriver + BeautifulSoup
- **ربات تلگرام:** python-telegram-bot v20+
- **دیتابیس:** SQLite (development) / PostgreSQL (production)
- **Async Processing:** asyncio + aiohttp
- **Caching:** Redis (پیشنهاد جدید)
- **Monitoring:** Prometheus + Grafana (اختیاری)
- **Containerization:** Docker + Docker Compose

### Dependencies
```txt
# Core Dependencies
playwright>=1.40.0
beautifulsoup4>=4.12.0
python-telegram-bot>=20.7
asyncio
aiohttp>=3.9.0
sqlalchemy>=2.0.0
alembic>=1.13.0
redis>=5.0.0
pydantic>=2.5.0
pyyaml>=6.0.1

# Development & Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.7.0

# Monitoring (Optional)
prometheus-client>=0.19.0
structlog>=23.2.0

# Production
gunicorn>=21.2.0
uvicorn>=0.24.0
```

---

## 📁 ساختار پروژه (بهبود یافته)

```
P24_SlotHunter/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # تنظیمات مرکزی با Pydantic
│   │   ├── exceptions.py          # Exception classes سفارشی
│   │   └── constants.py           # ثوابت پروژه
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── base_scraper.py        # Abstract base class
│   │   ├── paziresh_scraper.py    # هسته اصلی scraping
│   │   ├── appointment_parser.py  # پارس کردن نوبت‌ها
│   │   ├── session_manager.py     # مدیریت session و cookie
│   │   └── retry_handler.py       # مدیریت retry و circuit breaker
│   ├── telegram/
│   │   ├── __init__.py
│   │   ├── bot_handler.py         # مدیریت ربات تلگرام
│   │   ├── message_formatter.py   # فرمت پیام‌ها
│   │   ├── user_manager.py        # مدیریت کاربران
│   │   ├── keyboards.py           # کیبوردهای inline
│   │   └── middleware.py          # Middleware برای logging و auth
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py              # مدل‌های SQLAlchemy
│   │   ├── database.py            # اتصال و عملیات DB
│   │   ├── repositories.py        # Repository pattern
│   │   └── migrations/            # Alembic migrations
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── task_scheduler.py      # زمان‌بندی چک‌ها
│   │   ├── job_manager.py         # مدیریت job ها
│   │   └── health_checker.py      # بررسی سلامت سیستم
│   ├── cache/
│   │   ├── __init__.py
│   │   ├── redis_client.py        # Redis client
│   │   └── cache_manager.py       # مدیریت cache
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── metrics.py             # Prometheus metrics
│   │   ├── logger.py              # Structured logging
│   │   └���─ health.py              # Health check endpoints
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py             # توابع کمکی
│       ├── validators.py          # اعتبارسنجی داده‌ها
│       └── decorators.py          # Decorators مفید
├── tests/
│   ├── unit/                      # تست‌های واحد
│   ├── integration/               # تست‌های یکپارچگی
│   ├── e2e/                       # تست‌های end-to-end
│   └── fixtures/                  # Test fixtures
├── config/
│   ├── config.yaml                # تنظیمات اصلی
│   ├── config.dev.yaml            # تنظیمات development
│   ├── config.prod.yaml           # تنظیمات production
│   ├── doctors.json               # لیست دکترها
│   └── logging.yaml               # تنظیمات logging
├── docker/
│   ├── Dockerfile                 # Docker image اصلی
│   ├── Dockerfile.dev             # Development image
│   └── docker-compose.yml         # Multi-service setup
├── scripts/
│   ├── setup.sh                   # راه‌اندازی اولیه
│   ├── deploy.sh                  # اسکریپت deployment
│   └── backup.sh                  # پشتیبان‌گیری
├── docs/
│   ├── API.md                     # مستندات API
│   ├── DEPLOYMENT.md              # راهنمای deployment
│   └── TROUBLESHOOTING.md         # عیب‌یابی
├── requirements/
│   ├── base.txt                   # Dependencies اصلی
│   ├── dev.txt                    # Development dependencies
│   └── prod.txt                   # Production dependencies
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Continuous Integration
│       └── cd.yml                 # Continuous Deployment
├── main.py                        # Entry point اصلی
├── README.md
├── CHANGELOG.md
└── LICENSE
```

---

## 🚀 مراحل پیاده‌سازی (۶ فاز)

### 📅 فاز ۱: راه‌اندازی پایه و Infrastructure (روز ۱-۲)

#### ۱.۱ تنظیم محیط توسعه
- [ ] نصب Python 3.9+ و virtual environment
- [ ] نصب Playwright و browsers
- [ ] راه‌اندازی Redis (Docker)
- [ ] تنظیم Git hooks و pre-commit
- [ ] ایجاد ساختار فولدربندی

#### ۱.۲ پیاده‌سازی Core Infrastructure
```python
# src/core/config.py
from pydantic import BaseSettings, Field
from typing import List, Optional

class Settings(BaseSettings):
    # Telegram Bot
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_admin_chat_id: int = Field(..., env="TELEGRAM_ADMIN_CHAT_ID")
    
    # Database
    database_url: str = Field("sqlite:///./data/appointments.db", env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    
    # Scraping
    check_interval: int = Field(30, description="Check interval in seconds")
    request_timeout: int = Field(10, description="Request timeout in seconds")
    max_retries: int = 3
    rate_limit: float = 0.5  # Requests per second
    
    # Monitoring
    enable_metrics: bool = Field(False, env="ENABLE_METRICS")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

#### ۱.۳ پیاده‌سازی Logging و Monitoring
```python
# src/monitoring/logger.py
import structlog
from typing import Any, Dict

def setup_logging(log_level: str = "INFO") -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

**تحویلی فاز ۱:**
- محیط توسعه کامل
- ساختار پروژه
- سیستم logging
- تست‌های اولیه

---

### 📅 فاز ۲: پیاده‌سازی Scraper پیشرفته (روز ۳-۴)

#### ۲.۱ Base Scraper با Playwright
```python
# src/scraper/base_scraper.py
from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Browser, Page
from typing import List, Dict, Any, Optional
import asyncio

class BaseScraper(ABC):
    def __init__(self, headless: bool = True, timeout: int = 10000):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.page = await self.browser.new_page()
        await self.page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    @abstractmethod
    async def scrape_appointments(self, doctor_url: str) -> List[Dict[str, Any]]:
        pass
```

#### ۲.۲ Paziresh24 Scraper
```python
# src/scraper/paziresh_scraper.py
from .base_scraper import BaseScraper
from .retry_handler import RetryHandler
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger(__name__)

class PazireshScraper(BaseScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry_handler = RetryHandler(max_retries=3, backoff_factor=2)
    
    @RetryHandler.with_retry
    async def scrape_appointments(self, doctor_url: str) -> List[Dict[str, Any]]:
        """استخراج نوبت‌های موجود از صفحه دکتر"""
        try:
            await self.page.goto(doctor_url, wait_until='networkidle')
            
            # انتظار برای بارگذاری کامل صفحه
            await self.page.wait_for_selector('.appointment-section', timeout=self.timeout)
            
            # استخراج نوبت‌های موجود
            appointments = await self.page.evaluate("""
                () => {
                    const appointments = [];
                    const slots = document.querySelectorAll('.available-slot');
                    
                    slots.forEach(slot => {
                        const date = slot.querySelector('.date')?.textContent?.trim();
                        const time = slot.querySelector('.time')?.textContent?.trim();
                        const price = slot.querySelector('.price')?.textContent?.trim();
                        
                        if (date && time) {
                            appointments.push({
                                date: date,
                                time: time,
                                price: price || 'نامشخص',
                                available: true,
                                scraped_at: new Date().toISOString()
                            });
                        }
                    });
                    
                    return appointments;
                }
            """)
            
            logger.info("Appointments scraped successfully", 
                       doctor_url=doctor_url, 
                       count=len(appointments))
            
            return appointments
            
        except Exception as e:
            logger.error("Failed to scrape appointments", 
                        doctor_url=doctor_url, 
                        error=str(e))
            raise
```

#### ۲.۳ Retry Handler و Circuit Breaker
```python
# src/scraper/retry_handler.py
import asyncio
import time
from functools import wraps
from typing import Callable, Any
import structlog

logger = structlog.get_logger(__name__)

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        if self.state == 'CLOSED':
            return True
        elif self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

class RetryHandler:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.circuit_breaker = CircuitBreaker()
    
    @staticmethod
    def with_retry(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            if not self.retry_handler.circuit_breaker.can_execute():
                raise Exception("Circuit breaker is OPEN")
            
            last_exception = None
            for attempt in range(self.retry_handler.max_retries + 1):
                try:
                    result = await func(self, *args, **kwargs)
                    self.retry_handler.circuit_breaker.record_success()
                    return result
                except Exception as e:
                    last_exception = e
                    if attempt < self.retry_handler.max_retries:
                        wait_time = self.retry_handler.backoff_factor ** attempt
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s", 
                                     error=str(e))
                        await asyncio.sleep(wait_time)
                    else:
                        self.retry_handler.circuit_breaker.record_failure()
            
            raise last_exception
        return wrapper
```

**تحویلی فاز ۲:**
- Scraper کامل با Playwright
- سیستم retry و circuit breaker
- تست‌های scraping روی ۱ دکتر
- اندازه‌گیری performance

---

### 📅 فاز ۳: توسعه ربات تلگرام پیشرفته (روز ۵-۶)

#### ۳.۱ Bot Handler با Middleware
```python
# src/telegram/bot_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from .middleware import LoggingMiddleware, AuthMiddleware
from .user_manager import UserManager
from .message_formatter import MessageFormatter
import structlog

logger = structlog.get_logger(__name__)

class TelegramBot:
    def __init__(self, token: str, user_manager: UserManager):
        self.token = token
        self.user_manager = user_manager
        self.formatter = MessageFormatter()
        self.app = None
    
    async def setup(self):
        """راه‌اندازی ربات و handlers"""
        self.app = Application.builder().token(self.token).build()
        
        # اضافه کردن middleware
        self.app.add_handler(LoggingMiddleware())
        self.app.add_handler(AuthMiddleware(self.user_manager))
        
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.app.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        # Callback handlers
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور شروع کار با ربات"""
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        # ثبت کاربر در دیتابیس
        await self.user_manager.register_user(user_id, username)
        
        welcome_message = self.formatter.format_welcome_message()
        keyboard = self.formatter.get_main_keyboard()
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اشتراک در دکتر"""
        user_id = update.effective_user.id
        
        # نمایش لیست دکترهای موجود
        doctors = await self.user_manager.get_available_doctors()
        keyboard = self.formatter.get_doctors_keyboard(doctors)
        
        await update.message.reply_text(
            "🔍 لطفاً دکتر مورد نظر خود را انتخاب کنید:",
            reply_markup=keyboard
        )
    
    async def notify_appointment_available(self, user_id: int, doctor_info: dict, appointment: dict):
        """اطلاع‌رسانی نوبت خالی"""
        message = self.formatter.format_appointment_notification(doctor_info, appointment)
        keyboard = self.formatter.get_appointment_keyboard(doctor_info['url'])
        
        try:
            await self.app.bot.send_message(
                chat_id=user_id,
                text=message,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            logger.info("Notification sent successfully", user_id=user_id)
        except Exception as e:
            logger.error("Failed to send notification", user_id=user_id, error=str(e))
```

#### ۳.۲ Message Formatter
```python
# src/telegram/message_formatter.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, List, Any
from datetime import datetime

class MessageFormatter:
    def format_welcome_message(self) -> str:
        return """
🎯 <b>به ربات نوبت‌گیری پذیرش۲۴ خوش آمدید!</b>

این ربات به شما کمک می‌کند تا از نوبت‌های خالی دکترهای مورد نظرتان در سایت پذیرش۲۴ مطلع شوید.

📋 <b>دستورات موجود:</b>
• /subscribe - ا��تراک در دکتر
• /unsubscribe - لغو اشتراک
• /status - وضعیت اشتراک‌ها
• /help - راهنما

⚡ <b>ویژگی‌ها:</b>
• نظارت ۲۴/۷ بر نوبت‌های خالی
• اطلاع‌رسانی فوری (کمتر از ۱ دقیقه)
• پشتیبانی از چندین دکتر همزمان
• رابط کاربری ساده و کاربرپسند

برای شروع، از دستور /subscribe استفاده کنید.
        """
    
    def format_appointment_notification(self, doctor_info: Dict, appointment: Dict) -> str:
        return f"""
🎯 <b>نوبت خالی پیدا شد!</b>

👨‍⚕️ <b>دکتر:</b> {doctor_info['name']}
🏥 <b>تخصص:</b> {doctor_info['specialty']}
📅 <b>تاریخ:</b> {appointment['date']}
🕐 <b>ساعت:</b> {appointment['time']}
💰 <b>هزینه:</b> {appointment['price']}

⏰ <b>زمان یافت نوبت:</b> {datetime.now().strftime('%H:%M:%S')}

⚠️ <b>توجه:</b> برای رزرو نوبت، سریعاً روی دکمه زیر کلیک کنید.
        """
    
    def get_main_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("🔍 اشتراک در دکتر", callback_data="subscribe")],
            [InlineKeyboardButton("📋 وضعیت اشتراک‌ها", callback_data="status")],
            [InlineKeyboardButton("❌ لغو اشتراک", callback_data="unsubscribe")],
            [InlineKeyboardButton("❓ راهنما", callback_data="help")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_doctors_keyboard(self, doctors: List[Dict]) -> InlineKeyboardMarkup:
        keyboard = []
        for doctor in doctors:
            keyboard.append([
                InlineKeyboardButton(
                    f"👨‍⚕️ {doctor['name']}", 
                    callback_data=f"subscribe_doctor_{doctor['id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
        return InlineKeyboardMarkup(keyboard)
    
    def get_appointment_keyboard(self, doctor_url: str) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("🔗 رزرو نوبت", url=doctor_url)],
            [InlineKeyboardButton("🔄 بررسی مجدد", callback_data="refresh_appointments")]
        ]
        return InlineKeyboardMarkup(keyboard)
```

**تحویلی فاز ۳:**
- ربات تلگرام کامل با UI پیشرفته
- سیستم middleware و logging
- مدیریت کاربران
- تست‌های تعامل با ربات

---

### 📅 فاز ۴: دیتابیس و Cache Layer (روز ۷-۸)

#### ۴.۱ Database Models
```python
# src/database/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    notification_preferences = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user")

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), unique=True, nullable=False)
    specialty = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime, nullable=True)
    check_interval = Column(Integer, default=30)  # seconds
    success_rate = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    notification_count = Column(Integer, default=0)
    last_notification = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    doctor = relationship("Doctor", back_populates="subscriptions")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(String(20), nullable=False)
    appointment_time = Column(String(20), nullable=False)
    price = Column(String(50), nullable=True)
    is_available = Column(Boolean, default=True)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    notification_sent = Column(Boolean, default=False)
    
    # Relationships
    doctor = relationship("Doctor", back_populates="appointments")

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    component = Column(String(50), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### ۴.۲ Repository Pattern
```python
# src/database/repositories.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from .models import User, Doctor, Subscription, Appointment
from datetime import datetime, timedelta

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, telegram_id: int, username: str = None, 
                         first_name: str = None, last_name: str = None) -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()
    
    async def get_active_subscribers_for_doctor(self, doctor_id: int) -> List[User]:
        return self.db.query(User).join(Subscription).filter(
            and_(
                Subscription.doctor_id == doctor_id,
                Subscription.is_active == True,
                User.is_active == True
            )
        ).all()

class DoctorRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_doctor(self, name: str, url: str, specialty: str = None, 
                           location: str = None) -> Doctor:
        doctor = Doctor(
            name=name,
            url=url,
            specialty=specialty,
            location=location
        )
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor
    
    async def get_active_doctors(self) -> List[Doctor]:
        return self.db.query(Doctor).filter(Doctor.is_active == True).all()
    
    async def update_last_checked(self, doctor_id: int, success: bool = True):
        doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if doctor:
            doctor.last_checked = datetime.utcnow()
            if success:
                doctor.success_rate = min(1.0, doctor.success_rate + 0.01)
            else:
                doctor.success_rate = max(0.0, doctor.success_rate - 0.05)
            self.db.commit()

class AppointmentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def save_appointments(self, doctor_id: int, appointments: List[Dict[str, Any]]):
        # حذف نوبت‌های قدیمی
        self.db.query(Appointment).filter(Appointment.doctor_id == doctor_id).delete()
        
        # اضافه کردن نوبت‌های جدید
        for apt in appointments:
            appointment = Appointment(
                doctor_id=doctor_id,
                appointment_date=apt['date'],
                appointment_time=apt['time'],
                price=apt.get('price', 'نامشخص'),
                is_available=True
            )
            self.db.add(appointment)
        
        self.db.commit()
    
    async def get_new_appointments(self, doctor_id: int, 
                                  since: datetime = None) -> List[Appointment]:
        query = self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.is_available == True,
                Appointment.notification_sent == False
            )
        )
        
        if since:
            query = query.filter(Appointment.first_seen >= since)
        
        return query.all()
```

#### ۴.۳ Redis Cache Manager
```python
# src/cache/cache_manager.py
import redis.asyncio as redis
import json
from typing import Any, Optional, List, Dict
from datetime import timedelta
import structlog

logger = structlog.get_logger(__name__)

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
    
    async def connect(self):
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        await self.redis_client.ping()
        logger.info("Connected to Redis successfully")
    
    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
    
    async def set_appointments(self, doctor_id: int, appointments: List[Dict], 
                              expire: int = 300):
        """ذخیره نوبت‌ها در cache"""
        key = f"appointments:doctor:{doctor_id}"
        value = json.dumps(appointments, ensure_ascii=False)
        await self.redis_client.setex(key, expire, value)
    
    async def get_appointments(self, doctor_id: int) -> Optional[List[Dict]]:
        """دریافت نوبت‌ها از cache"""
        key = f"appointments:doctor:{doctor_id}"
        value = await self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set_doctor_status(self, doctor_id: int, status: str, expire: int = 60):
        """وضعیت دکتر (checking, success, error)"""
        key = f"doctor:status:{doctor_id}"
        await self.redis_client.setex(key, expire, status)
    
    async def get_doctor_status(self, doctor_id: int) -> Optional[str]:
        key = f"doctor:status:{doctor_id}"
        return await self.redis_client.get(key)
    
    async def increment_notification_count(self, user_id: int, doctor_id: int):
        """شمارش تعداد اطلاع‌رسانی‌ها"""
        key = f"notifications:{user_id}:{doctor_id}"
        await self.redis_client.incr(key)
        await self.redis_client.expire(key, 86400)  # 24 hours
    
    async def get_notification_count(self, user_id: int, doctor_id: int) -> int:
        key = f"notifications:{user_id}:{doctor_id}"
        count = await self.redis_client.get(key)
        return int(count) if count else 0
```

**تحویلی فاز ۴:**
- م��ل‌های دیتابیس کامل
- Repository pattern
- Redis cache layer
- Migration scripts
- تست‌های دیتابیس

---

### 📅 فاز ۵: Async Scheduler و Orchestration (روز ۹-۱۰)

#### ۵.۱ Task Scheduler
```python
# src/scheduler/task_scheduler.py
import asyncio
from typing import List, Dict, Callable, Any
from datetime import datetime, timedelta
import structlog
from ..scraper.paziresh_scraper import PazireshScraper
from ..database.repositories import DoctorRepository, AppointmentRepository, UserRepository
from ..telegram.bot_handler import TelegramBot
from ..cache.cache_manager import CacheManager
from ..monitoring.metrics import MetricsCollector

logger = structlog.get_logger(__name__)

class AppointmentScheduler:
    def __init__(self, 
                 scraper: PazireshScraper,
                 telegram_bot: TelegramBot,
                 cache_manager: CacheManager,
                 doctor_repo: DoctorRepository,
                 appointment_repo: AppointmentRepository,
                 user_repo: UserRepository,
                 metrics: MetricsCollector):
        
        self.scraper = scraper
        self.telegram_bot = telegram_bot
        self.cache_manager = cache_manager
        self.doctor_repo = doctor_repo
        self.appointment_repo = appointment_repo
        self.user_repo = user_repo
        self.metrics = metrics
        
        self.running = False
        self.tasks = {}
        self.check_interval = 30  # seconds
    
    async def start(self):
        """شروع scheduler"""
        self.running = True
        logger.info("Starting appointment scheduler")
        
        # دریافت لیست دکترهای فعال
        doctors = await self.doctor_repo.get_active_doctors()
        
        # ایجاد task برای هر دکتر
        for doctor in doctors:
            task = asyncio.create_task(self.monitor_doctor(doctor))
            self.tasks[doctor.id] = task
        
        # Task نظارت بر سلامت سیستم
        health_task = asyncio.create_task(self.health_monitor())
        self.tasks['health'] = health_task
        
        # انتظار برای تمام task ها
        await asyncio.gather(*self.tasks.values(), return_exceptions=True)
    
    async def stop(self):
        """توقف scheduler"""
        self.running = False
        logger.info("Stopping appointment scheduler")
        
        # لغو تمام task ها
        for task in self.tasks.values():
            task.cancel()
        
        # انتظار برای تمام شدن task ها
        await asyncio.gather(*self.tasks.values(), return_exceptions=True)
    
    async def monitor_doctor(self, doctor):
        """نظارت مداوم بر یک دکتر"""
        logger.info(f"Starting monitoring for doctor {doctor.name}", doctor_id=doctor.id)
        
        while self.running:
            try:
                start_time = datetime.utcnow()
                
                # تنظیم وضعیت در cache
                await self.cache_manager.set_doctor_status(doctor.id, "checking")
                
                # بررسی نوبت‌های موجود
                async with self.scraper as scraper:
                    appointments = await scraper.scrape_appointments(doctor.url)
                
                # مقایسه با نوبت‌های قبلی
                cached_appointments = await self.cache_manager.get_appointments(doctor.id)
                new_appointments = self.find_new_appointments(appointments, cached_appointments)
                
                if new_appointments:
                    logger.info(f"Found {len(new_appointments)} new appointments", 
                               doctor_id=doctor.id)
                    
                    # ذخیره در دیتابیس
                    await self.appointment_repo.save_appointments(doctor.id, appointments)
                    
                    # اطلاع‌رسانی به کاربران
                    await self.notify_subscribers(doctor, new_appointments)
                
                # بروزرسانی cache
                await self.cache_manager.set_appointments(doctor.id, appointments)
                await self.cache_manager.set_doctor_status(doctor.id, "success")
                
                # بروزرسانی آمار دکتر
                await self.doctor_repo.update_last_checked(doctor.id, success=True)
                
                # ثبت metrics
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                self.metrics.record_scraping_duration(doctor.id, processing_time)
                self.metrics.record_appointments_found(doctor.id, len(appointments))
                
                logger.info(f"Successfully checked doctor {doctor.name}", 
                           doctor_id=doctor.id, 
                           appointments_count=len(appointments),
                           processing_time=processing_time)
                
            except Exception as e:
                logger.error(f"Error monitoring doctor {doctor.name}", 
                           doctor_id=doctor.id, 
                           error=str(e))
                
                await self.cache_manager.set_doctor_status(doctor.id, "error")
                await self.doctor_repo.update_last_checked(doctor.id, success=False)
                self.metrics.record_scraping_error(doctor.id)
            
            # انتظار تا چک بعدی
            await asyncio.sleep(self.check_interval)
    
    def find_new_appointments(self, current: List[Dict], cached: List[Dict]) -> List[Dict]:
        """یافتن نوبت‌های جدید"""
        if not cached:
            return current
        
        cached_set = {(apt['date'], apt['time']) for apt in cached}
        new_appointments = []
        
        for apt in current:
            if (apt['date'], apt['time']) not in cached_set:
                new_appointments.append(apt)
        
        return new_appointments
    
    async def notify_subscribers(self, doctor, appointments: List[Dict]):
        """اطلاع‌رسانی به مشترکین"""
        subscribers = await self.user_repo.get_active_subscribers_for_doctor(doctor.id)
        
        for user in subscribers:
            # بررسی محدودیت تعداد اطلاع‌رسانی
            notification_count = await self.cache_manager.get_notification_count(
                user.telegram_id, doctor.id
            )
            
            if notification_count < 10:  # حداکثر 10 اطلاع‌رسانی در روز
                for appointment in appointments:
                    try:
                        await self.telegram_bot.notify_appointment_available(
                            user.telegram_id, 
                            {
                                'name': doctor.name,
                                'specialty': doctor.specialty,
                                'url': doctor.url
                            },
                            appointment
                        )
                        
                        await self.cache_manager.increment_notification_count(
                            user.telegram_id, doctor.id
                        )
                        
                        self.metrics.record_notification_sent(user.telegram_id, doctor.id)
                        
                    except Exception as e:
                        logger.error("Failed to send notification", 
                                   user_id=user.telegram_id, 
                                   doctor_id=doctor.id, 
                                   error=str(e))
    
    async def health_monitor(self):
        """نظارت بر سلامت سیستم"""
        while self.running:
            try:
                # بررسی وضعیت Redis
                await self.cache_manager.redis_client.ping()
                
                # بررسی وضعیت دیتابیس
                doctors = await self.doctor_repo.get_active_doctors()
                
                # بررسی task های در حال اجرا
                active_tasks = sum(1 for task in self.tasks.values() if not task.done())
                
                logger.info("System health check", 
                           active_doctors=len(doctors),
                           active_tasks=active_tasks)
                
                self.metrics.record_system_health(len(doctors), active_tasks)
                
            except Exception as e:
                logger.error("Health check failed", error=str(e))
            
            await asyncio.sleep(60)  # هر دقیقه
```

#### ۵.۲ Metrics Collector
```python
# src/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from typing import Dict, Any
import time

class MetricsCollector:
    def __init__(self):
        # Counters
        self.scraping_total = Counter('scraping_requests_total', 
                                     'Total scraping requests', 
                                     ['doctor_id', 'status'])
        
        self.notifications_sent = Counter('notifications_sent_total',
                                         'Total notifications sent',
                                         ['user_id', 'doctor_id'])
        
        self.appointments_found = Counter('appointments_found_total',
                                         'Total appointments found',
                                         ['doctor_id'])
        
        # Histograms
        self.scraping_duration = Histogram('scraping_duration_seconds',
                                          'Time spent scraping',
                                          ['doctor_id'])
        
        # Gauges
        self.active_doctors = Gauge('active_doctors_count',
                                   'Number of active doctors being monitored')
        
        self.active_tasks = Gauge('active_tasks_count',
                                 'Number of active monitoring tasks')
        
        self.system_uptime = Gauge('system_uptime_seconds',
                                  'System uptime in seconds')
        
        self.start_time = time.time()
    
    def record_scraping_duration(self, doctor_id: int, duration: float):
        self.scraping_duration.labels(doctor_id=str(doctor_id)).observe(duration)
        self.scraping_total.labels(doctor_id=str(doctor_id), status='success').inc()
    
    def record_scraping_error(self, doctor_id: int):
        self.scraping_total.labels(doctor_id=str(doctor_id), status='error').inc()
    
    def record_notification_sent(self, user_id: int, doctor_id: int):
        self.notifications_sent.labels(
            user_id=str(user_id), 
            doctor_id=str(doctor_id)
        ).inc()
    
    def record_appointments_found(self, doctor_id: int, count: int):
        self.appointments_found.labels(doctor_id=str(doctor_id)).inc(count)
    
    def record_system_health(self, doctors_count: int, tasks_count: int):
        self.active_doctors.set(doctors_count)
        self.active_tasks.set(tasks_count)
        self.system_uptime.set(time.time() - self.start_time)
    
    def start_metrics_server(self, port: int = 8000):
        start_http_server(port)
```

**تحویلی فاز ۵:**
- Async scheduler کامل
- سیستم monitoring و metrics
- Health check mechanism
- Performance optimization
- تست‌های load testing

---

### 📅 فاز ۶: تست، Deployment و Documentation (روز ۱۱-۱۴)

#### ۶.۱ Test Suite
```python
# tests/integration/test_appointment_flow.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.scheduler.task_scheduler import AppointmentScheduler

@pytest.mark.asyncio
async def test_complete_appointment_flow():
    """تست کامل فرآیند یافتن و اطلاع‌رسانی نوبت"""
    
    # Mock dependencies
    scraper = AsyncMock()
    telegram_bot = AsyncMock()
    cache_manager = AsyncMock()
    doctor_repo = AsyncMock()
    appointment_repo = AsyncMock()
    user_repo = AsyncMock()
    metrics = MagicMock()
    
    # Setup test data
    test_doctor = MagicMock()
    test_doctor.id = 1
    test_doctor.name = "دکتر تست"
    test_doctor.url = "https://test.com"
    
    test_appointments = [
        {'date': '1403/01/15', 'time': '10:00', 'price': '200000'},
        {'date': '1403/01/15', 'time': '10:30', 'price': '200000'}
    ]
    
    test_users = [MagicMock()]
    test_users[0].telegram_id = 123456789
    
    # Configure mocks
    scraper.scrape_appointments.return_value = test_appointments
    cache_manager.get_appointments.return_value = []  # No cached appointments
    user_repo.get_active_subscribers_for_doctor.return_value = test_users
    cache_manager.get_notification_count.return_value = 0
    
    # Create scheduler
    scheduler = AppointmentScheduler(
        scraper, telegram_bot, cache_manager,
        doctor_repo, appointment_repo, user_repo, metrics
    )
    
    # Test the monitoring process
    await scheduler.monitor_doctor(test_doctor)
    
    # Verify scraping was called
    scraper.scrape_appointments.assert_called_once_with(test_doctor.url)
    
    # Verify appointments were saved
    appointment_repo.save_appointments.assert_called_once()
    
    # Verify notifications were sent
    assert telegram_bot.notify_appointment_available.call_count == 2
```

#### ۶.۲ Docker Configuration
```dockerfile
# docker/Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright browsers
RUN pip install playwright==1.40.0
RUN playwright install chromium
RUN playwright install-deps

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY main.py ./

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: p24-slothunter
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/p24_slothunter
      - REDIS_URL=redis://redis:6379
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_ADMIN_CHAT_ID=${TELEGRAM_ADMIN_CHAT_ID}
      - LOG_LEVEL=INFO
      - ENABLE_METRICS=true
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    ports:
      - "8000:8000"  # Metrics endpoint
    depends_on:
      - postgres
      - redis
    networks:
      - p24-network

  postgres:
    image: postgres:15-alpine
    container_name: p24-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=p24_slothunter
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - p24-network

  redis:
    image: redis:7-alpine
    container_name: p24-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - p24-network

  prometheus:
    image: prom/prometheus:latest
    container_name: p24-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - p24-network

  grafana:
    image: grafana/grafana:latest
    container_name: p24-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana:/etc/grafana/provisioning
    networks:
      - p24-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  p24-network:
    driver: bridge
```

#### ۶.۳ Deployment Scripts
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 Starting P24_SlotHunter deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it first."
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Build and start services
echo "🔨 Building and starting services..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec app python -m alembic upgrade head

# Check service health
echo "🏥 Checking service health..."
if curl -f http://localhost:8000/health; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed!"
    docker-compose logs app
    exit 1
fi

echo "🎉 P24_SlotHunter is now running!"
echo "📊 Metrics: http://localhost:9090"
echo "📈 Grafana: http://localhost:3000"
```

#### ۶.۴ Main Application Entry Point
```python
# main.py
import asyncio
import signal
import sys
from contextlib import asynccontextmanager
from src.core.config import settings
from src.database.database import DatabaseManager
from src.cache.cache_manager import CacheManager
from src.scraper.paziresh_scraper import PazireshScraper
from src.telegram.bot_handler import TelegramBot
from src.scheduler.task_scheduler import AppointmentScheduler
from src.monitoring.logger import setup_logging
from src.monitoring.metrics import MetricsCollector
import structlog

# Setup logging
setup_logging(settings.log_level)
logger = structlog.get_logger(__name__)

class Application:
    def __init__(self):
        self.db_manager = None
        self.cache_manager = None
        self.telegram_bot = None
        self.scheduler = None
        self.metrics = None
        self.running = False
    
    async def startup(self):
        """راه‌اندازی اجزای سیستم"""
        logger.info("Starting P24_SlotHunter application")
        
        try:
            # Database
            self.db_manager = DatabaseManager(settings.database_url)
            await self.db_manager.connect()
            
            # Cache
            self.cache_manager = CacheManager(settings.redis_url)
            await self.cache_manager.connect()
            
            # Metrics
            if settings.enable_metrics:
                self.metrics = MetricsCollector()
                self.metrics.start_metrics_server(8000)
            
            # Telegram Bot
            from src.database.repositories import UserRepository
            user_repo = UserRepository(self.db_manager.get_session())
            self.telegram_bot = TelegramBot(settings.telegram_bot_token, user_repo)
            await self.telegram_bot.setup()
            
            # Scheduler
            from src.database.repositories import DoctorRepository, AppointmentRepository
            doctor_repo = DoctorRepository(self.db_manager.get_session())
            appointment_repo = AppointmentRepository(self.db_manager.get_session())
            
            scraper = PazireshScraper()
            
            self.scheduler = AppointmentScheduler(
                scraper=scraper,
                telegram_bot=self.telegram_bot,
                cache_manager=self.cache_manager,
                doctor_repo=doctor_repo,
                appointment_repo=appointment_repo,
                user_repo=user_repo,
                metrics=self.metrics or MetricsCollector()
            )
            
            self.running = True
            logger.info("Application startup completed successfully")
            
        except Exception as e:
            logger.error("Failed to start application", error=str(e))
            await self.shutdown()
            raise
    
    async def shutdown(self):
        """خاموش کردن سیستم"""
        logger.info("Shutting down P24_SlotHunter application")
        
        self.running = False
        
        if self.scheduler:
            await self.scheduler.stop()
        
        if self.telegram_bot and self.telegram_bot.app:
            await self.telegram_bot.app.stop()
        
        if self.cache_manager:
            await self.cache_manager.disconnect()
        
        if self.db_manager:
            await self.db_manager.disconnect()
        
        logger.info("Application shutdown completed")
    
    async def run(self):
        """اجرای اصلی برنامه"""
        await self.startup()
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Start telegram bot
            bot_task = asyncio.create_task(self.telegram_bot.app.run_polling())
            
            # Start scheduler
            scheduler_task = asyncio.create_task(self.scheduler.start())
            
            # Wait for tasks
            await asyncio.gather(bot_task, scheduler_task, return_exceptions=True)
            
        except Exception as e:
            logger.error("Application error", error=str(e))
        finally:
            await self.shutdown()

async def main():
    app = Application()
    await app.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error("Application failed", error=str(e))
        sys.exit(1)
```

**تحویلی فاز ۶:**
- Test suite کامل
- Docker containerization
- CI/CD pipeline
- Monitoring dashboard
- Documentation کامل
- Production deployment

---

## 📊 معیارهای موفقیت و KPIs

### Performance Metrics
- **زمان پردازش:** < 3 ثانیه برای 3 دکتر
- **Response Time:** < 5 ثانیه برای اطلاع‌رسانی
- **Uptime:** > 99%
- **False Positive Rate:** < 5%
- **Memory Usage:** < 512MB
- **CPU Usage:** < 50%

### Functional Requirements
- ✅ تشخیص صحیح نوبت‌های خالی
- ✅ اطلاع‌رسانی فوری (< 1 دقیقه)
- ✅ مدیریت چندین کاربر همزمان
- ✅ Restart خودکار در صورت خطا
- ✅ رابط کاربری ساده و کاربرپسند

### Security & Compliance
- ✅ Rate limiting (حداکثر 2 درخواست در ثانیه)
- ✅ رمزگذاری API keys
- ✅ محافظت از اطلاعات کاربران
- ✅ HTTPS برای تمام ارتباطات
- ✅ Backup منظم دیتابیس

---

## 🛠 منابع مورد نیاز

### Infrastructure
- **Server:** VPS با 2GB RAM و 2 CPU cores (بهبود یافته)
- **Storage:** 20GB برای logs، database و cache
- **Network:** اتصال پایدار به اینترنت با حداقل 10Mbps
- **Monitoring:** Prometheus + Grafana stack

### Development Tools
- **IDE:** VS Code / PyCharm
- **Version Control:** Git + GitHub
- **CI/CD:** GitHub Actions
- **Testing:** pytest + coverage
- **Code Quality:** black + flake8 + mypy

---

## 🚨 نکات مهم و بهترین شیوه‌ها

### Critical Success Factors
1. **تست مداوم:** ساختار سایت ممکن است تغییر کند
2. **Graceful Degradation:** سیستم باید در صورت خطا به آرامی متوقف شود
3. **Rate Limiting:** حتماً محدودیت درخواست‌ها را رعایت کنید
4. **User Experience:** رابط ربات تلگرام باید ساده و کاربرپسند باشد
5. **Monitoring:** نظارت مداوم بر عملکرد سیستم ضروری است

### Risk Mitigation
- **Website Changes:** پیاده‌سازی flexible selectors
- **Rate Limiting:** استفاده از exponential backoff
- **Server Downtime:** Circuit breaker pattern
- **Data Loss:** Backup strategy و replication
- **Security:** Regular security audits

### Maintenance Strategy
- **Weekly:** بررسی logs و performance metrics
- **Monthly:** بروزرسانی dependencies
- **Quarterly:** Security audit و penetration testing
- **Yearly:** Architecture review و optimization

---

## 📈 نقشه راه آینده (Post-MVP)

### Phase 7: Advanced Features
- **Smart Scheduling:** ML-based optimal check intervals
- **Multi-City Support:** پشتیبانی از شهرهای مختلف
- **Appointment Booking:** رزرو خودکار نوبت
- **Mobile App:** اپلیکیشن موبایل native

### Phase 8: Scale & Optimization
- **Microservices:** تبدیل به architecture میکروسرویس
- **Load Balancing:** پشتیبانی از traffic بالا
- **Multi-Region:** deployment در چندین منطقه
- **Advanced Analytics:** تحلیل رفتار کاربران

---

## 🎯 خلاصه و نتیجه‌گیری

این نقشه راه جامع برای توسعه P24_SlotHunter طراحی شده تا:

1. **کیفیت بالا:** با استفاده از بهترین practices و patterns
2. **مقیاس‌پذیری:** قابلیت رشد و توسعه در آینده
3. **قابلیت اطمینان:** uptime بالا و error handling مناسب
4. **امنیت:** رعایت اصول امنیتی و حریم خصوصی
5. **نگهداری آسان:** کد تمیز و مستندات کامل

با پیروی از این نقشه راه، پروژه P24_SlotHunter قادر خواهد بود به هدف سرعت ۹ از ۱۰ دست یابد و خدمات باکیفیتی به کاربران ارائه دهد.

---

**تاریخ ایجاد:** {datetime.now().strftime('%Y/%m/%d')}  
**نسخه:** 1.0  
**وضعیت:** Ready for Implementation
