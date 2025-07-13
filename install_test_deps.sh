ff#!/bin/bash

# نصب وابستگی‌های تست برای لینوکس
echo "🐧 نصب وابستگی‌های تست برای لینوکس..."

# بررسی Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 یافت نشد. لطفاً نصب کنید:"
    echo "   sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi

# بررسی pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 یافت نشد. لطفاً نصب کنید:"
    echo "   sudo apt install python3-pip"
    exit 1
fi

echo "✅ Python3 و pip3 موجود است"

# نصب وابستگی‌ها
echo "📦 نصب وابستگی‌های مورد نیاز..."

pip3 install --user httpx beautifulsoup4

echo "✅ وابستگی‌ها نصب شدند"

# اجازه اجرا برای اسکریپت
chmod +x test_doctor_extraction.py

echo "🎯 آماده برای تست!"
echo ""
echo "🚀 برای اجرا:"
echo "   python3 test_doctor_extraction.py"
echo ""
echo "🔗 یا با URL سفارشی:"
echo "   python3 test_doctor_extraction.py 'https://www.paziresh24.com/dr/doctor-name/'"