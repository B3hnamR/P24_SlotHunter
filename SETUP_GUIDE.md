# 🚀 راهنمای سریع راه‌اندازی P24_SlotHunter

## 📋 **مراحل راه‌اندازی (برای سرور خام)**

### 1️⃣ **تست اولیه (بدون dependency)**
```bash
python3 simple_test.py
```

### 2️⃣ **راه‌اندازی خودکار**
```bash
chmod +x server_manager.sh
./server_manager.sh
```

### 3️⃣ **یا راه‌اندازی دستی**
```bash
# ایجاد virtual environment
python3 -m venv venv

# فعال‌سازی
source venv/bin/activate

# نصب dependencies
pip install -r requirements.txt

# تست dependencies
python check_dependencies.py

# تنظیم .env
cp .env.example .env
nano .env  # ویرایش توکن و chat ID

# اجرای سرویس
./server_manager.sh start
```

## 🔧 **حل مشکلات رایج**

### ❌ **"No module named 'dotenv'"**
```bash
source venv/bin/activate
pip install python-dotenv
```

### ❌ **"Virtual environment not found"**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ **"Bot token not configured"**
```bash
nano .env
# تنظیم TELEGRAM_BOT_TOKEN و ADMIN_CHAT_ID
```

## 📱 **دریافت توکن ربات**

1. به @BotFather در تلگرام پیام دهید
2. دستور `/newbot` را ارسال کنید
3. نام و username ربات را انتخاب کنید
4. توکن دریافتی را در `.env` قرار دهید

## 👤 **دریافت Chat ID**

1. به @userinfobot در تلگرام پیام دهید
2. Chat ID خود را کپی کنید
3. در `.env` قرار دهید

## 🎯 **تست نهایی**

```bash
# فعال‌سازی محیط
source venv/bin/activate

# تست کامل
python check_dependencies.py

# اجرای سرویس
./server_manager.sh start
```

## 📊 **مانیتورینگ**

```bash
# وضعیت سرویس
./server_manager.sh status

# مشاهده لاگ‌ها
./server_manager.sh logs

# آمار سیستم
./server_manager.sh stats
```

## 🆘 **در صورت مشکل**

1. **تست ساده:** `python3 simple_test.py`
2. **بررسی dependencies:** `python check_dependencies.py`
3. **راه‌اندازی مجدد:** `./server_manager.sh setup`
4. **مشاهده لاگ خطا:** `./server_manager.sh logs`

---

**نکته:** همیشه ابتدا `source venv/bin/activate` را اجرا کنید!