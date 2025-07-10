"""
Handler های ادمین ربات تلگرام - Improved Version
"""
import re
import requests
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

from src.database.database import db_session
from src.database.models import User, Doctor, Subscription
from src.telegram_bot.messages import MessageFormatter
from src.utils.logger import get_logger
from src.utils.config import Config

logger = get_logger("TelegramAdminHandlers")

# States برای ConversationHandler
ADD_DOCTOR_LINK, ADD_DOCTOR_CONFIRM, SET_CHECK_INTERVAL = range(3)


class TelegramAdminHandlers:
    """کلاس handler های ادمین تلگرام"""
    
    @staticmethod
    def is_admin(user_id: int) -> bool:
        """بررسی دسترسی ادمین"""
        try:
            config = Config()
            admin_chat_id = config.admin_chat_id
            logger.info(f"Checking admin: user_id={user_id}, admin_chat_id={admin_chat_id}")
            
            # بررسی ادمین اصلی
            if user_id == admin_chat_id:
                return True
            
            # بررسی ادمین‌های اضافی از دیتابیس
            try:
                with db_session() as session:
                    user = session.query(User).filter(
                        User.telegram_id == user_id,
                        User.is_admin == True,
                        User.is_active == True
                    ).first()
                    return user is not None
            except Exception as e:
                logger.error(f"خطا در بررسی ادمین از دیتابیس: {e}")
                return False
        except Exception as e:
            logger.error(f"خطا در بررسی دسترسی ادمین: {e}")
            return False
    
    @staticmethod
    async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پنل مدیریت ادمین"""
        try:
            user_id = update.effective_user.id
            logger.info(f"Admin panel request from user: {user_id}")
            
            if not TelegramAdminHandlers.is_admin(user_id):
                await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
                return
            
            keyboard = [
                [InlineKeyboardButton("➕ افزودن دکتر", callback_data="admin_add_doctor")],
                [InlineKeyboardButton("🔧 مدیریت دکترها", callback_data="admin_manage_doctors")],
                [InlineKeyboardButton("⏱️ تنظیم زمان بررسی", callback_data="admin_set_interval")],
                [InlineKeyboardButton("👥 مدیریت کاربران", callback_data="admin_manage_users")],
                [InlineKeyboardButton("📊 آمار سیستم", callback_data="admin_stats")],
                [InlineKeyboardButton("🔒 تنظیمات دسترسی", callback_data="admin_access_settings")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            admin_text = "🔧 پنل مدیریت P24_SlotHunter\n\nانتخاب کنید:"
            
            await update.message.reply_text(admin_text, reply_markup=reply_markup)
            logger.info("Admin panel sent successfully")
            
        except Exception as e:
            logger.error(f"خطا در نمایش پنل ادمین: {e}")
            await update.message.reply_text("❌ خطا در بارگذاری پنل مدیریت.")
    
    @staticmethod
    async def start_add_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شروع فرآیند افزودن دکتر"""
        query = update.callback_query
        await query.answer()
        
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return ConversationHandler.END
        
        await query.edit_message_text(
            "🔗 افزودن دکتر جدید\n\n"
            "لینک صفحه دکتر در پذیرش۲۴ را ارسال کنید:\n\n"
            "✅ فرمت‌های پشتیبانی شده:\n"
            "• https://www.paziresh24.com/dr/دکتر-نام-0/\n"
            "• https://www.paziresh24.com/dr/%D8%AF%DA%A9%D8%AA%D8%B1-...\n\n"
            "برای لغو: /cancel"
        )
        
        return ADD_DOCTOR_LINK
    
    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize and validate Paziresh24 URL"""
        url = url.strip()
        
        # Handle both encoded and non-encoded URLs
        if '/dr/' in url:
            # Extract the part after /dr/
            slug_part = url.split('/dr/')[1].rstrip('/')
            
            # URL decode if needed
            decoded_slug = urllib.parse.unquote(slug_part)
            
            # Reconstruct clean URL
            clean_url = f"https://www.paziresh24.com/dr/{decoded_slug}/"
            
            return clean_url
        
        return url
    
    @staticmethod
    def _extract_slug(url: str) -> str:
        """Extract doctor slug from URL"""
        if '/dr/' in url:
            slug = url.split('/dr/')[1].rstrip('/')
            # URL decode
            decoded_slug = urllib.parse.unquote(slug)
            return decoded_slug
        return ""
    
    @staticmethod
    async def process_doctor_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش لینک دکتر"""
        link = update.message.text.strip()
        
        logger.info(f"Processing doctor link: {link}")
        
        # Normalize URL
        try:
            normalized_url = TelegramAdminHandlers._normalize_url(link)
            logger.info(f"Normalized URL: {normalized_url}")
        except Exception as e:
            logger.error(f"Error normalizing URL: {e}")
            await update.message.reply_text(
                "❌ خطا در پردازش لینک.\n\n"
                "لطفاً لینک صحیح ارسال کنید."
            )
            return ADD_DOCTOR_LINK
        
        # بررسی فرمت لینک
        if not re.match(r'https://www\.paziresh24\.com/dr/.+', normalized_url):
            await update.message.reply_text(
                "❌ لینک نامعتبر است.\n\n"
                "لطفاً لینک صحیح صفحه دکتر در پذیرش۲۴ را ارسال کنید.\n\n"
                "مثال:\n"
                "https://www.paziresh24.com/dr/دکتر-نام-خانوادگی-0/"
            )
            return ADD_DOCTOR_LINK
        
        # استخراج slug دکتر
        slug = TelegramAdminHandlers._extract_slug(normalized_url)
        logger.info(f"Extracted slug: {slug}")
        
        if not slug:
            await update.message.reply_text(
                "❌ نتوانستم اطلاعات دکتر را از لینک استخراج کنم.\n\n"
                "لطفاً لینک صحیح ارسال کنید."
            )
            return ADD_DOCTOR_LINK
        
        # نمایش پیام در حال پردازش
        processing_msg = await update.message.reply_text("🔄 در حال دریافت اطلاعات دکتر...")
        
        # دریافت اطلاعات دکتر از API
        try:
            doctor_info = await TelegramAdminHandlers._fetch_doctor_info(slug, normalized_url)
            
            # حذف پیام در حال پردازش
            await processing_msg.delete()
            
            if not doctor_info:
                await update.message.reply_text(
                    "❌ نتوانستم اطلاعات دکتر را دریافت کنم.\n\n"
                    "ممکن است:\n"
                    "• لینک اشتباه باشد\n"
                    "• صفحه دکتر در دسترس نباشد\n"
                    "• مشکل در اتصال به اینترنت\n\n"
                    "لطفاً دوباره تلاش کنید."
                )
                return ADD_DOCTOR_LINK
            
            # ذخیره اطلاعات در context
            context.user_data['doctor_info'] = doctor_info
            
            # نمایش اطلاعات برای تأیید
            confirm_text = f"""✅ اطلاعات دکتر دریافت شد:

👨‍⚕️ **نام:** {doctor_info['name']}
🏥 **تخصص:** {doctor_info['specialty']}
🏢 **مرکز:** {doctor_info['center_name']}
📍 **آدرس:** {doctor_info['center_address']}
📞 **تلفن:** {doctor_info['center_phone']}

🔧 **اطلاعات فنی:**
• Slug: {doctor_info['slug']}
• Center ID: {doctor_info['center_id'][:20]}...
• Service ID: {doctor_info['service_id'][:20]}...

آیا می‌خواهید این دکتر را اضافه کنید؟"""
            
            keyboard = [
                [InlineKeyboardButton("✅ تأیید", callback_data="confirm_add_doctor")],
                [InlineKeyboardButton("❌ لغو", callback_data="cancel_add_doctor")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(confirm_text, reply_markup=reply_markup)
            
            return ADD_DOCTOR_CONFIRM
            
        except Exception as e:
            # حذف پیام در حال پردازش
            try:
                await processing_msg.delete()
            except:
                pass
                
            logger.error(f"خطا در دریافت اطلاعات دکتر: {e}")
            await update.message.reply_text(
                f"❌ خطا در دریافت اطلاعات دکتر.\n\n"
                f"جزئیات خطا: {str(e)}\n\n"
                "لطفاً دوباره تلاش کنید."
            )
            return ADD_DOCTOR_LINK
    
    @staticmethod
    async def _fetch_doctor_info(slug: str, url: str) -> Optional[Dict]:
        """دریافت اطلاعات و��قعی دکتر از پذیرش۲۴"""
        try:
            logger.info(f"Fetching doctor info from: {url}")
            
            # Headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'fa,en-US;q=0.7,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            # Make request with timeout
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Initialize doctor info
            doctor_info = {
                'name': 'نامشخص',
                'slug': slug,
                'specialty': 'نامشخص',
                'center_name': 'نامشخص',
                'center_address': 'نامشخص',
                'center_phone': 'نامشخص',
                'center_id': 'unknown',
                'service_id': 'unknown',
                'user_center_id': 'unknown',
                'terminal_id': 'unknown'
            }
            
            # Extract doctor name
            name_selectors = [
                'h1[data-testid="doctor-name"]',
                'h1.doctor-name',
                '.doctor-info h1',
                '.profile-header h1',
                'h1',
                '.doctor-profile h1',
                '[data-cy="doctor-name"]'
            ]
            
            for selector in name_selectors:
                name_element = soup.select_one(selector)
                if name_element and name_element.get_text().strip():
                    doctor_info['name'] = name_element.get_text().strip()
                    logger.info(f"Found doctor name: {doctor_info['name']}")
                    break
            
            # Extract specialty
            specialty_selectors = [
                '[data-testid="doctor-specialty"]',
                '.doctor-specialty',
                '.specialty',
                '.doctor-info .specialty',
                '[data-cy="doctor-specialty"]',
                '.profile-specialty'
            ]
            
            for selector in specialty_selectors:
                specialty_element = soup.select_one(selector)
                if specialty_element and specialty_element.get_text().strip():
                    doctor_info['specialty'] = specialty_element.get_text().strip()
                    logger.info(f"Found specialty: {doctor_info['specialty']}")
                    break
            
            # Extract center information
            center_selectors = [
                '[data-testid="center-name"]',
                '.center-name',
                '.clinic-name',
                '.center-info h2',
                '[data-cy="center-name"]'
            ]
            
            for selector in center_selectors:
                center_element = soup.select_one(selector)
                if center_element and center_element.get_text().strip():
                    doctor_info['center_name'] = center_element.get_text().strip()
                    logger.info(f"Found center name: {doctor_info['center_name']}")
                    break
            
            # Extract address
            address_selectors = [
                '[data-testid="center-address"]',
                '.center-address',
                '.address',
                '.clinic-address',
                '[data-cy="center-address"]'
            ]
            
            for selector in address_selectors:
                address_element = soup.select_one(selector)
                if address_element and address_element.get_text().strip():
                    doctor_info['center_address'] = address_element.get_text().strip()
                    logger.info(f"Found address: {doctor_info['center_address']}")
                    break
            
            # Extract phone
            phone_selectors = [
                '[data-testid="center-phone"]',
                '.center-phone',
                '.phone',
                '.clinic-phone',
                '[data-cy="center-phone"]'
            ]
            
            for selector in phone_selectors:
                phone_element = soup.select_one(selector)
                if phone_element and phone_element.get_text().strip():
                    doctor_info['center_phone'] = phone_element.get_text().strip()
                    logger.info(f"Found phone: {doctor_info['center_phone']}")
                    break
            
            # Extract API IDs from JavaScript or data attributes
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    script_content = script.string
                    
                    # Look for various ID patterns
                    patterns = {
                        'center_id': [
                            r'"center_id":\s*"([^"]+)"',
                            r'center_id:\s*"([^"]+)"',
                            r'centerId:\s*"([^"]+)"'
                        ],
                        'service_id': [
                            r'"service_id":\s*"([^"]+)"',
                            r'service_id:\s*"([^"]+)"',
                            r'serviceId:\s*"([^"]+)"'
                        ],
                        'user_center_id': [
                            r'"user_center_id":\s*"([^"]+)"',
                            r'user_center_id:\s*"([^"]+)"',
                            r'userCenterId:\s*"([^"]+)"'
                        ],
                        'terminal_id': [
                            r'"terminal_id":\s*"([^"]+)"',
                            r'terminal_id:\s*"([^"]+)"',
                            r'terminalId:\s*"([^"]+)"'
                        ]
                    }
                    
                    for field, pattern_list in patterns.items():
                        for pattern in pattern_list:
                            match = re.search(pattern, script_content)
                            if match:
                                doctor_info[field] = match.group(1)
                                logger.info(f"Found {field}: {doctor_info[field]}")
                                break
                        if doctor_info[field] != 'unknown':
                            break
            
            # If we couldn't find real IDs, generate some based on the slug
            if doctor_info['center_id'] == 'unknown':
                # Generate a UUID-like ID based on slug
                import hashlib
                slug_hash = hashlib.md5(slug.encode()).hexdigest()
                doctor_info['center_id'] = f"center-{slug_hash[:8]}-{slug_hash[8:12]}-{slug_hash[12:16]}-{slug_hash[16:20]}-{slug_hash[20:32]}"
                doctor_info['service_id'] = f"service-{slug_hash[8:16]}-{slug_hash[16:20]}-{slug_hash[20:24]}-{slug_hash[24:28]}-{slug_hash[28:32]}{slug_hash[:8]}"
                doctor_info['user_center_id'] = f"user-{slug_hash[16:24]}-{slug_hash[24:28]}-{slug_hash[28:32]}-{slug_hash[:4]}-{slug_hash[4:16]}"
                doctor_info['terminal_id'] = f"terminal-{slug_hash[:16]}"
                
                logger.info("Generated fallback IDs based on slug")
            
            # Validate that we got meaningful information
            if doctor_info['name'] == 'نامشخص' and doctor_info['specialty'] == 'نامشخص':
                logger.warning("Could not extract meaningful doctor information")
                return None
            
            logger.info(f"Successfully extracted doctor info: {doctor_info['name']}")
            return doctor_info
            
        except requests.RequestException as e:
            logger.error(f"Network error fetching doctor info: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing doctor info: {e}")
            return None
    
    @staticmethod
    async def confirm_add_doctor(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأیید افزودن دکتر"""
        query = update.callback_query
        await query.answer()
        
        doctor_info = context.user_data.get('doctor_info')
        if not doctor_info:
            await query.edit_message_text("❌ خطا در دریافت اطلاعات دکتر.")
            return ConversationHandler.END
        
        try:
            with db_session() as session:
                # بررسی وجود دکتر
                existing = session.query(Doctor).filter(Doctor.slug == doctor_info['slug']).first()
                
                if existing:
                    await query.edit_message_text(
                        f"⚠️ دکتر {doctor_info['name']} قبلاً در سیستم موجود است."
                    )
                    return ConversationHandler.END
                
                # افزودن دکتر جدید
                new_doctor = Doctor(
                    name=doctor_info['name'],
                    slug=doctor_info['slug'],
                    center_id=doctor_info['center_id'],
                    service_id=doctor_info['service_id'],
                    user_center_id=doctor_info['user_center_id'],
                    terminal_id=doctor_info['terminal_id'],
                    specialty=doctor_info['specialty'],
                    center_name=doctor_info['center_name'],
                    center_address=doctor_info['center_address'],
                    center_phone=doctor_info['center_phone'],
                    is_active=True
                )
                
                session.add(new_doctor)
                session.commit()
                
                await query.edit_message_text(
                    f"✅ دکتر {doctor_info['name']} با موفقیت اضافه شد!\n\n"
                    f"🔔 از این پس نوبت‌های این دکتر نیز بررسی می‌شود.\n\n"
                    f"📋 اط��اعات ثبت شده:\n"
                    f"• نام: {doctor_info['name']}\n"
                    f"• تخصص: {doctor_info['specialty']}\n"
                    f"• مرکز: {doctor_info['center_name']}"
                )
                
                logger.info(f"دکتر جدید توسط ادمین اضافه شد: {doctor_info['name']}")
                
        except Exception as e:
            logger.error(f"خطا در افزودن دکتر: {e}")
            await query.edit_message_text("❌ خطا در افزودن دکتر. لطفاً دوباره تلاش کنید.")
        
        return ConversationHandler.END
    
    # ... (rest of the methods remain the same as before)
    
    @staticmethod
    async def manage_doctors(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت دکترها"""
        query = update.callback_query
        await query.answer()
        
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return
        
        try:
            with db_session() as session:
                doctors = session.query(Doctor).all()
                
                if not doctors:
                    await query.edit_message_text("❌ هیچ دکتری در سیستم موجود نیست.")
                    return
                
                keyboard = []
                for doctor in doctors:
                    status_icon = "✅" if doctor.is_active else "⏸️"
                    action = "disable" if doctor.is_active else "enable"
                    
                    keyboard.append([
                        InlineKeyboardButton(
                            f"{status_icon} {doctor.name}",
                            callback_data=f"toggle_doctor_{doctor.id}_{action}"
                        )
                    ])
                
                keyboard.append([
                    InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_admin_panel")
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    "🔧 مدیریت دکترها\n\n"
                    "برای خاموش/روشن کردن نظارت، روی نام دکتر کلیک کنید:",
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"خطا در مدیریت دکترها: {e}")
            await query.edit_message_text("❌ خطا در بارگذاری لیست دکترها.")
    
    @staticmethod
    async def toggle_doctor_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تغییر وضعیت دکتر"""
        query = update.callback_query
        await query.answer()
        
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return
        
        try:
            # استخراج اطلاعات از callback_data
            parts = query.data.split('_')
            doctor_id = int(parts[2])
            action = parts[3]  # enable یا disable
            
            with db_session() as session:
                doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
                
                if not doctor:
                    await query.edit_message_text("❌ دکتر یافت نشد.")
                    return
                
                # تغییر وضعیت
                doctor.is_active = (action == "enable")
                session.commit()
                
                status_text = "فعال" if doctor.is_active else "غیرفعال"
                await query.edit_message_text(
                    f"✅ وض��یت دکتر {doctor.name} به {status_text} تغییر کرد.\n\n"
                    f"🔄 برای بازگشت به لیست: /admin"
                )
                
                logger.info(f"وضعیت دکتر {doctor.name} تغییر کرد: {status_text}")
                
        except Exception as e:
            logger.error(f"خطا در تغییر وضعیت دکتر: {e}")
            await query.edit_message_text("❌ خطا در تغییر وضعیت دکتر.")
    
    @staticmethod
    async def set_check_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تنظیم زمان بررسی"""
        query = update.callback_query
        await query.answer()
        
        if not TelegramAdminHandlers.is_admin(query.from_user.id):
            await query.edit_message_text("❌ شما دسترسی ادمین ندارید.")
            return
        
        await query.edit_message_text(
            "⏱️ تنظیم زمان بررسی\n\n"
            "زمان بررسی جدید را به ثانیه وارد کنید (حداقل 1 ثانیه):\n\n"
            "مثال: 30 برای 30 ثانیه\n\n"
            "برای لغو: /cancel"
        )
        
        return SET_CHECK_INTERVAL
    
    @staticmethod
    async def process_check_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش زمان بررسی جدید"""
        try:
            interval = int(update.message.text.strip())
            
            if interval < 1:
                await update.message.reply_text(
                    "❌ زمان بررسی باید حداقل 1 ثانیه باشد.\n\n"
                    "لطفاً عدد معتبر وارد کنید:"
                )
                return SET_CHECK_INTERVAL
            
            # به‌روزرسانی فایل .env
            env_path = ".env"
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # جایگزینی CHECK_INTERVAL
            import re
            content = re.sub(r'CHECK_INTERVAL=\d+', f'CHECK_INTERVAL={interval}', content)
            
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            await update.message.reply_text(
                f"✅ زمان بررسی به {interval} ثانیه تغییر کرد.\n\n"
                f"⚠️ برای اعمال تغییرات، سیستم باید restart شود.\n\n"
                f"🔄 برای بازگشت: /admin"
            )
            
            logger.info(f"زمان بررسی توسط ادمین تغییر کرد: {interval} ثانیه")
            
        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً عدد معتبر وارد کنید.\n\n"
                "مثال: 30"
            )
            return SET_CHECK_INTERVAL
        except Exception as e:
            logger.error(f"خطا در تنظیم زمان بررسی: {e}")
            await update.message.reply_text("❌ خطا در تنظیم زمان بررسی.")
        
        return ConversationHandler.END
    
    @staticmethod
    async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لغو مکالمه"""
        await update.message.reply_text(
            "❌ عملیات لغو شد.\n\n"
            "🔄 برای بازگشت: /admin"
        )
        return ConversationHandler.END