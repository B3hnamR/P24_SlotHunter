# 🎯 P24_SlotHunter

**ربات هوشمند نوبت‌گیری پذیرش۲۴** - نظارت خودکار بر نوبت‌های خالی و اطلاع‌رسانی فوری

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)]()

## 📋 ویژگی‌ها

- 🔍 **نظارت مداوم** بر نوبت‌های خالی دکترهای مشخص
- ⚡ **اطلاع‌رسانی فوری** از طریق تلگرام (< 1 دقیقه)
- 🚀 **سرعت بالا** با استفاده مستقیم از API (بدون web scraping)
- 👥 **پشتیبانی چندین دکتر** همزمان
- 🛡️ **پایدار و قابل اعتماد** با مدیریت خطا
- 🐳 **آماده Docker** برای deployment آسان

### 🆕 **ویژگی‌های جدید:**
- ➕ **افزودن دکتر دستی** از طریق لینک در تلگرام
- 🔧 **مدیریت دکترها** (خاموش/روشن کردن نظارت)
- ⏱️ **تنظیم زمان بررسی** از طریق ربات تلگرام
- 🎛️ **پنل مدیریت سرور** با bash script
- 🔒 **کنترل دسترسی** کاربران
- 📊 **آمار و مانیتورینگ** کامل

## 🚀 نصب و راه‌اندازی

### 1. دانلود پروژه
```bash
git clone https://github.com/B3hnamR/P24_SlotHunter.git
cd P24_SlotHunter
```

### 2. راه‌اندازی کامل (یک دستور!)
```bash
python manager.py setup
```

### 3. اجرای پروژه
```bash
python manager.py run
```

## 🎛️ مدیریت پروژه

### 🚀 **مدیریت یکپارچه سرور:**
```bash
# پنل مدیریت کامل (توصیه شده)
./server_manager.sh

# یا استفاده از دستورات مستقیم
./server_manager.sh start    # شروع سرویس
./server_manager.sh stop     # توقف سرویس
./server_manager.sh restart  # راه‌اندازی مجدد
./server_manager.sh status   # وضعیت سرویس
./server_manager.sh logs     # مشاهده لاگ‌ها
./server_manager.sh stats    # آمار سیستم
./server_manager.sh test     # تست سیستم
./server_manager.sh setup    # راه‌اندازی اولیه
```

### ⚡ **دستورات سریع:**
```bash
# دسترسی سریع به عملکردهای مختلف
./p24 start          # شروع سرویس
./p24 stop           # توقف سرویس
./p24 restart        # راه‌اندازی مجدد
./p24 status         # وضعیت سرویس
./p24 logs           # مشاهده لاگ‌ها
./p24 stats          # آمار سیستم
./p24 admin          # پنل مدیریت کامل
./p24 setup          # راه‌اندازی سیستم
./p24 test           # تست سیستم

# استفاده از Python manager برای تنظیمات پیشرفته
./p24 run            # اجرای با Python manager
./p24 config         # تنظیمات با Python manager
```

### 🔧 **پنل مدیریت ادمین:**
```bash
# دسترسی مستقیم به پنل مدیریت
./p24-admin

# شامل تمام قابلیت‌های مدیریتی:
# - کنترل سرویس (Start/Stop/Restart)
# - مانیتورینگ لاگ‌ها
# - آمار سیستم
# - تنظیمات ��یشرفته
# - تست سیستم
# - پشتیبان‌گیری و بازیابی
```

### 📋 **Python Manager (پیشرفته):**
```bash
# برای تنظیمات پیشرفته و توسعه
python manager.py setup      # راه‌اندازی کامل
python manager.py run        # اجرای کامل
python manager.py config     # تنظیم ربات تلگرام
python manager.py status     # وضعیت پروژه
python manager.py test       # تست کامل
python manager.py clean      # پاک‌سازی
```

## ⚙️ تنظیمات

### فایل `config/config.yaml`:
```yaml
telegram:
  bot_token: "${TELEGRAM_BOT_TOKEN}"
  admin_chat_id: "${ADMIN_CHAT_ID}"

monitoring:
  check_interval: 30        # فاصله بررسی (ثانیه)
  days_ahead: 7            # روزهای آینده

doctors:
  - name: "دکتر نمونه"
    slug: "doctor-slug"
    center_id: "center-id"
    service_id: "service-id"
    # ... سایر فیلدها
```

## 🤖 ربات تلگرام

### دستورات کاربر:
```
/start - شروع ربات
/doctors - مشاهده دکترها
/subscribe - اشتراک در دکتر
/status - وضعیت اشتراک‌ها
/help - راهنما
```

### دستورات ادمین:
```
/admin - پنل مدیریت کامل
  ➕ افزودن دکتر
  🔧 مدیریت دکترها
  ⏱️ تنظیم زمان بررسی
  👥 مدیریت کاربران
  📊 آمار سیستم
```

## 🧪 تست API

برای تست عملکرد API:
```bash
python test_api.py
```

## 📁 ساختار پروژه

```
P24_SlotHunter/
├── src/
│   ├── api/                 # کلاینت API پذیرش۲۴
│   ├── telegram_bot/        # ربات تلگرام پیشرفته
│   ├── database/            # مدیریت دیتابیس
│   ├── scheduler/           # سیستم نظارت
│   └── utils/               # ابزارهای کمکی
├── config/                  # فایل‌های تنظیمات
├── docs/                    # مستندات کامل
│   └── roadmap/            # نقشه‌های راه
├── tests/                   # تست‌ها
└── logs/                    # فایل‌های لاگ
```

## 🔧 API های استفاده شده

پروژه از API های رسمی پذیرش۲۴ استفاده می‌کند:

- `POST /booking/v2/getFreeDays` - دریافت روزهای موجود
- `POST /booking/v2/getFreeTurns` - دریافت نوبت‌های روز
- `POST /booking/v2/suspend` - رزرو موقت نوبت
- `POST /booking/v2/unsuspend` - لغو رزرو

## 📊 عملکرد

- ⚡ **سرعت**: < 3 ثانیه برای بررسی 3 دکتر
- 🎯 **دقت**: > 95% تشخیص صحیح نوبت‌ها
- 🔄 **Uptime**: > 99% با restart خودکار
- 📱 **اطلاع‌رسانی**: < 1 دقیقه از زمان موجود شدن

## 🐳 Docker

```bash
# Build
docker build -t p24-slothunter .

# Run
docker run -d --name slothunter \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e ADMIN_CHAT_ID=your_chat_id \
  p24-slothunter
```

## 📚 مستندات

### 🗺️ **Roadmap و نق��ه راه**
- [`docs/roadmap/`](docs/roadmap/) - نقشه‌های راه توسعه
  - [`SUMMARY.md`](docs/roadmap/SUMMARY.md) - خلاصه نقشه راه 18 ماهه
  - [`COMMERCIAL.md`](docs/roadmap/COMMERCIAL.md) - استراتژی تجاری کامل
  - [`TECHNICAL.md`](docs/roadmap/TECHNICAL.md) - معماری فنی مفصل
  - [`FEATURES.md`](docs/roadmap/FEATURES.md) - ویژگی‌های جدید

### 📖 **راهنماها**
- [`docs/`](docs/) - مستندات کامل پروژه
- [راهنمای نصب](INSTALLATION.md)
- [راهنمای کاربر](USER_GUIDE.md)
- [مستندات API](API_DOCS.md)

## 🤝 مشارکت

1. Fork کنید
2. Branch جدید بسازید (`git checkout -b feature/amazing-feature`)
3. تغییرات را commit کنید (`git commit -m 'Add amazing feature'`)
4. Push کنید (`git push origin feature/amazing-feature`)
5. Pull Request ایجاد کنید

## 📄 لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. فایل [LICENSE](LICENSE) را مطالعه کنید.

## ⚠️ اخلاق استفاده

- از این ابزار به صورت مسئولانه استفاده کنید
- سرور پذیرش۲۴ را overload نکنید
- حداقل 15 ثانیه فاصله بین درخواست‌ها رعایت کنید

## 📞 پشتیبانی

- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/P24_SlotHunter/issues)
- 📧 **Email**: your-email@example.com
- 💬 **Telegram**: @your_username

---

**ساخته شده با ❤️ برای بهبود دسترسی به خدمات پزشکی**
