"""
قالب‌های پیام برای ربات تلگرام
"""
from typing import List
from datetime import datetime

from src.api.models import Doctor, Appointment


class MessageFormatter:
    """کلاس فرمت کردن پیام‌ها"""
    
    @staticmethod
    def welcome_message(user_name: str) -> str:
        """پیام خوش‌آمدگویی"""
        return f"""
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
    
    @staticmethod
    def help_message() -> str:
        """پیام راهنما"""
        return """
📚 **راهنمای استفاده:**

🔍 **مشاهده دکترها:**
/doctors - لیست تمام دکترهای موجود

📝 **مدیریت اشتراک:**
/subscribe - اشتراک در دکتر جدید
/unsubscribe - لغو اشتراک از دکتر
/status - مشاهده اشتراک‌های فعلی

ℹ️ **اطلاعات:**
/help - نمایش این راهنما

⚡ **نکات مهم:**
• پس از اشتراک، هر نوبت خالی فوراً به شما اطلاع داده می‌شود
• می‌توانید در چندین دکتر همزمان مشترک شوید
• برای لغو اشتراک از دستور /unsubscribe استفاده کنید

🆘 **پشتیبانی:**
در صورت بروز مشکل، با ادمین تماس بگیرید.
        """
    
    @staticmethod
    def doctor_list_message(doctors: List[Doctor]) -> str:
        """پیام لیست دکترها"""
        if not doctors:
            return "❌ هیچ دکتری در سیستم ثبت نشده است."
        
        message = "👨‍⚕️ **لیست دکترهای موجود:**\n\n"
        
        for i, doctor in enumerate(doctors, 1):
            status = "✅" if doctor.is_active else "⏸️"
            message += f"{status} **{i}. {doctor.name}**\n"
            message += f"   🏥 {doctor.specialty}\n"
            message += f"   📍 {doctor.center_name}\n\n"
        
        message += "💡 برای اشتراک از دستور /subscribe استفاده کنید."
        return message
    
    @staticmethod
    def doctor_info_message(doctor: Doctor) -> str:
        """پیام اطلاعات دکتر"""
        return f"""
👨‍⚕️ **{doctor.name}**

🏥 **تخصص:** {doctor.specialty}
🏢 **مرکز:** {doctor.center_name}
📍 **آدرس:** {doctor.center_address}
📞 **تلفن:** {doctor.center_phone}

🔗 **لینک مستقیم:**
https://www.paziresh24.com/dr/{doctor.slug}/

💡 برای اشتراک در این دکتر، دکمه زیر را فشار دهید.
        """
    
    @staticmethod
    def appointment_alert_message(doctor: Doctor, appointments: List[Appointment]) -> str:
        """پیام اطلاع‌رسانی نوبت جدید"""
        if not appointments:
            return ""
        
        # گروه‌بندی نوبت‌ها بر اساس تاریخ
        dates_dict = {}
        for apt in appointments:
            date_str = apt.start_datetime.strftime('%Y/%m/%d')
            if date_str not in dates_dict:
                dates_dict[date_str] = []
            dates_dict[date_str].append(apt)
        
        message = f"""
🎯 **نوبت خالی پیدا شد!**

👨‍⚕️ **دکتر:** {doctor.name}
🏥 **مرکز:** {doctor.center_name}
📍 **آدرس:** {doctor.center_address}

📅 **نوبت‌های موجود:**
        """
        
        # نمایش نوبت‌ها بر اساس تاریخ
        for date_str, date_appointments in sorted(dates_dict.items()):
            message += f"\n🗓️ **{date_str}:**\n"
            
            # نمایش حداکثر 5 نوبت اول هر روز
            for apt in date_appointments[:5]:
                time_str = apt.start_datetime.strftime('%H:%M')
                message += f"   ⏰ {time_str} (نوبت #{apt.workhour_turn_num})\n"
            
            if len(date_appointments) > 5:
                message += f"   ... و {len(date_appointments) - 5} نوبت دیگر\n"
        
        message += f"""
🔗 **لینک رزرو:**
https://www.paziresh24.com/dr/{doctor.slug}/

⚡ **سریع عمل کنید! نوبت‌ها ممکن است زود تمام شوند.**

📱 برای لغو اشتراک از دستور /unsubscribe استفاده کنید.
        """
        
        return message
    
    @staticmethod
    def subscription_success_message(doctor: Doctor) -> str:
        """پیام موفقیت اشتراک"""
        return f"""
✅ **اشتراک موفق!**

شما با موفقیت در دکتر **{doctor.name}** مشترک شدید.

🔔 از این پس، هر نوبت خالی فوراً به شما اطلاع داده می‌شود.

📊 برای مشاهده وضعیت اشتراک‌ها از دستور /status استفاده کنید.
        """
    
    @staticmethod
    def unsubscription_success_message(doctor: Doctor) -> str:
        """پیام موفقیت لغو اشتراک"""
        return f"""
✅ **لغو اشتراک موفق!**

اشتراک شما از دکتر **{doctor.name}** لغو شد.

🔕 دیگر اطلاع‌رسانی نوبت‌های این دکتر دریافت نخواهید کرد.

📊 برای مشاهده اشتراک‌های باقی‌مانده از دستور /status استفاده کنید.
        """
    
    @staticmethod
    def subscription_status_message(subscriptions: List[tuple]) -> str:
        """پیام وضعیت اشتراک‌ها"""
        if not subscriptions:
            return """
📊 **وضعیت اشتراک‌ها**

❌ شما در هیچ دکتری مشترک نیستید.

💡 برای اشتراک از دستور /subscribe استفاده ک��ی��.
            """
        
        message = "📊 **وضعیت اشتراک‌ها:**\n\n"
        
        for i, (doctor, sub_date) in enumerate(subscriptions, 1):
            date_str = sub_date.strftime('%Y/%m/%d') if sub_date else "نامشخص"
            message += f"✅ **{i}. {doctor.name}**\n"
            message += f"   🏥 {doctor.specialty}\n"
            message += f"   📅 تاریخ اشتراک: {date_str}\n\n"
        
        message += "💡 برای لغو اشتراک از دستور /unsubscribe استفاده کنید."
        return message
    
    @staticmethod
    def error_message(error_text: str = "یک خطای پیش‌بینی نشده رخ داده است.") -> str:
        """پیام خطای عمومی"""
        return f"""
❌ **خطا**

{error_text}

🔄 لطفاً دوباره تلاش کنید. در صورت تکرار مشکل، با پشتیبانی تماس بگیرید.
        """

    @staticmethod
    def db_error_message() -> str:
        """پیام خطای دیتابیس"""
        return """
❌ **خطای سرور**

مشکلی در ارتباط با دیتابیس پیش آمده است. تیم فنی در حال بررسی مشکل است.

🙏 لطفاً چند دقیقه دیگر دوباره تلاش کنید.
        """
    
    @staticmethod
    def admin_report_message(stats: dict) -> str:
        """گزارش ادمین"""
        return f"""
📊 **گزارش سیستم**

👥 **کاربران:** {stats.get('total_users', 0)}
👨‍⚕️ **دکترها:** {stats.get('total_doctors', 0)}
📝 **اشتراک‌ها:** {stats.get('total_subscriptions', 0)}
🎯 **نوبت‌های پیدا شده امروز:** {stats.get('appointments_found_today', 0)}

⏰ **آخرین بررسی:** {stats.get('last_check', 'نامشخص')}
🔄 **وضعیت سیستم:** {stats.get('system_status', 'فعال')}

💾 **حافظه:** {stats.get('memory_usage', 'نامشخص')}
🌐 **شبکه:** {stats.get('network_status', 'متصل')}
        """