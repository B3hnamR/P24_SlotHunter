"""
قالب‌های پیام برای ربات تلگرام - نسخه HTML
"""
from typing import List
from datetime import datetime
import html

from src.api.models import Doctor, Appointment


def escape_html(text: str) -> str:
    """Escape کاراکترهای حساس برای HTML تلگرام"""
    if not isinstance(text, str):
        return text
    return html.escape(text)


class MessageFormatter:
    """کلاس فرمت کردن پیام‌ها (HTML)"""

    @staticmethod
    def welcome_message(user_name: str, is_returning: bool = False) -> str:
        """پیام خوش‌آمدگویی"""
        if is_returning:
            return f"""
👋 <b>سلام مجدد {escape_html(user_name)}!</b>

خوشحالیم که دوباره اینجایی! 😊

🎯 <b>چیکار می‌تونم برات بکنم؟</b>

🔍 <b>نوبت‌یابی هوشمند</b> - من مداوم نوبت‌های خالی رو چک می‌کنم
📱 <b>اطلاع‌رسانی فوری</b> - تا نوبت پیدا شد، بهت خبر می‌دم
👨‍⚕️ <b>چندین دکتر</b> - می‌تونی توی چندتا دکتر همزمان ثبت‌نام کنی

🚀 <b>آماده برای شروع؟</b>
            """
        else:
            return f"""
🎉 <b>سلام {escape_html(user_name)}! خوش اومدی!</b>

من ربات نوبت‌یاب پذیرش۲۴ هستم! 🤖

🤔 <b>چیکار می‌کنم؟</b>
به جای اینکه تو هر چند وقت یه بار بری سایت پذیرش۲۴ رو چک کنی، من این کارو برات انجام می‌دم!

⚡ <b>چطور کار می‌کنه؟</b>
• تو فقط اسم دکتری که می‌خوای رو بهم بگو
• من هر چند دقیقه یه بار چک می‌کنم نوبت خالی داره یا نه
• تا نوبت پیدا شد، فوری بهت پیام می‌دم!

🎯 <b>مزیت‌ها:</b>
✅ دیگه نیازی نیست مداوم سایت رو چک کنی
✅ نوبت‌ها رو زودتر از بقیه پیدا می‌کنی
✅ می‌تونی چندتا دکتر رو همزمان رصد کنی

🚀 <b>بزن بریم شروع کنیم!</b>
            """

    @staticmethod
    def help_message() -> str:
        """پیام راهنما"""
        return """
📚 <b>راهنمای کامل ربات</b>

🎯 <b>من چیکار می‌کنم؟</b>
نوبت‌های خالی دکترها رو برات پیدا می‌کنم و فوری بهت خبر می‌دم!

🔍 <b>دستورات اصلی:</b>
• <b>مشاهده دکترها</b> - لیست دکترهای موجود
• <b>ثبت‌نام در دکتر</b> - برای رصد نوبت‌های خالی
• <b>لغو ثبت‌نام</b> - وقتی دیگه نیاز نداری

📱 <b>چطور استفاده کنم؟</b>
1️⃣ روی "👨‍⚕️ دکترها" بزن
2️⃣ دکتر مورد نظرت رو انتخاب کن
3️⃣ روی "📝 ثبت‌نام" بزن
4️⃣ منتظر باش تا نوبت پیدا کنم!

⚡ <b>نکات مهم:</b>
• تا نوبت پیدا شد، فوری بهت پیام می‌دم
• می‌تونی توی چندتا دکتر همزمان ثبت‌نام کنی
• نوبت‌ها خیلی سریع تموم میشن، پس سریع عمل کن!

🆘 <b>مشکل داری؟</b>
با ادمین تماس بگیر یا دوباره امتحان کن.
        """

    @staticmethod
    def doctor_list_message(doctors: List[Doctor]) -> str:
        """پیام لیست دکترها"""
        if not doctors:
            return """
😔 <b>هنوز دکتری اضافه نشده!</b>

💡 <b>چیکار کنم؟</b>
از ادمین بخواه دکترهای مورد نظرت رو اضافه کنه.
            """

        message = "👨‍⚕️ <b>دکترهای موجود:</b>\n\n"

        for i, doctor in enumerate(doctors, 1):
            status = "🟢" if doctor.is_active else "🔴"
            specialty = doctor.specialty if doctor.specialty else "عمومی"
            center_name = doctor.centers[0].center_name if doctor.centers else "مطب شخصی"

            message += f"{status} <b>{escape_html(doctor.name)}</b>\n"
            message += f"   🩺 {escape_html(specialty)}\n"
            message += f"   🏥 {escape_html(center_name)}\n\n"

        message += "💡 <b>برای ثبت‌نام روی دکتر مورد نظرت کلیک کن!</b>"
        return message

    @staticmethod
    def doctor_info_message(doctor: Doctor) -> str:
        """پیام اطلاعات دکتر"""
        specialty = doctor.specialty if doctor.specialty else "عمومی"
        center_name = doctor.centers[0].center_name if doctor.centers else "مطب شخصی"
        center_address = doctor.centers[0].center_address if doctor.centers and doctor.centers[0].center_address else "آدرس موجود نیست"
        center_phone = doctor.centers[0].center_phone if doctor.centers and doctor.centers[0].center_phone else "شماره موجود نیست"

        return f"""
<b>👨‍⚕️ {escape_html(doctor.name)}</b>

🩺 <b>تخصص:</b> {escape_html(specialty)}
🏥 <b>مطب/کلینیک:</b> {escape_html(center_name)}
📍 <b>آدرس:</b> {escape_html(center_address)}
📞 <b>تلفن:</b> {escape_html(center_phone)}

🔗 <b>لینک مستقیم پذیرش۲۴:</b>
https://www.paziresh24.com/dr/{escape_html(doctor.slug)}/

💡 <b>برای ثبت‌نام در رصد نوبت‌های این دکتر، دکمه زیر رو بزن:</b>
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
🎉 <b>نوبت خالی پیدا شد!</b>

👨‍⚕️ <b>دکتر:</b> {escape_html(doctor.name)}
🩺 <b>تخصص:</b> {escape_html(specialty)}
🏥 <b>مطب/کلینیک:</b> {escape_html(center_name)}
📍 <b>آدرس:</b> {escape_html(center_address)}

📅 <b>نوبت‌های موجود:</b>
        """

        # نمایش نوبت‌ها بر اساس تاریخ
        for date_str, date_appointments in sorted(dates_dict.items()):
            message += f"\n🗓️ <b>{escape_html(date_str)}:</b>\n"

            # نمایش حداکثر 5 نوبت اول هر روز
            for apt in date_appointments[:5]:
                time_str = apt.time_str.split(' ')[1]
                message += f"   ⏰ {escape_html(time_str)} (نوبت #{apt.workhour_turn_num})\n"

            if len(date_appointments) > 5:
                message += f"   ... و {len(date_appointments) - 5} نوبت دیگر\n"

        message += f"""

🔗 <b>برای رزرو کلیک کن:</b>
https://www.paziresh24.com/dr/{escape_html(doctor.slug)}/

🏃‍♂️ <b>سریع باش! نوبت‌ها خیلی زود تموم میشن!</b>

💡 <b>نمی���خوای دیگه پیام بگیری؟</b> از دکمه‌های زیر استفاده کن.
        """

        return message

    @staticmethod
    def subscription_success_message(doctor: Doctor) -> str:
        """پیام موفقیت اشتراک"""
        return f"""
✅ <b>عالی! ثبت‌نام شدی!</b>

حالا من مداوم نوبت‌های خالی <b>{escape_html(doctor.name)}</b> رو چک می‌کنم.

🔔 <b>تا نوبت پیدا شد، فوری بهت خبر می‌دم!</b>

📊 <b>می‌خوای ببینی توی چه دکترهایی ثبت‌نام کردی؟</b>
از دکمه "📊 وضعیت من" استفاده کن.

💡 <b>نکته:</b> نوبت‌ها معمولاً خیلی سریع تموم میشن، پس آماده باش!
        """

    @staticmethod
    def unsubscription_success_message(doctor: Doctor) -> str:
        """پیام موفقیت لغو اشتراک"""
        return f"""
✅ <b>باشه! لغو شد!</b>

دیگه برای <b>{escape_html(doctor.name)}</b> پیام نمی‌فرستم.

🔕 <b>اگه بعداً دوباره خواستی، می‌تونی دوباره ثبت‌نام کنی.</b>

📊 <b>می‌خوای ببینی هنوز توی چه دکترهایی ثبت‌نامی؟</b>
از دکمه "📊 وضعیت من" استفاده کن.
        """

    @staticmethod
    def subscription_status_message(subscriptions: List[tuple]) -> str:
        """پیام وضعیت اشتراک‌ها"""
        if not subscriptions:
            return """
📊 <b>وضعیت ثبت‌نام‌های تو</b>

😔 <b>هنوز توی هیچ دکتری ثبت‌نام نکردی!</b>

💡 <b>چیکار کنی؟</b>
برو قسمت "👨‍⚕️ دکترها" و دکتر مورد نظرت رو انتخاب کن.
            """

        message = "📊 <b>وضعیت ثبت‌نام‌های تو:</b>\n\n"

        for i, (doctor, sub_date) in enumerate(subscriptions, 1):
            date_str = sub_date.strftime('%Y/%m/%d') if sub_date else "نامشخص"
            specialty = doctor.specialty if doctor.specialty else "عمومی"

            message += f"✅ <b>{escape_html(doctor.name)}</b>\n"
            message += f"   🩺 {escape_html(specialty)}\n"
            message += f"   📅 ثبت‌نام شدی: {escape_html(date_str)}\n\n"

        message += "💡 <b>می‌خوای از یکیشون لغو ثبت‌نام کنی؟</b> از دکمه‌های زیر استفاده کن."
        return message

    @staticmethod
    def error_message(error_text: str = "یه مشکلی پیش اومد") -> str:
        """پیام خطا"""
        return f"""
😅 <b>اوپس! {escape_html(error_text)}</b>

🔄 <b>چیکار کنی؟</b>
• یه بار دیگه امتحان کن
• اگه بازم نشد، با ادمین تماس بگیر

💡 <b>معمولاً با یه بار امتحان دوباره درست میشه!</b>
        """

    @staticmethod
    def admin_report_message(stats: dict) -> str:
        """گزارش ادمین"""
        return f"""
📊 <b>گزارش سیستم</b>

👥 <b>کاربران:</b> {stats.get('total_users', 0)}
👨‍⚕️ <b>دکترها:</b> {stats.get('total_doctors', 0)}
📝 <b>ثبت‌نام‌ها:</b> {stats.get('total_subscriptions', 0)}
🎯 <b>نوبت‌های پیدا شده امروز:</b> {stats.get('appointments_found_today', 0)}

⏰ <b>آخرین بررسی:</b> {escape_html(stats.get('last_check', 'نامشخص'))}
🔄 <b>وضعیت سیستم:</b> {escape_html(stats.get('system_status', 'فعال'))}

💾 <b>حافظه:</b> {escape_html(stats.get('memory_usage', 'نامشخص'))}
🌐 <b>شبکه:</b> {escape_html(stats.get('network_status', 'متصل'))}
        """

    @staticmethod
    def access_denied_message() -> str:
        """پیام عدم دسترسی"""
        return "❌ <b>متاسفانه دسترسی ادمین نداری!</b>"

    @staticmethod
    def admin_stats_message(stats: dict) -> str:
        """پیام آمار ادمین"""
        return f"""
📊 <b>آمار سیستم P24_SlotHunter</b>

👥 <b>کاربران فعال:</b> {stats.get('total_users', 0)}
👨‍⚕️ <b>کل دکترها:</b> {stats.get('total_doctors', 0)}
✅ <b>دکترهای فعال:</b> {stats.get('active_doctors', 0)}
📝 <b>ثبت‌نام‌های فعال:</b> {stats.get('total_subscriptions', 0)}
🎯 <b>نوبت‌های پیدا شده امروز:</b> {stats.get('appointments_today', 0)}

⏰ <b>آخرین بررسی:</b> در حال اجرا
🔄 <b>وضعیت سیستم:</b> فعال و سالم
        """

    @staticmethod
    def user_management_message(users: list) -> str:
        """پیام مدیریت کاربران"""
        user_list = "👥 <b>آخرین کاربران:</b>\n\n"
        for i, user in enumerate(users, 1):
            subscription_count = len([sub for sub in user.subscriptions if sub.is_active])
            admin_badge = " 🔧" if user.is_admin else ""
            user_list += f"{i}. {escape_html(user.full_name)}{admin_badge}\n"
            user_list += f"   📱 ID: <code>{escape_html(str(user.telegram_id))}</code>\n"
            user_list += f"   📝 ثبت‌نام‌ها: {subscription_count}\n\n"
        return user_list

    @staticmethod
    def access_settings_message() -> str:
        """پیام تنظیمات دسترسی"""
        return """
🔒 <b>تنظیمات دسترسی</b>

⚠️ <b>وضعیت فعلی:</b> ربات برای همه در دسترس است

🔧 <b>برای محدود کردن دسترسی:</b>
1. از منوی مدیریت سرور استفاده کنید
2. گزینه "Access Control" را انتخاب کنید
3. لیست کاربران مجاز را تنظیم کنید

💡 <b>نکته:</b> تغییرات از طریق سرور اعمال می‌شود
        """

    @staticmethod
    def returning_user_message(user_name: str, last_activity: datetime = None) -> str:
        """پیام برای کاربر بازگشتی"""
        if last_activity:
            last_visit = last_activity.strftime('%Y/%m/%d %H:%M')
        else:
            last_visit = "نامشخص"

        return f"""
👋 <b>سلام مجدد {escape_html(user_name)}!</b>

خوشحالیم که دوباره اینجایی! 😊

📊 <b>وضعیت سریع:</b>
• آخرین بازدید: {escape_html(last_visit)}
• حساب کاربری: ✅ فعال

🚀 <b>آماده برای شروع؟</b>
        """

    @staticmethod
    def add_doctor_prompt_message() -> str:
        """پیام درخواست اضافه کردن دکتر"""
        return """
🆕 <b>اضافه کردن دکتر جدید</b>

📝 <b>چطور کار می‌کنه؟</b>
فقط لینک صفحه دکتر رو از سایت پذیرش۲۴ برام بفرست!

🔗 <b>مثال لینک:</b>
<code>https://www.paziresh24.com/dr/دکتر-احمد-محمدی-0/</code>

💡 <b>راه‌های ارسال:</b>
• کل لینک رو کپی کن و بفرست
• یا فقط قسمت <code>دکتر-احمد-محمدی-0</code> رو بفرست

⚡ <b>من خودم اطلاعات دکتر رو استخراج می‌کنم!</b>
        """

    @staticmethod
    def doctor_extraction_success_message(doctor_name: str) -> str:
        """پیام موفقیت استخراج دکتر"""
        return f"""
✅ <b>عالی! دکتر اضافه شد!</b>

👨‍⚕️ <b>{escape_html(doctor_name)}</b> با موفقیت به سیستم اضافه شد.

🎯 <b>حالا می‌تونی:</b>
• توی این دکتر ثبت‌نام کنی
• منتظر باشی تا نوبت‌های خالی رو برات پیدا کنم

💡 <b>برای ثبت‌نام برو قسمت "👨‍⚕️ دکترها"</b>
        """

    @staticmethod
    def doctor_extraction_failed_message() -> str:
        """پیام شکست استخراج دکتر"""
        return """
😔 <b>متاسفانه نتونستم اطلاعات دکتر ر�� پیدا کنم!</b>

🔍 <b>چیکار کنی؟</b>
• مطمئن شو لینک درسته
• دوباره امتحان کن
• یا با ادمین تماس بگیر

💡 <b>مثال لینک درست:</b>
<code>https://www.paziresh24.com/dr/دکتر-احمد-محمدی-0/</code>
        """