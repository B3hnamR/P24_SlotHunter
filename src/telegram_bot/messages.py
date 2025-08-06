"""
قالب‌های پیام برای ربات تلگرام - نسخه بهبود یافته
"""
from typing import List
from datetime import datetime

from src.api.models import Doctor, Appointment


def escape_markdown(text: str) -> str:
    """Escape کاراکترهای حساس Markdown برای تلگرام"""
    if not isinstance(text, str):
        return text
    for ch in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
        text = text.replace(ch, f'\\{ch}')
    return text

class MessageFormatter:
    """کلاس فرمت کردن پیام‌ها"""
    
    @staticmethod
    def welcome_message(user_name: str, is_returning: bool = False) -> str:
        """پیام خوش‌آمدگویی"""
        if is_returning:
            return f"""
👋 **سلام مجدد {user_name}!**

خوشحالیم که دوباره اینجایی! 😊

🎯 **چیکار می‌تونم برات بکنم؟**

🔍 **نوبت‌یابی هوشمند** - من مداوم نوبت‌های خ��لی رو چک می‌کنم
📱 **اطلاع‌رسانی فوری** - تا نوبت پیدا شد، بهت خبر می‌دم
👨‍⚕️ **چندین دکتر** - می‌تونی توی چندتا دکتر همزمان ثبت‌نام کنی

🚀 **آماده برای شروع؟**
            """
        else:
            return f"""
🎉 **سلام {user_name}! خوش اومدی!**

من ربات نوبت‌یاب پذیرش۲۴ هستم! 🤖

🤔 **چیکار می‌کنم؟**
به جای اینکه تو هر چند وقت یه بار بری سایت پذیرش۲۴ رو چک کنی، من این کارو برات انجام می‌دم! 

⚡ **چطور کار می‌کنه؟**
• تو فقط اسم دکتری که می‌خوای رو بهم بگو
• من هر چند دقیقه یه بار چک می‌کنم نوبت خالی داره یا نه
• تا نوبت پیدا شد، فوری بهت پیام می‌دم!

🎯 **مزیت‌ها:**
✅ دیگه نیازی نیست مداوم سایت رو چک کنی
✅ نوبت‌ها رو زودتر از بقیه پیدا می‌کنی
✅ می‌تونی چندتا دکتر رو همزمان رصد کنی

🚀 **بزن بریم شروع کنیم!**
            """
    
    @staticmethod
    def help_message() -> str:
        """پیام راهنما"""
        return """
📚 **راهنمای کامل ربات**

🎯 **من چیکار می‌کنم؟**
نوبت‌های خالی دکترها رو برات پیدا می‌کنم و فوری بهت خبر می‌دم!

🔍 **دستورات اصلی:**
• **مشاهده دکترها** - لیست دکترهای موجود
• **ثبت‌نام در دکتر** - برای رصد نوبت‌های خالی
• **لغو ثبت‌نام** - وقتی دیگه نیاز نداری

📱 **چطور استفاده کنم؟**
1️⃣ روی "👨‍⚕️ دکترها" بزن
2️⃣ دکتر مورد نظرت رو انتخاب کن
3️⃣ روی "📝 ثبت‌نام" بزن
4️⃣ منتظر باش تا نوبت پیدا کنم!

⚡ **نکات مهم:**
• تا نوبت پیدا شد، فوری بهت پیام می‌دم
• می‌تونی توی چندتا دکتر همزمان ثبت‌نام کنی
• نوبت‌ها خیلی سریع تموم میشن، پس سریع عمل کن!

🆘 **مشکل داری؟**
با ادمین تماس بگیر یا دوباره امتحان کن.
        """
    
    @staticmethod
    def doctor_list_message(doctors: List[Doctor]) -> str:
        """پیام لیست دکترها"""
        if not doctors:
            return """
😔 **هنوز دکتری اضافه نشده!**

💡 **چیکار کنم؟**
از ادمین بخواه دکترهای مورد نظرت رو اضافه کنه.
            """
        
        message = "👨‍⚕️ **دکترهای موجود:**\n\n"
        
        for i, doctor in enumerate(doctors, 1):
            status = "🟢" if doctor.is_active else "🔴"
            specialty = doctor.specialty if doctor.specialty else "عمومی"
            center_name = doctor.centers[0].center_name if doctor.centers else "مطب شخصی"
            
            message += f"{status} **{doctor.name}**\n"
            message += f"   🩺 {specialty}\n"
            message += f"   🏥 {center_name}\n\n"
        
        message += "💡 **برای ثبت‌نام روی دکتر مورد نظرت کلیک کن!**"
        return message
    
    @staticmethod
    def doctor_info_message(doctor: Doctor) -> str:
        """پیام اطلاعات دکتر"""
        specialty = doctor.specialty if doctor.specialty else "عمومی"
        center_name = doctor.centers[0].center_name if doctor.centers else "مطب شخصی"
        center_address = doctor.centers[0].center_address if doctor.centers and doctor.centers[0].center_address else "آدرس موجود نیست"
        center_phone = doctor.centers[0].center_phone if doctor.centers and doctor.centers[0].center_phone else "شماره موجود نیست"
        
        return f"""
👨‍⚕️ **{escape_markdown(doctor.name)}**

🩺 **تخصص:** {escape_markdown(specialty)}
🏥 **مطب/کلینیک:** {escape_markdown(center_name)}
📍 **آدرس:** {escape_markdown(center_address)}
📞 **تلفن:** {escape_markdown(center_phone)}

🔗 **لینک مستقیم پذیرش۲۴:**
https://www.paziresh24.com/dr/{escape_markdown(doctor.slug)}/

💡 **برای ثبت‌نام در رصد نوبت‌های این دکتر، دکمه زیر رو بزن:**
        """
    
    @staticmethod
    def appointment_alert_message(doctor: Doctor, appointments: List[Appointment]) -> str:
        """پیام اطلاع‌رسانی نوبت جدید"""
        if not appointments:
            return ""
        
        # گروه‌بندی نوبت‌ها بر اساس تاریخ
        dates_dict = {}
        for apt in appointments:
            date_str = apt.time_str.split(' ')[0]
            if date_str not in dates_dict:
                dates_dict[date_str] = []
            dates_dict[date_str].append(apt)
        
        specialty = doctor.specialty if doctor.specialty else "عمومی"
        center_name = doctor.centers[0].center_name if doctor.centers else "مطب شخصی"
        center_address = doctor.centers[0].center_address if doctor.centers and doctor.centers[0].center_address else "آدرس موجود نیست"
        
        message = f"""
🎉 **نوبت خالی پیدا شد!**

👨‍⚕️ **دکتر:** {escape_markdown(doctor.name)}
🩺 **تخصص:** {escape_markdown(specialty)}
🏥 **مطب/کلینیک:** {escape_markdown(center_name)}
📍 **آدرس:** {escape_markdown(center_address)}

📅 **نوبت‌های موجود:**
        """
        
        # نمایش نوبت‌ها بر اساس تاریخ
        for date_str, date_appointments in sorted(dates_dict.items()):
            message += f"\n🗓️ **{date_str}:**\n"
            
            # نمایش حداکثر 5 نوبت اول هر روز
            for apt in date_appointments[:5]:
                time_str = apt.time_str.split(' ')[1]
                message += f"   ⏰ {time_str} (نوبت #{apt.workhour_turn_num})\n"
            
            if len(date_appointments) > 5:
                message += f"   ... و {len(date_appointments) - 5} نوبت دیگر\n"
        
        message += f"""

🔗 **برای رزرو کلیک کن:**
https://www.paziresh24.com/dr/{escape_markdown(doctor.slug)}/

🏃‍♂️ **سریع باش! نوبت‌ها خیلی زود تموم میشن!**

💡 **نمی‌خوای دیگه پیام بگیری؟** از دکمه‌های زیر استفاده کن.
        """
        
        return message
    
    @staticmethod
    def subscription_success_message(doctor: Doctor) -> str:
        """پیام موفقیت اشتراک"""
        return f"""
✅ **عالی! ثبت‌نام شدی!**

حالا من مداوم نوبت‌های خالی **{doctor.name}** رو چک می‌کنم.

🔔 **تا نوبت پیدا شد، فوری بهت خبر می‌دم!**

📊 **می‌خوای ببینی توی چه دکترهایی ثبت‌نام کردی؟**
از دکمه "📊 وضعیت من" استفاده کن.

💡 **نکته:** نوبت‌ها معمولاً خیلی سریع تموم میشن، پس آماده باش!
        """
    
    @staticmethod
    def unsubscription_success_message(doctor: Doctor) -> str:
        """پیام موفقیت لغو اشتراک"""
        return f"""
✅ **باشه! لغو شد!**

دیگه برای **{doctor.name}** پیام نمی‌فرستم.

🔕 **اگه بعداً دوباره خواستی، می‌تونی دوباره ثبت‌نام کنی.**

📊 **می‌خوای ببینی هنوز توی چه دکترهایی ثبت‌نامی؟**
از دکمه "📊 وضعیت من" استفاده کن.
        """
    
    @staticmethod
    def subscription_status_message(subscriptions: List[tuple]) -> str:
        """پیام وضعیت اشتراک‌ها"""
        if not subscriptions:
            return """
📊 **وضعیت ثبت‌نام‌های تو**

😔 **هنوز توی هیچ دکتری ثبت‌نام نکردی!**

💡 **چیکار کنی؟**
برو قسمت "👨‍⚕️ دکترها" و دکتر مورد نظرت رو انتخاب کن.
            """
        
        message = "📊 **وضعیت ثبت‌نام‌های تو:**\n\n"
        
        for i, (doctor, sub_date) in enumerate(subscriptions, 1):
            date_str = sub_date.strftime('%Y/%m/%d') if sub_date else "نامشخص"
            specialty = doctor.specialty if doctor.specialty else "عمومی"
            
            message += f"✅ **{doctor.name}**\n"
            message += f"   🩺 {specialty}\n"
            message += f"   📅 ثبت‌نام شدی: {date_str}\n\n"
        
        message += "💡 **می‌خوای از یکیشون لغو ثبت‌نام کنی؟** از دکمه‌های زیر استفاده کن."
        return message
    
    @staticmethod
    def error_message(error_text: str = "یه مشکلی پیش اومد") -> str:
        """پیام خطا"""
        return f"""
😅 **اوپس! {error_text}**

🔄 **چیکار کنی؟**
• یه بار دیگه امتحان کن
• اگه بازم نشد، با ادمین تماس بگیر

💡 **معمولاً با یه بار امتحان دوباره درست میشه!**
        """
    
    @staticmethod
    def admin_report_message(stats: dict) -> str:
        """گزارش ادمین"""
        return f"""
📊 **گزارش سیستم**

👥 **کاربران:** {stats.get('total_users', 0)}
👨‍⚕️ **دکترها:** {stats.get('total_doctors', 0)}
📝 **ثبت‌نام‌ها:** {stats.get('total_subscriptions', 0)}
🎯 **نوبت‌های پیدا شده امروز:** {stats.get('appointments_found_today', 0)}

⏰ **آخرین بررسی:** {stats.get('last_check', 'نامشخص')}
���� **وضعیت سیستم:** {stats.get('system_status', 'فعال')}

💾 **حافظه:** {stats.get('memory_usage', 'نامشخص')}
🌐 **شبکه:** {stats.get('network_status', 'متصل')}
        """

    @staticmethod
    def access_denied_message() -> str:
        """پیام عدم دسترسی"""
        return "❌ **متاسفانه دسترسی ادمین نداری!**"

    @staticmethod
    def admin_stats_message(stats: dict) -> str:
        """پیام آمار ادمین"""
        return f"""
📊 **آمار سیستم P24_SlotHunter**

👥 **کاربران فعال:** {stats.get('total_users', 0)}
👨‍⚕️ **کل دکترها:** {stats.get('total_doctors', 0)}
✅ **دکترهای فعال:** {stats.get('active_doctors', 0)}
📝 **ثبت‌نام‌های فعال:** {stats.get('total_subscriptions', 0)}
🎯 **نوبت‌های پیدا شده امروز:** {stats.get('appointments_today', 0)}

⏰ **آخرین بررسی:** در حال اجرا
🔄 **وضعیت سیستم:** فعال و سالم
        """

    @staticmethod
    def user_management_message(users: list) -> str:
        """پیام مدیریت کاربران"""
        user_list = "👥 **آخرین کاربران:**\n\n"
        for i, user in enumerate(users, 1):
            subscription_count = len([sub for sub in user.subscriptions if sub.is_active])
            admin_badge = " 🔧" if user.is_admin else ""
            user_list += f"{i}. {user.full_name}{admin_badge}\n"
            user_list += f"   📱 ID: `{user.telegram_id}`\n"
            user_list += f"   📝 ثبت‌نام‌ها: {subscription_count}\n\n"
        return user_list

    @staticmethod
    def access_settings_message() -> str:
        """پیام تنظیمات دسترسی"""
        return """
🔒 **تنظیمات دسترسی**

⚠️ **وضعیت فعلی:** ربات برای همه در دسترس است

🔧 **برای محدود کردن دسترسی:**
1. از منوی مدیریت سرور استفاده کنید
2. گزینه "Access Control" را انتخاب کنید
3. لیست کاربران مجاز را تنظیم کنید

💡 **نکته:** تغییرات از طریق سرور اعمال می‌شود
        """

    @staticmethod
    def returning_user_message(user_name: str, last_activity: datetime = None) -> str:
        """پیام برای کاربر بازگشتی"""
        if last_activity:
            last_visit = last_activity.strftime('%Y/%m/%d %H:%M')
        else:
            last_visit = "نامشخص"
            
        return f"""
👋 **سلام مجدد {user_name}!**

خوشحالیم که دوباره اینجایی! 😊

📊 **وضعیت سریع:**
• آخرین بازدید: {last_visit}
• حساب کاربری: ✅ فعال

🚀 **آماده برای شروع؟**
        """

    @staticmethod
    def add_doctor_prompt_message() -> str:
        """پیام درخواست اضافه کردن دکتر"""
        return """
🆕 **اضافه کردن دکتر جدید**

📝 **چطور کار می‌کنه؟**
فقط لینک صفحه دکت�� رو از سایت پذیرش۲۴ برام بفرست!

🔗 **مثال لینک:**
`https://www.paziresh24.com/dr/دکتر-احمد-محمدی-0/`

💡 **راه‌های ارسال:**
• کل لینک رو کپی کن و بفرست
• یا فقط قسمت `دکتر-احمد-محمدی-0` رو بفرست

⚡ **من خودم اطلاعات دکتر رو استخراج می‌کنم!**
        """

    @staticmethod
    def doctor_extraction_success_message(doctor_name: str) -> str:
        """پیام موفقیت استخراج دکتر"""
        return f"""
✅ **عالی! دکتر اضافه شد!**

👨‍⚕️ **{doctor_name}** با موفقیت به سیستم اضافه شد.

🎯 **حالا می‌تونی:**
• توی این دکتر ثبت‌نام کنی
• منتظر باشی تا نوبت‌های خالی رو برات پیدا کنم

💡 **برای ثبت‌نام برو قسمت "👨‍⚕️ دکترها"**
        """

    @staticmethod
    def doctor_extraction_failed_message() -> str:
        """پیام شکست استخراج دکتر"""
        return """
😔 **متاسفانه نتونستم اطلاعات دکتر رو پیدا کنم!**

🔍 **چیکار کنی؟**
• مطمئن شو لینک درسته
• دوباره امتحان کن
• یا ��ا ادمین تماس بگیر

💡 **مثال لینک درست:**
`https://www.paziresh24.com/dr/دکتر-احمد-محمدی-0/`
        """