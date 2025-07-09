#!/bin/bash
# اسکریپت راه‌اندازی Virtual Environment

echo "🔧 راه‌اندازی Virtual Environment برای P24_SlotHunter..."

# بررسی وجود python3-venv
if ! dpkg -l | grep -q python3-venv; then
    echo "📦 نصب python3-venv..."
    apt update
    apt install python3-venv python3-full -y
fi

# ایجاد virtual environment
echo "🏗️ ایجاد virtual environment..."
python3 -m venv venv

# فعال‌سازی
echo "⚡ فعال‌سازی virtual environment..."
source venv/bin/activate

# به‌روزرسانی pip
echo "📦 به‌روزرسانی pip..."
pip install --upgrade pip

# نصب dependencies
echo "📚 نصب dependencies..."
pip install -r requirements.txt

echo "✅ Virtual environment آماده است!"
echo ""
echo "🚀 برای استفاده:"
echo "source venv/bin/activate"
echo "python check_dependencies.py"
echo ""
echo "🛑 برای خروج از virtual environment:"
echo "deactivate"