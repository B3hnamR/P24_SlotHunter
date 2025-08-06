# 🔌 P24_SlotHunter - مرجع کامل API

**مستندات کامل API پذیرش۲۴ و نحوه استفاده در پروژه**

---

## 📖 فهرست مطالب

1. [معرفی API](#-معرفی-api)
2. [Base URL و Endpoints](#-base-url-و-endpoints)
3. [Headers و Authentication](#-headers-و-authentication)
4. [کلاس EnhancedPazireshAPI](#-کلاس-enhancedpazireshapi)
5. [Endpoints تفصیلی](#-endpoints-تفصیلی)
6. [مدل‌های داده](#-مدل‌های-داده)
7. [Rate Limiting](#-rate-limiting)
8. [مثال‌های کاربردی](#-مثال‌های-کاربردی)
9. [عیب‌یابی](#-عیب‌یابی)

---

## 🎯 معرفی API

API پذیرش۲۴ یک REST API است که امکان دسترسی به اطلاعات نوبت‌های پزشکی را فراهم می‌کند.

### ویژگی‌های کلیدی:
- 🔍 **جستجوی نوبت‌های خالی** در روزهای مختلف
- 📅 **دریافت تقویم** روزهای کاری دکتر
- 🔒 **رزرو موقت** نوبت‌ها
- ❌ **لغو رزرو** نوبت‌های رزرو شده
- 🏥 **پشتیبانی چندمرکزی** برای دکترهای مختلف

---

## 🌐 Base URL و Endpoints

### Base URL:
```
https://apigw.paziresh24.com/booking/v2
```

### Endpoints اصلی:

| Endpoint | Method | توضیح |
|----------|--------|-------|
| `/getFreeDays` | POST | دریافت روزهای موجود |
| `/getFreeTurns` | POST | دریافت نوبت‌های روز خاص |
| `/suspend` | POST | رزرو موقت نوبت |
| `/unsuspend` | POST | لغو رزرو نوبت |

---

## 🔐 Headers و Authentication

### Headers ضروری:
```python
headers = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.paziresh24.com',
    'referer': 'https://www.paziresh24.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'accept-language': 'fa-IR,fa;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'center_id': '12345',           # شناسه مرکز
    'terminal_id': 'clinic-xxx'     # ش��اسه ترمینال
}
```

### نکات مهم:
- **User-Agent:** باید شبیه مرورگر واقعی باشد
- **center_id:** در header و body ارسال می‌شود
- **terminal_id:** شناسه منحصر به فرد برای هر session

---

## 🏗️ کلاس EnhancedPazireshAPI

### تعریف کلاس:
```python
class EnhancedPazireshAPI:
    def __init__(self, 
                 doctor: Doctor,                    # شیء دکتر
                 client: httpx.AsyncClient = None,  # HTTP client
                 timeout: int = 15,                 # timeout (ثانیه)
                 base_url: str = None,              # URL پایه
                 request_delay: float = 1.5):       # تاخیر بین درخواست‌ها
```

### متدهای اصلی:

#### 1. `get_all_available_appointments(days_ahead: int = 5)`
دریافت تمام نوبت‌های موجود برای دکتر

**پارامترها:**
- `days_ahead`: تعداد روزهای آینده (پیش‌فرض: 5)

**خروجی:**
```python
List[Appointment]  # لیست نوبت‌های موجود
```

**مثال:**
```python
api = EnhancedPazireshAPI(doctor)
appointments = await api.get_all_available_appointments(days_ahead=7)

for apt in appointments:
    print(f"نوبت: {apt.time_str} - مرکز: {apt.center_name}")
```

#### 2. `reserve_appointment(center, service, appointment)`
رزرو موقت نوبت

**پارامترها:**
- `center`: شیء مرکز درمانی
- `service`: شیء سرویس
- `appointment`: شیء نوبت

**خروجی:**
```python
APIResponse  # شامل وضعیت رزرو و کد درخواست
```

#### 3. `cancel_reservation(center, request_code)`
لغو رزرو نوبت

**پارامترها:**
- `center`: شیء مرکز درمانی
- `request_code`: کد درخواست رزرو

#### 4. `generate_terminal_id()`
تولید شناسه ترمینال منحصر به فرد

**خروجی:**
```python
str  # مثال: "clinic-1703462400123.87654321"
```

---

## 📡 Endpoints تفصیلی

### 1. دریافت روزهای موجود (`/getFreeDays`)

#### درخواست:
```http
POST https://apigw.paziresh24.com/booking/v2/getFreeDays
Content-Type: application/x-www-form-urlencoded

center_id=12345&service_id=67890&user_center_id=11111&return_free_turns=false&return_type=calendar&terminal_id=clinic-xxx
```

#### پارامترهای ضروری:
```python
{
    'center_id': '12345',           # شناسه مرکز درمانی
    'service_id': '67890',          # شناسه سرویس
    'user_center_id': '11111',      # شناسه کاربری مرکز
    'return_free_turns': 'false',   # عدم بازگشت نوبت‌ها
    'return_type': 'calendar',      # نوع بازگشت: calendar
    'terminal_id': 'clinic-xxx'     # شناسه ترمینال
}
```

#### پاسخ موفق:
```json
{
    "status": 1,
    "message": "success",
    "calendar": {
        "turns": [1703462400, 1703548800, 1703635200],
        "holidays": ["1703721600"],
        "working_days": ["saturday", "sunday", "monday", "tuesday", "wednesday"]
    }
}
```

#### پاسخ خطا:
```json
{
    "status": 0,
    "message": "No available days",
    "error": "Center not found"
}
```

### 2. دریافت نوبت‌های روز (`/getFreeTurns`)

#### درخواست:
```http
POST https://apigw.paziresh24.com/booking/v2/getFreeTurns
Content-Type: application/x-www-form-urlencoded

center_id=12345&service_id=67890&user_center_id=11111&date=1703462400&terminal_id=clinic-xxx
```

#### پارامترهای ضروری:
```python
{
    'center_id': '12345',           # شناسه مرکز درمانی
    'service_id': '67890',          # شناسه سرویس
    'user_center_id': '11111',      # شناسه کاربری مرکز
    'date': '1703462400',           # تاریخ (Unix timestamp)
    'terminal_id': 'clinic-xxx'     # شناسه ترمینال
}
```

#### پاس�� موفق:
```json
{
    "status": 1,
    "message": "success",
    "result": [
        {
            "from": 1703462400,
            "to": 1703463000,
            "workhour_turn_num": 1
        },
        {
            "from": 1703463600,
            "to": 1703464200,
            "workhour_turn_num": 2
        },
        {
            "from": 1703465200,
            "to": 1703465800,
            "workhour_turn_num": 3
        }
    ]
}
```

### 3. رزرو موقت نوبت (`/suspend`)

#### درخواست:
```http
POST https://apigw.paziresh24.com/booking/v2/suspend
Content-Type: application/x-www-form-urlencoded

center_id=12345&service_id=67890&user_center_id=11111&from=1703462400&to=1703463000&terminal_id=clinic-xxx
```

#### پارامترهای ضروری:
```python
{
    'center_id': '12345',           # شناسه مرکز درمانی
    'service_id': '67890',          # شناسه سرویس
    'user_center_id': '11111',      # شناسه کاربری مرکز
    'from': '1703462400',           # زمان شروع نوبت
    'to': '1703463000',             # زمان پایان نوبت
    'terminal_id': 'clinic-xxx'     # شناسه ترمینال
}
```

#### پاسخ موفق:
```json
{
    "status": 1,
    "message": "Appointment suspended successfully",
    "request_code": "REQ123456789",
    "suspend_time": 300
}
```

### 4. ��غو رزرو نوبت (`/unsuspend`)

#### درخواست:
```http
POST https://apigw.paziresh24.com/booking/v2/unsuspend
Content-Type: application/x-www-form-urlencoded

center_id=12345&request_code=REQ123456789&terminal_id=clinic-xxx
```

#### پارامترهای ضروری:
```python
{
    'center_id': '12345',           # شناسه مرکز درمانی
    'request_code': 'REQ123456789', # کد درخواست رزرو
    'terminal_id': 'clinic-xxx'     # شناسه ترمینال
}
```

---

## 📊 مدل‌های داده

### کلاس Appointment:
```python
@dataclass
class Appointment:
    from_time: int          # زمان شروع (Unix timestamp)
    to_time: int            # زمان پایان (Unix timestamp)
    workhour_turn_num: int  # شماره نوبت
    doctor_slug: str = ""   # شناسه دکتر
    center_name: str = ""   # نام مرکز
    service_name: str = ""  # نام سرویس
    center_id: str = ""     # شناسه مرکز
    service_id: str = ""    # شناسه سرویس
    
    @property
    def start_datetime(self) -> datetime:
        """تبدیل timestamp به datetime"""
        return datetime.fromtimestamp(self.from_time)
    
    @property
    def end_datetime(self) -> datetime:
        """تبدیل timestamp پایان به datetime"""
        return datetime.fromtimestamp(self.to_time)
    
    @property
    def time_str(self) -> str:
        """نمایش زمان به صورت رشته فارسی"""
        return self.start_datetime.strftime('%Y/%m/%d %H:%M')
    
    @property
    def duration_minutes(self) -> int:
        """مدت زمان نوبت به دقیقه"""
        return (self.to_time - self.from_time) // 60
    
    @property
    def is_today(self) -> bool:
        """بررسی اینکه نوبت امروز است یا نه"""
        today = datetime.now().date()
        return self.start_datetime.date() == today
```

### کلاس APIResponse:
```python
@dataclass
class APIResponse:
    status: int                    # کد وضعیت (1 = موفق، 0 = خطا)
    message: str                   # پیام پاسخ
    data: Optional[dict] = None    # داده‌های اضافی
    error: Optional[str] = None    # پیام خطا
    
    @property
    def is_success(self) -> bool:
        """بررسی موفقیت درخواست"""
        return self.status == 1
    
    @property
    def is_rate_limited(self) -> bool:
        """بررسی Rate Limiting"""
        return "rate" in self.message.lower() or "limit" in self.message.lower()
    
    def get_appointments(self) -> List[Appointment]:
        """استخراج نوبت‌ها از پاسخ"""
        if not self.is_success or not self.data:
            return []
        
        appointments = []
        for apt_data in self.data.get('result', []):
            appointment = Appointment(
                from_time=apt_data['from'],
                to_time=apt_data['to'],
                workhour_turn_num=apt_data['workhour_turn_num']
            )
            appointments.append(appointment)
        
        return appointments
```

### کلاس Doctor (Database Model):
```python
class Doctor(Base):
    __tablename__ = 'doctors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    doctor_id = Column(String(100))
    specialty = Column(String(200))
    is_active = Column(Boolean, default=True)
    
    # روابط
    centers = relationship("DoctorCenter", back_populates="doctor")
    subscriptions = relationship("Subscription", back_populates="doctor")
```

---

## ⚡ Rate Limiting

### محدودیت‌های شناخته شده:
```python
# بر اساس تست‌های انجام شده:
MAX_REQUESTS_PER_MINUTE = 20      # حداکثر 20 درخواست در دقیقه
MAX_REQUESTS_PER_HOUR = 300       # ح��اکثر 300 درخواست در ساعت
MAX_CONCURRENT_REQUESTS = 3       # حداکثر 3 درخواست همزمان

# کدهای خطای Rate Limiting:
HTTP_429_TOO_MANY_REQUESTS = 429
API_STATUS_RATE_LIMITED = 0
```

### تنظیمات بهینه:
```python
# تنظیمات پیشنهادی برای جلوگیری از Rate Limiting:
CHECK_INTERVAL = 90               # بررسی هر 90 ثانیه
DAYS_AHEAD = 5                    # بررسی 5 روز آینده
REQUEST_DELAY = 1.5               # 1.5 ثانیه تاخیر بین درخواست‌ها
RETRY_DELAY = 5                   # 5 ثانیه انتظار بعد از Rate Limit

# محاسبه تعداد درخواست‌ها:
# هر دکتر: 1 getFreeDays + 5 getFreeTurns = 6 درخواست
# هر 90 ثانیه: 6 درخواست
# در ساعت: (3600/90) * 6 = 240 درخواست (کمتر از حد مجاز)
```

### مدیریت Rate Limiting:
```python
async def handle_rate_limit(self, retry_count: int = 0):
    """مدیریت Rate Limiting"""
    if retry_count >= 3:
        raise Exception("Maximum retry attempts reached")
    
    # انتظار تصاعدی
    delay = 5 * (2 ** retry_count)  # 5, 10, 20 ثانیه
    
    self.logger.warning(f"⚠️ Rate limit hit, waiting {delay} seconds...")
    await asyncio.sleep(delay)
    
    return retry_count + 1
```

---

## 💡 مثال‌های کاربردی

### 1. بررسی نوبت‌های یک دکتر:
```python
import asyncio
from src.api.enhanced_paziresh_client import EnhancedPazireshAPI
from src.database.models import Doctor

async def check_doctor_appointments():
    # ایجاد شیء دکتر (معمولاً از دیتابیس)
    doctor = Doctor(
        name="دکتر احمد محمدی",
        slug="doctor-ahmad-mohammadi-0"
    )
    
    # ایجاد API client
    api = EnhancedPazireshAPI(doctor, request_delay=2.0)
    
    # دریافت نوبت‌ها
    appointments = await api.get_all_available_appointments(days_ahead=3)
    
    # نمایش نتایج
    if appointments:
        print(f"🎯 {len(appointments)} نوبت موجود:")
        for apt in appointments:
            print(f"  📅 {apt.time_str} - {apt.center_name}")
    else:
        print("📭 هیچ نوبتی موجود نیست")

# اجرا
asyncio.run(check_doctor_appointments())
```

### 2. رزرو موقت نوبت:
```python
async def reserve_appointment_example():
    api = EnhancedPazireshAPI(doctor)
    
    # دریافت نوبت‌ها
    appointments = await api.get_all_available_appointments()
    
    if appointments:
        # انتخاب اولین نوبت
        first_appointment = appointments[0]
        
        # رزرو موقت
        response = await api.reserve_appointment(
            center=doctor.centers[0],
            service=doctor.centers[0].services[0],
            appointment=first_appointment
        )
        
        if response.is_success:
            request_code = response.data.get('request_code')
            print(f"✅ نوبت رزرو شد. کد: {request_code}")
            
            # لغو رزرو بعد از 30 ثانیه
            await asyncio.sleep(30)
            
            cancel_response = await api.cancel_reservation(
                center=doctor.centers[0],
                request_code=request_code
            )
            
            if cancel_response.is_success:
                print("✅ رزرو لغو شد")
        else:
            print(f"❌ خطا در رزرو: {response.message}")
```

### 3. مانیتورینگ مداوم:
```python
async def continuous_monitoring():
    api = EnhancedPazireshAPI(doctor, request_delay=1.5)
    
    while True:
        try:
            appointments = await api.get_all_available_appointments()
            
            if appointments:
                print(f"🎯 {len(appointments)} نوبت پیدا شد!")
                # ارسال اطلاع‌رسانی
                await send_notification(appointments)
            else:
                print("📭 نوبتی موجود نیست")
            
            # انتظار 90 ثانیه
            await asyncio.sleep(90)
            
        except Exception as e:
            print(f"❌ خطا: {e}")
            await asyncio.sleep(60)  # انتظار بیشتر در صورت خطا
```

### 4. استخراج اطلاعات دکتر از URL:
```python
from src.api.doctor_extractor import DoctorInfoExtractor

async def extract_doctor_info():
    extractor = DoctorInfoExtractor()
    
    url = "https://www.paziresh24.com/dr/دکتر-احمد-محمدی-0/"
    
    doctor_info = await extractor.extract_doctor_info(url)
    
    if doctor_info:
        print("✅ اطلاعات استخراج شد:")
        print(f"  نام: {doctor_info.get('name')}")
        print(f"  تخصص: {doctor_info.get('specialty')}")
        print(f"  center_id: {doctor_info.get('center_id')}")
        print(f"  service_id: {doctor_info.get('service_id')}")
    else:
        print("❌ استخراج اطلاعات ناموفق")
```

---

## 🔧 عیب‌یابی

### مشکلات رایج و راه‌حل‌ها:

#### 1. خطای 429 (Rate Limiting):
```python
# علائم:
"⚠️ Rate limit hit, waiting 5 seconds..."
HTTP 429 Too Many Requests

# راه‌حل:
# افزایش تاخیر بین درخواست‌ها
REQUEST_DELAY = 2.0

# کا��ش فرکانس بررسی
CHECK_INTERVAL = 120

# کاهش روزهای بررسی
DAYS_AHEAD = 3
```

#### 2. خطای اتصال:
```python
# علائم:
httpx.ConnectError: Connection failed
httpx.TimeoutException: Request timed out

# راه‌حل:
# افزایش timeout
api = EnhancedPazireshAPI(doctor, timeout=30)

# استفاده از retry mechanism
for attempt in range(3):
    try:
        response = await api.get_appointments()
        break
    except httpx.RequestError:
        if attempt == 2:
            raise
        await asyncio.sleep(5)
```

#### 3. پاسخ خالی یا نادرست:
```python
# علائم:
{"status": 0, "message": "No data found"}
[]  # لیست خالی

# راه‌حل:
# بررسی صحت پارامترها
if not center_id or not service_id:
    raise ValueError("Missing required parameters")

# بررسی وضعیت دکتر
if not doctor.is_active:
    logger.warning("Doctor is not active")
    return []
```

#### 4. خطای JSON Parsing:
```python
# علائم:
json.JSONDecodeError: Expecting value

# راه‌حل:
try:
    result = response.json()
except json.JSONDecodeError:
    logger.error(f"Invalid JSON response: {response.text}")
    return APIResponse(status=0, message="Invalid response format")
```

### ابزارهای عیب‌یابی:

#### 1. لاگ تفصیلی:
```python
import logging

# فعال‌سازی لاگ DEBUG
logging.getLogger("EnhancedPazireshAPI").setLevel(logging.DEBUG)

# لاگ درخواست‌ها
logger.debug(f"Sending request to {url} with data: {data}")
logger.debug(f"Response: {response.text}")
```

#### 2. تست دستی API:
```bash
# تست با curl
curl -X POST "https://apigw.paziresh24.com/booking/v2/getFreeDays" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "User-Agent: Mozilla/5.0..." \
  -d "center_id=12345&service_id=67890&user_center_id=11111&return_free_turns=false&return_type=calendar&terminal_id=clinic-test"
```

#### 3. مانیتورینگ شبکه:
```python
import time

class APIMonitor:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.last_request_time = 0
    
    async def log_request(self, url: str, success: bool):
        self.request_count += 1
        if not success:
            self.error_count += 1
        
        current_time = time.time()
        if current_time - self.last_request_time < 1:
            logger.warning("Requests too frequent!")
        
        self.last_request_time = current_time
        
        # آمار
        error_rate = (self.error_count / self.request_count) * 100
        logger.info(f"📊 Requests: {self.request_count}, Errors: {error_rate:.1f}%")
```

---

## 📈 بهینه‌سازی عملکرد

### 1. Connection Pooling:
```python
import httpx

# استفاده از connection pool
async with httpx.AsyncClient(
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
    timeout=15
) as client:
    api = EnhancedPazireshAPI(doctor, client=client)
    appointments = await api.get_all_available_appointments()
```

### 2. Caching:
```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedAPI:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 دقیقه
    
    async def get_cached_appointments(self, doctor_id: str):
        cache_key = f"appointments_{doctor_id}"
        
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        
        # دریافت داده جدید
        appointments = await self.api.get_all_available_appointments()
        self.cache[cache_key] = (appointments, time.time())
        
        return appointments
```

### 3. Batch Processing:
```python
async def process_multiple_doctors(doctors: List[Doctor]):
    """پردازش همزمان چندین دکتر"""
    semaphore = asyncio.Semaphore(3)  # حداکثر 3 همزمان
    
    async def process_doctor(doctor):
        async with semaphore:
            api = EnhancedPazireshAPI(doctor)
            return await api.get_all_available_appointments()
    
    # اجرای همزمان
    tasks = [process_doctor(doctor) for doctor in doctors]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

---

## 🔒 امنیت و بهترین شیوه‌ها

### 1. مخفی کردن اطلاعات حساس:
```python
# ❌ اشتباه
logger.info(f"Request data: {data}")  # ممکن است اطلاعات حساس لو برود

# ✅ درست
safe_data = {k: v for k, v in data.items() if k not in ['terminal_id', 'center_id']}
logger.info(f"Request data: {safe_data}")
```

### 2. اعتبارسنجی ورودی:
```python
def validate_doctor_data(doctor_data: dict) -> bool:
    """اعتبارسنجی داده‌های دکتر"""
    required_fields = ['center_id', 'service_id', 'user_center_id']
    
    for field in required_fields:
        if not doctor_data.get(field):
            raise ValueError(f"Missing required field: {field}")
        
        # بررسی فرمت
        if not doctor_data[field].isdigit():
            raise ValueError(f"Invalid format for {field}")
    
    return True
```

### 3. محدودیت نرخ درخواست:
```python
class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        now = time.time()
        
        # حذف درخواست‌های قدیمی
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            await asyncio.sleep(sleep_time)
        
        self.requests.append(now)
```

---

## 📚 منابع و مراجع

### مستندات مرتبط:
- [COMPLETE_DOCUMENTATION.md](COMPLETE_DOCUMENTATION.md) - مستندات کامل پروژه
- [README.md](../README.md) - راهنمای اصلی
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - راهنمای راه‌اندازی

### کتابخانه‌های استفاده شده:
- [httpx](https://www.python-httpx.org/) - HTTP client async
- [asyncio](https://docs.python.org/3/library/asyncio.html) - برنامه‌نویسی async
- [dataclasses](https://docs.python.org/3/library/dataclasses.html) - مدل‌های داده

### ابزارهای توسعه:
- [Postman](https://www.postman.com/) - تست API
- [curl](https://curl.se/) - تست خط فرمان
- [Wireshark](https://www.wireshark.org/) - تحلیل ترافیک شبکه

---

**آخرین به‌روزرسانی:** دسامبر 2024  
**نسخه API:** v2  
**سازگاری:** Python 3.9+