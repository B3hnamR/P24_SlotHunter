import pytest
from src.telegram_bot.messages import MessageFormatter

def test_welcome_message():
    """
    Tests the welcome_message function to ensure it formats the welcome message correctly.
    """
    user_name = "Jules"
    expected_message = f"""
🎯 **سلام {user_name}!**

به ربات نوبت‌یاب پذیرش۲۴ خوش آمدید!

🔍 **امکانات:**
• نظارت مداوم بر نوبت‌های خالی
• اطلاع‌رسانی فوری از طریق تلگرام
• پشتیبانی از چندین دکتر همزمان

📋 **دستورات:**
/doctors - مشاهده لیست دکترها
/subscribe - اشتراک در دکتر
/unsubscribe - لغو اشتراک
/status - وضعیت اشتراک‌های من
/help - راهنما

🚀 برای شروع، از دستور /doctors استفاده کنید.
        """
    assert MessageFormatter.welcome_message(user_name) == expected_message
