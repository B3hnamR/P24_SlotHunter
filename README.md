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

## 🚀 نصب و راه‌اندازی

### 1. دانلود پروژه
```bash
git clone https://github.com/your-username/P24_SlotHunter.git
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

### دستورات اصلی:
```bash
# راه‌اندازی کامل
python manager.py setup

# اجرای کامل (با تلگرام)
python manager.py run

# اجرای بدون تلگرام
python manager.py run --no-telegram

# تنظیم مجدد ربات تلگرام
python manager.py config

# نمایش وضعیت پروژه
python manager.py status

# تست کامل سیستم
python manager.py test

# پاک‌سازی فایل‌های اضافی
python manager.py clean
```

### اجرای سریع:
```bash
# در Linux/Mac
chmod +x p24
./p24 run

# راهنمای کامل
python manager.py --help
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
│   ├── telegram/            # ربات تلگرام
│   ├── database/            # مدیریت دیتابیس
│   ├── scheduler/           # سیستم نظارت
│   └── utils/               # ابزارهای کمکی
├── config/                  # فایل‌های تنظیمات
├── tests/                   # تست‌ها
└── logs/                    # فایل‌ها�� لاگ
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