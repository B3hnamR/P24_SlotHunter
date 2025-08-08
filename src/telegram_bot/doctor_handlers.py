"""
Handlers مربوط به مدیریت دکترها (نسخه HTML)
"""
import asyncio
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy import select
from typing import List
from datetime import datetime

from src.database.models import User, Doctor, Subscription
from src.api.doctor_manager import DoctorManager
from src.api.enhanced_paziresh_client import EnhancedPazireshAPI
from src.telegram_bot.messages import MessageFormatter
from src.utils.logger import get_logger

logger = get_logger("DoctorHandlers")

# States برای ConversationHandler
ADD_DOCTOR_URL = 1


class DoctorHandlers:
    """کلاس handlers مربوط به دکترها (HTML)"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.doctor_manager = DoctorManager(db_manager)
        # API client را در هر متد جداگانه ایجاد می‌کنیم
    
    # ==================== Add Doctor Conversation ====================
    
    async def start_add_doctor(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شروع فرآیند اضافه کردن دکتر"""
        try:
            user_id = update.effective_user.id
            
            text = (
                "🆕 <b>اضافه کردن دکتر جدید</b>\n\n"
                "لطفاً لینک صفحه دکتر در پذیرش۲۴ را ارسال کنید.\n\n"
                "📋 <b>فرمت‌های قابل قبول:</b>\n\n"
                "1️⃣ <b>لینک کامل:</b>\n"
                "<code>https://www.paziresh24.com/dr/دکتر-نام-خانوادگی-0/</code>\n\n"
                "2️⃣ <b>لینک کوتاه:</b>\n"
                "<code>dr/دکتر-نام-خانوادگی-0/</code>\n\n"
                "3️⃣ <b>فقط slug:</b>\n"
                "<code>دکتر-نام-خانوادگی-0</code>\n\n"
                "💡 <b>نکته:</b> ربات تمام اطلاعات مورد نیاز را از صفحه دکتر استخراج می‌کند.\n\n"
                "🔄 <b>برای لغو:</b> /cancel"
            )
            
            keyboard = [
                [InlineKeyboardButton("❌ لغو", callback_data="cancel_add_doctor")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
            return ADD_DOCTOR_URL
            
        except Exception as e:
            logger.error(f"❌ خطا در شروع اضافه کردن دکتر: {e}")
            await update.message.reply_text(f"❌ خطا: {html.escape(str(e))}", parse_mode='HTML')
            return ConversationHandler.END
    
    async def receive_doctor_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دریافت URL دکتر و پردازش"""
        try:
            url = update.message.text.strip()
            user_id = update.effective_user.id
            
            # ارسال پیام در حال پردازش
            processing_message = await update.message.reply_text(
                "🔄 <b>در حال پردازش...</b>\n\n"
                "⏳ دریافت اطلاعات دکتر از پذیرش۲۴\n"
                "📊 استخراج اطلاعات API\n"
                "💾 ذخیره در دیتابیس\n\n"
                "لطفاً صبر کنید...",
                parse_mode='HTML'
            )
            
            # اعتبارسنجی URL
            is_valid, validation_message = self.doctor_manager.validate_doctor_url(url)
            if not is_valid:
                await processing_message.edit_text(
                    f"❌ <b>URL نامعتبر</b>\n\n{html.escape(validation_message)}\n\n"
                    "لطفاً URL معتبری ارسال کنید یا /cancel کنید.",
                    parse_mode='HTML'
                )
                return ADD_DOCTOR_URL
            
            # اضافه کردن دکتر
            success, message, doctor = await self.doctor_manager.add_doctor_from_url(url, user_id)
            
            if success:
                # موفقیت: از پیام استاندارد HTML استفاده می‌کنیم
                text = MessageFormatter.doctor_extraction_success_message(doctor.name)
                
                keyboard = [
                    [InlineKeyboardButton("👨‍⚕️ مشاهده دکتر", callback_data=f"doctor_info_{doctor.id}")],
                    [InlineKeyboardButton("📝 اشتراک در این دکتر", callback_data=f"subscribe_{doctor.id}")],
                    [InlineKeyboardButton("🔍 دریافت نوبت‌های خالی", callback_data=f"check_appointments_{doctor.id}")],
                    [InlineKeyboardButton("🔙 منوی اصل��", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await processing_message.edit_text(
                    text,
                    parse_mode='HTML',
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
                    f"❌ <b>خطا در اضافه کردن دکتر</b>\n\n{html.escape(str(message))}",
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"❌ خطا در پردازش URL دکتر: {e}")
            await update.message.reply_text(
                f"❌ <b>خطا در پردازش</b>\n\n<code>{html.escape(str(e))}</code>\n\n"
                "لطفاً دوباره تلاش کنید یا /cancel کنید.",
                parse_mode='HTML'
            )
            return ADD_DOCTOR_URL
    
    async def cancel_add_doctor(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لغو فرآیند اضافه کردن دکتر"""
        try:
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    "❌ <b>اضافه کردن دکتر لغو شد</b>\n\n"
                    "می‌توانید از منوی اصلی استفاده کنید.",
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")
                    ]])
                )
            else:
                await update.message.reply_text(
                    "❌ <b>اضافه کردن دکتر لغو شد</b>",
                    parse_mode='HTML'
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
            
            # ساخت متن اطلاعات (HTML)
            specialty_emoji = self._get_specialty_emoji(doctor.specialty)
            
            # اطلاعات مرکز
            if doctor.centers:
                first_center = doctor.centers[0]
                center_info = (
                    f"\n🏥 <b>مطب/کلینیک:</b> {html.escape(first_center.center_name)}\n"
                    f"📍 <b>آدرس:</b> {html.escape(first_center.center_address or 'آدرس موجود نیست')}\n"
                    f"📞 <b>تلفن:</b> {html.escape(first_center.center_phone or 'شماره موجود نیست')}"
                )
                if len(doctor.centers) > 1:
                    center_info += f"\n🏢 <b>تعداد مراکز:</b> {len(doctor.centers)} مرکز"
            else:
                center_info = "\n🏥 <b>مطب/کلینیک:</b> اطلاعات موجود نیست"
            
            text = (
                f"{specialty_emoji} <b>{html.escape(doctor.name)}</b>\n\n"
                f"🩺 <b>تخصص:</b> {html.escape(doctor.specialty or 'عمومی')}" +
                center_info +
                "\n\n🔗 <b>لینک صفحه دکتر:</b>\n"
                f"https://www.paziresh24.com/dr/{html.escape(doctor.slug)}/\n\n"
                f"📊 <b>وضعیت ثبت‌نام شما:</b>\n"
                f"{'✅ ثبت‌نام کردی' if is_subscribed else '❌ ثبت‌نام نکردی'}\n\n"
                "🤖 <b>چطور کار می‌کنه؟</b>\n"
                "اگه ثبت‌نام کنی، من هر چند دقیقه یه بار نوبت‌های خالی این دکتر رو چک می‌کنم و تا پیدا شد، فوری بهت خبر می‌دم!\n\n"
                "💡 <b>نکته:</b> نوبت‌ها خیلی سریع تموم میشن، پس آماده باش!"
            )
            
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
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ خطا در نمایش اطلاعات دکتر: {e}")
            await query.edit_message_text(f"❌ خطا: {html.escape(str(e))}")
    
    async def check_doctor_appointments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بررسی نوبت‌های خالی دکتر"""
        try:
            query = update.callback_query
            await query.answer()
            
            doctor_id = int(query.data.split("_")[-1])
            
            # ارسال پیام در حال بررسی
            await query.edit_message_text(
                "🔍 <b>در حال بررسی نوبت‌های خالی...</b>\n\n"
                "⏳ اتصال به API پذیرش۲۴\n"
                "📅 بررسی روزهای موجود\n"
                "🕐 دریافت نوبت‌های خالی\n\n"
                "لطفاً صبر کنید...",
                parse_mode='HTML'
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
                text = (
                    "❌ <b>نوبت خالی یافت نشد</b>\n\n"
                    f"👨‍⚕️ <b>دکتر:</b> {html.escape(doctor.name)}\n"
                    "📅 <b>بررسی شده:</b> 7 روز آینده\n"
                    f"🕐 <b>زمان بررسی:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
                    "💡 <b>توصیه:</b> \n"
                    "• در این دکتر مشترک شوید تا به محض پیدا شدن نوبت اطلاع‌رسانی شوید\n"
                    "• نوبت‌ها معمولاً سریع تمام می‌شوند\n\n"
                    "🔄 <b>برای بررسی مجدد:</b> دکمه زیر را بزنید"
                )
                
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
                
                text = (
                    f"✅ <b>{len(appointments)} نوبت خالی پیدا شد!</b>\n\n"
                    f"👨‍⚕️ <b>دکتر:</b> {html.escape(doctor.name)}\n"
                    f"🕐 <b>زمان بررسی:</b> {datetime.now().strftime('%H:%M:%S')}\n\n"
                    "📋 <b>نوبت‌های موجود:</b>\n"
                )
                
                for key, apts in grouped_appointments.items():
                    center_name, service_name = key.split('_', 1)
                    text += f"\n🏢 <b>{html.escape(center_name)}</b> - {html.escape(service_name)}\n"
                    
                    # گروه‌بندی بر اساس تاریخ
                    dates = {}
                    for apt in apts:
                        date_str = apt.start_datetime.strftime('%Y/%m/%d')
                        dates.setdefault(date_str, []).append(apt)
                    
                    for date_str, date_apts in dates.items():
                        text += f"  📅 {html.escape(date_str)}: "
                        times = []
                        for apt in date_apts:
                            time_str = apt.start_datetime.strftime('%H:%M')
                            times.append(time_str)
                        text += html.escape(", ".join(times)) + "\n"
                
                text += (
                    "\n🚀 <b>برای رزرو:</b>\n"
                    "• روی \"رزرو سریع\" کلیک کنید\n"
                    "• یا از لینک مستقیم استفاده کنید\n\n"
                    "⚠️ <b>توجه:</b> نوبت‌ها سریع تمام می‌شوند!"
                )
                
                keyboard = [
                    [InlineKeyboardButton("🚀 رزرو سریع", callback_data=f"quick_reserve_{doctor.id}")],
                    [InlineKeyboardButton("🔗 لینک رزرو", url=f"https://www.paziresh24.com/dr/{doctor.slug}/")],
                    [InlineKeyboardButton("🔄 بررسی مجدد", callback_data=f"check_appointments_{doctor.id}")],
                    [InlineKeyboardButton("🔙 اطلاعات دکتر", callback_data=f"doctor_info_{doctor.id}")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ خطا در بررسی نوبت‌ها: {e}")
            await query.edit_message_text(
                f"❌ <b>خطا در بررسی نوبت‌ها</b>\n\n<code>{html.escape(str(e))}</code>",
                parse_mode='HTML',
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

            # دریافت slug برای لینک صحیح رزرو
            doctor = await self.doctor_manager.get_doctor_with_details(doctor_id)
            slug = doctor.slug if doctor else str(doctor_id)
            
            text = (
                "🚧 <b>قابلیت رزرو سریع</b>\n\n"
                "این قابلیت در حال توسعه است و به زودی اضافه خواهد شد.\n\n"
                "🔗 <b>فعلاً می‌توانید:</b>\n"
                "• از لینک رزرو استفاده کنید\n"
                "• به صورت دستی نوبت رزرو کنید\n\n"
                "💡 <b>قابلیت‌های آینده:</b>\n"
                "• رزرو خودکار نوبت‌ها\n"
                "• انتخاب نوبت مورد نظر\n"
                "• تایید و پرداخت"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔗 رزرو دستی", url=f"https://www.paziresh24.com/dr/{slug}/")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data=f"check_appointments_{doctor_id}")]
            ]
            
            await query.edit_message_text(
                text,
                parse_mode='HTML',
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
        
        return "👨‍⚕️"
    
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
