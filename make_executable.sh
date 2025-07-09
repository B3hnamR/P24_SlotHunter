#!/bin/bash
# اسکریپت executable کردن فایل‌ها

echo "🔧 Executable کردن فایل‌ها..."

chmod +x server_manager.sh
chmod +x p24-admin
chmod +x p24

echo "✅ فایل‌های زیر executable شدند:"
echo "  - server_manager.sh"
echo "  - p24-admin"
echo "  - p24"

echo ""
echo "🚀 حالا می‌توانید استفاده کنید:"
echo "  ./p24-admin     # پنل مدیریت سرور"
echo "  ./p24 run       # اجرای پروژه"