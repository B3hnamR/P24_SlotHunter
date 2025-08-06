"""
Handlers مربوط به مدیریت دکترها
"""
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy import select
from typing import List
from datetime import datetime

from src.database.models import User, Doctor, Subscription
from src.api.doctor_manager import DoctorManager
from src.api.enhanced_paziresh_client import EnhancedPazireshAPI
from src.utils.logger import get_logger

logger = get_logger("DoctorHandlers")

# States برای ConversationHandler
ADD_DOCTOR_URL = 1


class DoctorHandlers:
    """کلاس handlers مربوط به دکترها"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.doctor_manager = DoctorManager(db_manager)
        # API client را در هر متد جداگانه ایجاد می‌کنیم
    
    # ==================== Add Doctor Conversation ====================
    
    async def start_add_doctor(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شروع فرآیند اضافه کردن دکتر"""
        try:
            user_id = update.effective_user.id
            
            # بررسی دسترسی ادمین (اختیاری - فعلاً همه می‌توانند اضافه کنند)
            # if not await self._is_admin(user_id):
            #     await update.message.reply_text("❌ فقط ادمین‌ها می‌توانند دکتر اضافه کنند.")
            #     return ConversationHandler.END
            
            text = """
🆕 **اضافه کردن دکتر جدید**

لطفاً لینک صفحه دکتر در پذیرش۲۴ را ارسال کنید.

📋 **فرمت‌های قابل قبول:**

1️⃣ **لینک کامل:**
`https://www.paziresh24.com/dr/دکتر-نام-خانوادگی-0/`

2️⃣ **لینک کوتاه:**
`dr/دکتر-نام-خانوادگی-0/`

3️⃣ **فقط slug:**
`دکتر-نام-خانوادگی-0`

💡 **نکته:** ربات تمام اطلاعات مورد نیاز را از صفحه دکتر استخراج می‌کند.

🔄 **برای لغو:** /cancel
            """
            
            keyboard = [
                [InlineKeyboardButton("❌ لغو", callback_data="cancel_add_doctor")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            return ADD_DOCTOR_URL
            
        except Exception as e:
            logger.error(f"❌ خطا در شروع اضافه کردن دکتر: {e}")
            await update.message.reply_text(f"❌ خطا: {str(e)}")
            return ConversationHandler.END
    
    async def receive_doctor_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دریافت URL دکتر و پردازش"""
        try:
            url = update.message.text.strip()
            user_id = update.effective_user.id
            
            # ارسال پیام در حال پردازش
            processing_message = await update.message.reply_text(
                "🔄 **در حال پردازش...**\n\n"
                "⏳ دریافت اطلاعات دکتر از پذیرش۲۴\n"
                "📊 استخراج اطلاعات API\n"
                "💾 ذخیره در دیتابیس\n\n"
                "لطفاً صبر کنید...",
                parse_mode='Markdown'
            )
            
            # اعتبارسنجی URL
            is_valid, validation_message = self.doctor_manager.validate_doctor_url(url)
            if not is_valid:
                await processing_message.edit_text(
                    f"❌ **URL نامعتبر**\n\n{validation_message}\n\n"
                    "لطفاً URL معتبری ارسال کنید یا /cancel کنید.",
                    parse_mode='Markdown'
                )
                return ADD_DOCTOR_URL
            
            # اضافه کردن دکتر
            success, message, doctor = await self.doctor_manager.add_doctor_from_url(url, user_id)
            
            if success:
                # موفقیت
                keyboard = [
                    [InlineKeyboardButton("👨‍⚕️ مشاهده دکتر", callback_data=f"doctor_info_{doctor.id}")],
                    [InlineKeyboardButton("📝 اشتراک در این دکتر", callback_data=f"subscribe_{doctor.id}")],
                    [InlineKeyboardButton("🔍 دریافت نوبت‌های خالی", callback_data=f"check_appointments_{doctor.id}")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await processing_message.edit_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
                logger.info(f"✅ دکتر جدید اضافه شد: {doctor.name} توسط {update.effective_user.first_name}")
                
            else:
                # خطا
                keyboard = [
                    [InlineKeyboardButton("🔄 تلاش مجدد", callback_data="add_doctor")],
                    [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await processing_message.edit_text(
                    f"❌ **خطا در اضافه کردن دکتر**\n\n{message}",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"❌ خطا در پردازش URL دکتر: {e}")
            await update.message.reply_text(
                f"❌ **خطا در پردازش**\n\n`{str(e)}`\n\n"
                "لطفاً دوباره تلاش کنید یا /cancel کنید.",
                parse_mode='Markdown'
            )
            return ADD_DOCTOR_URL
    
    async def cancel_add_doctor(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لغو فرآیند اضافه کردن دکتر"""
        try:
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    "❌ **اضافه کردن دکتر لغو شد**\n\n"
                    "می‌توانید از منوی اصلی استفاده کنید.",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
            else:
                await update.message.reply_text(
                    "❌ **اضافه کردن دکتر لغو شد**",
                    parse_mode='Markdown'
                )
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"❌ خطا در لغو اضافه کردن دکتر: {e}")
            return ConversationHandler.END
    
    # ==================== Doctor Info & Management ====================
    
    async def show_doctor_detailed_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش اطلاعات تفصیلی دکتر"""
        try:
            query = update.callback_query
            await query.answer()
            
            doctor_id = int(query.data.split("_")[-1])
            user_id = query.from_user.id
            
            # دریافت دکتر با جزئیات
            doctor = await self.doctor_manager.get_doctor_with_details(doctor_id)
            if not doctor:
                await query.edit_message_text("❌ دکتر یافت نشد.")
                return
            
            # بررسی اشتراک کاربر
            async with self.db_manager.session_scope() as session:
                user_result = await session.execute(
                    select(User).filter(User.telegram_id == user_id)
                )
                user = user_result.scalar_one_or_none()
                
                is_subscribed = False
                if user:
                    sub_result = await session.execute(
                        select(Subscription).filter(
                            Subscription.user_id == user.id,
                            Subscription.doctor_id == doctor.id,
                            Subscription.is_active == True
                        )
                    )
                    is_subscribed = sub_result.scalar_one_or_none() is not None
            
            # ساخت متن اطلاعات
            specialty_emoji = self._get_specialty_emoji(doctor.specialty)
            
            text = f"""
{specialty_emoji} **{doctor.name}**

🏥 **تخصص:** {doctor.specialty or 'عمومی'}
🆔 **شناسه:** `{doctor.doctor_id}`

🏢 **مراکز درمانی ({len(doctor.centers)} مرکز):**
            """
            
            total_services = 0
            for i, center in enumerate(doctor.centers, 1):
                text += f"\n**{i}. {center.center_name}**\n"
                text += f"   📍 {center.center_address or 'آدرس نامشخص'}\n"
                text += f"   📞 {center.center_phone or 'تلفن نامشخص'}\n"
                text += f"   🏷️ {getattr(center, 'center_type', 'نوع نامشخص')}\n"
                
                if center.services:
                    text += f"   🔧 **سرویس‌ها ({len(center.services)}):**\n"
                    for service in center.services:
                        price_text = f"{service.price:,} تومان" if service.price > 0 else "رایگان"
                        text += f"      • {service.service_name} - {price_text}\n"
                        total_services += 1
                else:
                    text += "   ⚠️ سرویسی موجود نیست\n"
            
            text += f"""

📊 **آمار:**
• مراکز فعال: {len([c for c in doctor.centers if c.is_active])}
• کل سرویس‌ها: {total_services}
• مشترکین: {getattr(doctor, 'subscription_count', 0)}

🔗 **لینک صفحه:**
https://www.paziresh24.com/dr/{doctor.slug}/

📅 **تاریخ اضافه شدن:** {doctor.created_at.strftime('%Y/%m/%d') if doctor.created_at else 'نامشخص'}

🔔 **وضعیت اشتراک:**
{'✅ شما مشترک هستید' if is_subscribed else '❌ شما مشترک نیستید'}
            """
            
            # ساخت keyboard
            keyboard = []
            
            # دکمه‌های اصلی
            if is_subscribed:
                keyboard.append([
                    InlineKeyboardButton("🗑️ لغو اشتراک", callback_data=f"unsubscribe_{doctor.id}")
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton("📝 اشتراک در این دکتر", callback_data=f"subscribe_{doctor.id}")
                ])
            
            keyboard.append([
                InlineKeyboardButton("🔍 بررسی نوبت‌های خالی", callback_data=f"check_appointments_{doctor.id}")
            ])
            
            # دکمه‌های مدیریت (برای ادمین‌ها)
            # if await self._is_admin(user_id):
            keyboard.append([
                InlineKeyboardButton("🔄 به‌روزرسانی اطلاعات", callback_data=f"refresh_doctor_{doctor.id}"),
                InlineKeyboardButton("❌ حذف دکتر", callback_data=f"delete_doctor_{doctor.id}")
            ])
            
            keyboard.extend([
                [InlineKeyboardButton("🔙 لیست دکترها", callback_data="show_doctors")],
                [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")]
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ خطا در نمایش اطلاعات دکتر: {e}")
            await query.edit_message_text(f"❌ خطا: {str(e)}")
    
    async def check_doctor_appointments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بررسی نوبت‌های خالی دکتر"""
        try:
            query = update.callback_query
            await query.answer()
            
            doctor_id = int(query.data.split("_")[-1])
            
            # ارسال پیام در حال بررسی
            await query.edit_message_text(
                "🔍 **در حال بررسی نوبت‌های خالی...**\n\n"
                "⏳ اتصال به API پذیرش۲۴\n"
                "📅 بررسی روزهای موجود\n"
                "🕐 دریافت نوبت‌های خالی\n\n"
                "لطفاً صبر کنید...",
                parse_mode='Markdown'
            )
            
            # دریافت دکتر
            doctor = await self.doctor_manager.get_doctor_with_details(doctor_id)
            if not doctor:
                await query.edit_message_text("❌ دکتر یافت نشد.")
                return
            
            # بررسی نوبت‌ها با ایجاد API client جدید
            api_client = EnhancedPazireshAPI(doctor)
            appointments = await api_client.get_all_available_appointments(days_ahead=7)
            
            if not appointments:
                text = f"""
❌ **نوبت خالی یافت نشد**

👨‍⚕️ **دکتر:** {doctor.name}
📅 **بررسی شده:** 7 روز آینده
🕐 **زمان بررسی:** {datetime.now().strftime('%H:%M:%S')}

💡 **توصیه:** 
• در این دکتر مشترک شوید تا به محض پیدا شدن نوبت اطلاع‌رسانی شوید
• نوبت‌ها معمولاً سریع تمام می‌شوند

🔄 **برای بررسی مجدد:** دکمه زیر را بزنید
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 بررسی مجدد", callback_data=f"check_appointments_{doctor.id}")],
                    [InlineKeyboardButton("📝 اشتراک در این دکتر", callback_data=f"subscribe_{doctor.id}")],
                    [InlineKeyboardButton("🔙 اطلاعات دکتر", callback_data=f"doctor_info_{doctor.id}")]
                ]
            else:
                # گروه‌بندی نوبت‌ها بر اساس مرکز و تاریخ
                grouped_appointments = {}
                for apt in appointments:
                    key = f"{getattr(apt, 'center_name', 'نامشخص')}_{getattr(apt, 'service_name', 'ویزیت')}"
                    if key not in grouped_appointments:
                        grouped_appointments[key] = []
                    grouped_appointments[key].append(apt)
                
                text = f"""
✅ **{len(appointments)} نوبت خالی پیدا شد!**

👨‍⚕️ **دکتر:** {doctor.name}
🕐 **زمان بررسی:** {datetime.now().strftime('%H:%M:%S')}

📋 **نوبت‌های موجود:**
                """
                
                for key, apts in grouped_appointments.items():
                    center_name, service_name = key.split('_', 1)
                    text += f"\n🏢 **{center_name}** - {service_name}\n"
                    
                    # گروه‌بندی بر اساس تاریخ
                    dates = {}
                    for apt in apts:
                        date_str = apt.start_datetime.strftime('%Y/%m/%d')
                        if date_str not in dates:
                            dates[date_str] = []
                        dates[date_str].append(apt)
                    
                    for date_str, date_apts in dates.items():
                        text += f"  📅 {date_str}: "
                        times = []
                        for apt in date_apts:
                            time_str = apt.start_datetime.strftime('%H:%M')
                            times.append(time_str)
                        text += ", ".join(times) + "\n"
                
                text += f"""

🚀 **برای رزرو:**
• روی "رزرو سریع" کلیک کنید
• یا از لینک مستقیم استفاده کنید

⚠️ **توجه:** نوبت‌ها سریع تمام می‌شوند!
                """
                
                keyboard = [
                    [InlineKeyboardButton("🚀 رزرو سریع", callback_data=f"quick_reserve_{doctor.id}")],
                    [InlineKeyboardButton("🔗 لینک رزرو", url=f"https://www.paziresh24.com/dr/{doctor.slug}/")],
                    [InlineKeyboardButton("🔄 بررسی مجدد", callback_data=f"check_appointments_{doctor.id}")],
                    [InlineKeyboardButton("🔙 اطلاعات دکتر", callback_data=f"doctor_info_{doctor.id}")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ خطا در بررسی نوبت‌ها: {e}")
            await query.edit_message_text(
                f"❌ **خطا در بررسی نوبت‌ها**\n\n`{str(e)}`",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 اطلاعات دکتر", callback_data=f"doctor_info_{doctor_id}")
                ]])
            )
    
    async def quick_reserve_placeholder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پلیس‌هولدر برای رزرو سریع (پیاده‌سازی آینده)"""
        try:
            query = update.callback_query
            await query.answer()
            
            doctor_id = int(query.data.split("_")[-1])
            
            text = """
🚧 **قابلیت رزرو سریع**

این قابلیت در حال توسعه است و به زودی اضافه خواهد شد.

🔗 **فعلاً می‌توانید:**
• از لینک رزرو استفاده کنید
• به صورت دستی نوبت رزرو کنید

💡 **قابلیت‌های آینده:**
• رزرو خودکار نوبت‌ها
• انتخاب نوبت مورد نظر
• تایید و پرداخت
            """
            
            keyboard = [
                [InlineKeyboardButton("🔗 رزرو دستی", url=f"https://www.paziresh24.com/dr/{doctor_id}/")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data=f"check_appointments_{doctor_id}")]
            ]
            
            await query.edit_message_text(
                text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            logger.error(f"❌ خطا در رزرو سریع: {e}")
    
    # ==================== Utility Methods ====================
    
    def _get_specialty_emoji(self, specialty):
        """دریافت ایموجی مناسب برای تخصص"""
        if not specialty:
            return "👨‍⚕️"
        
        specialty_lower = specialty.lower()
        
        emoji_map = {
            "قلب": "❤️", "کاردیولوژی": "❤️",
            "مغز": "🧠", "نورولوژی": "🧠",
            "چشم": "👁️", "افتالمولوژی": "👁️",
            "دندان": "🦷",
            "کودکان": "👶", "اطفال": "👶",
            "زنان": "👩", "زایمان": "👩",
            "ارتوپدی": "🦴", "استخوان": "🦴",
            "پوست": "🧴", "درمتولوژی": "🧴",
            "گوش": "👂", "حلق": "👂",
            "تصویربرداری": "📷", "رادیولوژی": "📷"
        }
        
        for keyword, emoji in emoji_map.items():
            if keyword in specialty_lower:
                return emoji
        
        return "👨‍���️"
    
    async def _is_admin(self, user_id: int) -> bool:
        """بررسی دسترسی ادمین"""
        try:
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(User).filter(
                        User.telegram_id == user_id,
                        User.is_admin == True
                    )
                )
                return result.scalar_one_or_none() is not None
        except:
            return False