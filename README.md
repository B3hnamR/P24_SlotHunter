# 🎯 P24_SlotHunter

**ربات هوشمند نوبت‌یابی پذیرش۲۴** - رصد خودکار نوبت‌های خالی و اطلاع‌رسانی فوری

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![API](https://img.shields.io/badge/API-Only-green.svg)]()

## 🔥 ویژگی‌ها

- 🤖 **ربات تلگرام** با رابط کاربری ساده
- 🔍 **رصد خودکار** نوبت‌های خالی ۲۴/۷
- ⚡ **اطلاع‌رسانی فوری** در کمتر از 30 ثانیه
- 🚀 **API-Only** - بدون Web Scraping
- 👥 **چندین دکتر** همزمان
- 📊 **مدیریت کاربران** و اشتراک‌ها

## 🚀 نصب سریع

### 1. دانلود
```bash
git clone https://github.com/B3hnamR/P24_SlotHunter.git
cd P24_SlotHunter
```

### 2. راه‌اندازی خودکار
```bash
chmod +x server_manager.sh
./server_manager.sh setup
```

### 3. تنظیمات
```bash
./server_manager.sh config
```

### 4. شروع
```bash
./server_manager.sh start
```

## ⚙️ تنظیمات

### 1. ربات تلگرام
- به [@BotFather](https://t.me/BotFather) پیام دهید
- `/newbot` بزنید و توکن را کپی کنید
- Chat ID خود را از [@userinfobot](https://t.me/userinfobot) بگیرید

### 2. اضافه کردن دکتر
فایل `config/config.yaml` را ویرایش کنید:

```yaml
doctors:
  - name: "دکتر نمونه"
    slug: "doctor-slug"
    center_id: "12345"
    service_id: "67890"
    user_center_id: "11111"
    terminal_id: "22222"
    specialty: "قلب و عروق"
    is_active: true
```

## 🎛️ مدیریت

### دستورات اصلی:
```bash
./server_manager.sh start     # شروع
./server_manager.sh stop      # توقف
./server_manager.sh restart   # ری‌استارت
./server_manager.sh status    # وضعیت
./server_manager.sh logs      # مشاهده لاگ‌ها
./server_manager.sh health    # بررسی سلامت
```

### منوی تعاملی:
```bash
./server_manager.sh
```

## 🤖 ربات تلگرام

### دستورات کاربر:
- `/start` - شروع ربات
- `/doctors` - مشاهده دکترها
- `/help` - راهنما

### قابلیت‌ها:
- 👨‍⚕️ **مشاهده دکترها** - لیست دکترهای موجود
- 📝 **اشتراک/لغو اشتراک** - مدیریت اشتراک‌ها
- 🔔 **اطلاع‌رسانی** - دریافت پیام نوبت‌های خالی

## 📁 ساختار پروژه

```
P24_SlotHunter/
├── src/
│   ├── api/                 # API پذیرش۲۴
│   ├── telegram_bot/        # ربات تلگرام
│   ├── database/            # دیتابیس
│   ├── utils/               # ابزارها
│   └── main.py              # فایل اصلی
├── config/
│   └── config.yaml          # تنظیمات
├── data/                    # دیتابیس
├── logs/                    # لاگ‌ها
├── .env                     # متغیرهای محیطی
├── requirements.txt         # وابستگی‌ها
└── server_manager.sh        # مدیریت سرور
```

## 🔧 نیازمندی‌ها

- **Python 3.9+**
- **SQLite** (خودکار)
- **Internet** برای API

### وابستگی‌های Python:
- `python-telegram-bot` - ربات تلگرام
- `httpx` - HTTP client
- `sqlalchemy` - ORM دیتابیس
- `pyyaml` - خواندن config
- `python-dotenv` - متغیرهای محیطی

## 📊 عملکرد

- ⚡ **سرعت بررسی:** < 5 ثانیه برای هر ��کتر
- 🔄 **فاصله بررسی:** 30 ثانیه (قابل تنظیم)
- 📱 **اطلاع‌رسانی:** فوری پس از پیدا شدن نوبت
- 🛡️ **پایداری:** restart خودکار در صورت خطا

## 🐳 Docker (اختیاری)

```bash
# Build
docker build -t p24-slothunter .

# Run
docker run -d --name slothunter \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  p24-slothunter
```

## 🔒 امنیت

- 🔐 **متغیرهای محیطی** برای اطلاعات حساس
- 🛡️ **محدودیت دسترسی** ادمین
- 📝 **لاگ امن** بدون اطلاعات شخصی
- 🚫 **عدم ذخیره** اطلاعات پزشکی

## ⚠️ نکات مهم

- **مسئولانه استفاده کنید** - سرور پذیرش۲۴ را overload نکنید
- **حداقل 30 ثانیه فاصله** بین بررسی‌ها
- **فقط برای استفاده شخصی** - تجاری نکنید
- **قوانین پذیرش۲۴** را رعایت کنید

## 🐛 مشکلات رایج

### ربات پاسخ نمی‌دهد:
```bash
./server_manager.sh status
./server_manager.sh logs
```

### خطای API:
- اتصال اینترنت را بررسی کنید
- اطلاعات دکتر در config را چک کنید

### خطای دیتابیس:
```bash
rm data/slothunter.db
./server_manager.sh restart
```

## 📚 مستندات کامل

برای اطلاعات تفصیلی:
- [`PROJECT_STRUCTURE_SUMMARY.md`](PROJECT_STRUCTURE_SUMMARY.md) - ساختار کامل پروژه
- [`SETUP_GUIDE.md`](SETUP_GUIDE.md) - راهنمای نصب تفصیلی

## 🤝 مشارکت

1. Fork کنید
2. Branch جدید بسازید
3. تغییرات را commit کنید
4. Pull Request ایجاد کنید

## 📄 لایسنس

MIT License - فایل [LICENSE](LICENSE) را مطالعه کنید.

## 📞 پشتیبانی

- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/P24_SlotHunter/issues)
- 📧 **Email**: your-email@example.com

---

**ساخته شده با ❤️ برای بهبود دسترسی به خدمات پزشکی**