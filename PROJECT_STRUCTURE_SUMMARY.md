# P24_SlotHunter – Technical Project Structure Overview

این سند خلاصه‌ای حرفه‌ای و ساختاریافته از پروژه P24_SlotHunter را برای مطالعه و بررسی یک برنامه‌نویس متخصص ارائه می‌دهد. هدف، آشنایی سریع با معماری، نقش هر فایل/پوشه و نقاط کلیدی توسعه است.

---

## 1. ساختار کلی پروژه

```
P24_SlotHunter/
├── src/                  # کد اصلی برنامه (ماژولار)
│   ├── api/              # کلاینت API پذیرش۲۴ و مدل‌های داده
│   ├── database/         # ORM و مدیریت دیتابیس
│   ├── telegram_bot/     # منطق ربات تلگرام (handlers, menu, admin, ...)
│   ├── utils/            # ابزارهای کمکی (تنظیمات، لاگ)
│   └── main.py           # نقطه ورود اصلی برنامه
├── config/               # فایل‌های تنظیمات (YAML)
├── data/                 # دیتابیس و داده‌های ذخیره‌شده
├── logs/                 # لاگ‌های برنامه
├── tests/                # تست‌های واحد و یکپارچه
├── alembic/              # مدیریت migration دیتابیس
├── docs/                 # مستندات و نقشه راه توسعه
├── server_manager.sh     # مدیریت سرویس (لینوکس/یونیکس)
├── requirements.txt      # وابستگی‌های پایتون
├── .env / .env.example   # متغیرهای محیطی
└── slothunter.service    # فایل systemd برای اجرا به عنوان سرویس
```

---

## 2. شرح پوشه‌ها و فایل‌های کلیدی

### src/
- **main.py**: نقطه ورود async برنامه؛ راه‌اندازی کانفیگ، دیتابیس، ربات تلگرام و حلقه مانیتورینگ نوبت‌ها.
- **api/**
  - `paziresh_client.py`: کلاینت async برای API پذیرش۲۴ (دریافت نوبت، رزرو، لغو).
  - `models.py`: مدل‌های داده‌ای Doctor, Appointment, APIResponse (dataclass).
- **database/**
  - `models.py`: ORM SQLAlchemy برای User, Doctor, Subscription, AppointmentLog.
  - `database.py`: مدیریت AsyncSession، context manager و راه‌اندازی دیتابیس.
- **telegram_bot/**
  - `bot.py`: کلاس اصلی ربات تلگرام (python-telegram-bot v20+)، مدیریت lifecycle و ارسال پیام.
  - `handlers.py`: دستورات اصلی کاربر (start, help, subscribe, ...).
  - `menu_handlers.py`: منوهای تعاملی و نقش‌محور (Reply/Inline keyboards).
  - `callback_handlers.py`: مدیریت کامل callbackهای دکمه‌های inline (اشتراک، آمار، مدیریت).
  - `admin_handlers.py`: عملیات مدیریتی (افزودن دکتر، تنظیمات ادمین).
  - `admin_menu_handlers_fixed.py`: منوهای پیشرفته ادمین با کنترل دسترسی نقش‌محور.
  - `messages.py`: قالب‌بندی پیام‌ها و متون ربات.
  - `user_roles.py`: سیستم نقش‌های کاربری (User, Moderator, Admin, Super Admin).
  - `access_control.py`: کنترل دسترسی و مجوزها.
  - `decorators.py`: دکوراتورهای کمکی برای کنترل دسترسی.
  - `utils.py`: ابزارهای کمکی ربات تلگرام.
- **utils/**
  - `config.py`: مدیریت تنظیمات پروژه (YAML + env + pydantic).
  - `logger.py`: سیستم لاگ (console/file, rotating) و اطلاع‌رسانی خطا به ادمین تلگرام.

### config/
- **config.yaml**: تنظیمات اصلی پروژه (توکن ربات، چت ادمین، پارامترهای مانیتورینگ، لاگ، لیست دکترها).

### data/
- **slothunter.db**: دیتابیس SQLite پروژه (در صورت استفاده از SQLite).

### logs/
- **slothunter.log**: لاگ اصلی برنامه (قابل چرخش و مدیریت).

### alembic/
- **env.py**: تنظیمات migration دیتابیس (خواندن مدل‌ها و آدرس دیتابیس از config/env).
- **README.md**: راهنمای migration با Alembic.

### tests/
- **test_config.py**: تست بارگذاری تنظیمات و مقادیر پیش‌فرض.
- **test_doctor_model.py**: تست اعتبارسنجی مدل Doctor.
- **test_paziresh_api.py**: تست اولیه کلاینت API پذیرش۲۴ (async).

### اسکریپت‌های مدیریتی
- **server_manager.sh**: مدیریت سرویس و setup پیشرفته برای لینوکس (bash, systemd, health check، پنل تعاملی).
- **slothunter.service**: فایل systemd برای اجرای پروژه به عنوان سرویس دائمی.

### سایر فایل‌ها
- **requirements.txt**: لیست کامل وابستگی‌های پایتون (async, telegram, db, test, dev).
- **.env / .env.example**: متغیرهای محیطی (توکن ربات، چت ادمین، تنظیمات اختیاری).
- **CHANGES_SUMMARY.md**: خلاصه تغییرات و بهبودهای اخیر پروژه.

---

## 3. نکات معماری و توسعه
- **معماری ماژولار و async**: جداسازی کامل لایه‌ها (API, DB, Bot, Utils) و استفاده از async/await برای performance بالا.
- **پشتیبانی از migration دیتابیس**: با Alembic و مدل‌های SQLAlchemy.
- **سیستم لاگ حرفه‌ای**: پشتیبانی از rotating log، ارسال خطا به تلگرام ادمین.
- **مدیریت تنظیمات منعطف**: بارگذاری از YAML و env با اعتبارسنجی pydantic.
- **تست‌پذیری بالا**: تست‌های واحد برای کانفیگ، مدل‌ها و API.
- **سیستم نقش‌های کاربری**: کنترل دسترسی چندسطحه (User, Moderator, Admin, Super Admin).
- **مدیریت سرویس یکپارچه**: اسکریپت bash پیشرفته با پنل تعاملی و health check.
- **مستندسازی کامل**: پوشه docs و roadmap فنی/تجاری برای توسعه آینده.

---

## 4. ویژگی‌های جدید و بهبودها

### 🆕 **ویژگی‌های اضافه شده:**
- **سیستم نقش‌های کاربری**: مدیریت دسترسی چن��سطحه با کنترل دقیق
- **منوهای پیشرفته ادمین**: پنل‌های مدیریتی کامل با کنترل دسترسی
- **مدیریت سرویس پیشرفته**: `server_manager.sh` با پنل تعاملی و عملیات خودکار
- **کنترل دسترسی**: دکوراتورها و سیستم مجوزهای پیشرفته
- **بهینه‌سازی کد**: حذف فایل‌های تکراری و غیرضروری

### 🔧 **بهبودهای فنی:**
- **تمیزسازی کدبیس**: حذف فایل‌های deprecated و تکراری
- **بهینه‌سازی imports**: اصلاح مراجع و وابستگی‌ها
- **ساختار منظم**: سازماندهی بهتر فایل‌ها و پوشه‌ها
- **مستندسازی بروز**: به‌روزرسانی مستندات مطابق تغییرات

---

## 5. توصیه‌های مطالعه و توسعه
- برای توسعه feature جدید، ابتدا ساختار src/ و مدل‌های داده را بررسی کنید.
- برای افزودن دکتر جدید یا تغییر تنظیمات، از ربات تلگرام یا فایل config.yaml استفاده کنید.
- برای استقرار production، از server_manager.sh و فایل slothunter.service بهره ببرید.
- برای migration دیتابیس، از alembic و راهنمای آن استفاده کنید.
- برای تست و توسعه، تست‌های پوشه tests/ را اجرا و توسعه دهید.
- برای مدیریت نقش‌های کاربری، از سیستم user_roles استفاده کنید.

---

## 6. دستورات اجرا و مدیریت

### 🚀 **راه‌اندازی سریع:**
```bash
# راه‌اندازی کامل
./server_manager.sh setup

# اجرای سرویس
./server_manager.sh start

# پنل مدیریت تعاملی
./server_manager.sh
```

### 🔧 **دستورات مدیریتی:**
```bash
./server_manager.sh start     # شروع سرویس
./server_manager.sh stop      # توقف سرویس
./server_manager.sh restart   # راه‌اندازی مجدد
./server_manager.sh status    # وضعیت سرویس
./server_manager.sh logs      # مشاهده لاگ‌ها
./server_manager.sh stats     # آمار سیستم
./server_manager.sh test      # تست سیستم
```

### 📋 **اجرای مستقیم:**
```bash
# اجرای مستقیم پروژه
python src/main.py
```

---

**این پروژه آماده توسعه enterprise و مقیاس‌پذیر است و با رعایت best practiceهای معماری و توسعه Python طراحی شده است. پس از تمیزسازی و بهینه‌سازی، پروژه برای استقرار در محیط production لینوکس آماده می‌باشد.**