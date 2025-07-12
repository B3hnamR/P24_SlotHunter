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
        """بررسی دسترسی ادمین - استفاده از سیستم نقش‌های جدید"""
        try:
            from src.telegram_bot.user_roles import user_role_manager
            return user_role_manager.is_admin_or_higher(user_id)
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
        
        # نمایش پیا�� در حال پردازش
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

👨‍⚕️ نام: {doctor_info['name']}
🏥 تخصص: {doctor_info['specialty']}
🏢 مرکز: {doctor_info['center_name']}
📍 آدرس: {doctor_info['center_address']}
📞 تلفن: {doctor_info['center_phone']}

🔧 اطلاعات فنی:
• Slug: {doctor_info['slug']}
• Center ID: {doctor_info['center_id'][:20]}...

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
                f"جزئ��ات خطا: {str(e)}\n\n"
                "لطفاً دوباره تلاش کنید."
            )
            return ADD_DOCTOR_LINK
    
    @staticmethod
    async def _fetch_doctor_info(slug: str, url: str) -> Optional[Dict]:
        """دریافت اطلاعات واقعی دکتر از پذیرش۲۴"""
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
            
            # Extract API IDs from JavaScript or data attributes - Enhanced version
            api_ids_found = TelegramAdminHandlers._extract_api_ids_enhanced(soup, slug)
            doctor_info.update(api_ids_found)
            
            # If we still couldn't find real IDs, try alternative methods
            if doctor_info['center_id'] == 'unknown':
                logger.warning(f"Could not find real API IDs for {slug}")
                
                # Try to extract from network requests or other sources
                alternative_ids = TelegramAdminHandlers._try_alternative_id_extraction(url, slug)
                if alternative_ids:
                    doctor_info.update(alternative_ids)
                    logger.info("Found IDs using alternative method")
                else:
                    # Last resort: generate placeholder IDs with warning
                    doctor_info.update(TelegramAdminHandlers._generate_placeholder_ids(slug))
                    logger.warning("Using placeholder IDs - API functionality may be limited")
            
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
                    f"📋 اطلاعات ثبت شده:\n"
                    f"• نام: {doctor_info['name']}\n"
                    f"• تخصص: {doctor_info['specialty']}\n"
                    f"• مرکز: {doctor_info['center_name']}"
                )
                
                logger.info(f"دکتر جدید توسط ادمین اضافه شد: {doctor_info['name']}")
                
        except Exception as e:
            logger.error(f"خطا در افزودن دکتر: {e}")
            await query.edit_message_text("❌ خطا در افزودن دکتر. لطفاً دوباره تلاش کنید.")
        
        return ConversationHandler.END
    
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
            await query.edit_message_text("❌ خطا در بارگذ��ری لیست دکترها.")
    
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
                    f"✅ وضعیت دکتر {doctor.name} به {status_text} تغییر کرد.\n\n"
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
        """پردازش زمان بررسی جدید - نسخه بهبود یافته با backup و validation"""
        try:
            interval = int(update.message.text.strip())
            
            if interval < 1:
                await update.message.reply_text(
                    "❌ زمان بررسی باید حداقل 1 ثانیه باشد.\n\n"
                    "لطفاً عدد معتبر وارد کنید:"
                )
                return SET_CHECK_INTERVAL
            
            # بهبود یافته: استفاده از safe .env modification
            success = await TelegramAdminHandlers._update_env_variable_safe('CHECK_INTERVAL', str(interval))
            
            if success:
                await update.message.reply_text(
                    f"✅ زمان بررسی به {interval} ثانیه تغییر کرد.\n\n"
                    f"💾 فایل .env با backup به‌روزرسانی شد.\n\n"
                    f"⚠️ برای اعمال تغییرات، سیستم باید restart شود.\n\n"
                    f"🔄 برای بازگشت: /admin"
                )
                
                logger.info(f"زمان بررسی توسط ادمین تغییر کرد: {interval} ثانیه")
            else:
                await update.message.reply_text(
                    "❌ خطا در به‌روزرسانی فایل .env\n\n"
                    "لطفاً دوباره تلاش کنید یا با ادمین سیست�� تماس بگیرید."
                )
            
        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً عدد معتبر وارد کنید.\n\n"
                "مثال: 30"
            )
            return SET_CHECK_INTERVAL
        except Exception as e:
            logger.error(f"خطا در تنظیم زمان بررسی: {e}")
            await update.message.reply_text(
                f"❌ خطا در تنظیم زمان بررسی.\n\n"
                f"جزئیات: {str(e)}"
            )
        
        return ConversationHandler.END
    
    @staticmethod
    def _extract_api_ids_enhanced(soup: BeautifulSoup, slug: str) -> Dict[str, str]:
        """استخراج پیشرفته ID های API از HTML"""
        api_ids = {
            'center_id': 'unknown',
            'service_id': 'unknown', 
            'user_center_id': 'unknown',
            'terminal_id': 'unknown'
        }
        
        try:
            # Method 1: Extract from JavaScript variables
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    script_content = script.string
                    
                    # Enhanced patterns for different naming conventions
                    patterns = {
                        'center_id': [
                            r'"center_id":\s*"([^"]+)"',
                            r'center_id:\s*"([^"]+)"',
                            r'centerId:\s*"([^"]+)"',
                            r'"centerId":\s*"([^"]+)"',
                            r'center-id["\']:\s*["\']([^"\']+)["\']',
                            r'data-center-id["\']:\s*["\']([^"\']+)["\']'
                        ],
                        'service_id': [
                            r'"service_id":\s*"([^"]+)"',
                            r'service_id:\s*"([^"]+)"',
                            r'serviceId:\s*"([^"]+)"',
                            r'"serviceId":\s*"([^"]+)"',
                            r'service-id["\']:\s*["\']([^"\']+)["\']'
                        ],
                        'user_center_id': [
                            r'"user_center_id":\s*"([^"]+)"',
                            r'user_center_id:\s*"([^"]+)"',
                            r'userCenterId:\s*"([^"]+)"',
                            r'"userCenterId":\s*"([^"]+)"',
                            r'user-center-id["\']:\s*["\']([^"\']+)["\']'
                        ],
                        'terminal_id': [
                            r'"terminal_id":\s*"([^"]+)"',
                            r'terminal_id:\s*"([^"]+)"',
                            r'terminalId:\s*"([^"]+)"',
                            r'"terminalId":\s*"([^"]+)"',
                            r'terminal-id["\']:\s*["\']([^"\']+)["\']'
                        ]
                    }
                    
                    for field, pattern_list in patterns.items():
                        if api_ids[field] == 'unknown':
                            for pattern in pattern_list:
                                match = re.search(pattern, script_content, re.IGNORECASE)
                                if match:
                                    api_ids[field] = match.group(1)
                                    logger.info(f"Found {field}: {api_ids[field]}")
                                    break
            
            # Method 2: Extract from data attributes
            data_selectors = [
                '[data-center-id]',
                '[data-service-id]', 
                '[data-user-center-id]',
                '[data-terminal-id]',
                '[data-centerId]',
                '[data-serviceId]',
                '[data-userCenterId]',
                '[data-terminalId]'
            ]
            
            for selector in data_selectors:
                elements = soup.select(selector)
                for element in elements:
                    for attr in element.attrs:
                        if 'center-id' in attr.lower() or 'centerid' in attr.lower():
                            if api_ids['center_id'] == 'unknown':
                                api_ids['center_id'] = element.get(attr)
                        elif 'service-id' in attr.lower() or 'serviceid' in attr.lower():
                            if api_ids['service_id'] == 'unknown':
                                api_ids['service_id'] = element.get(attr)
                        elif 'user-center-id' in attr.lower() or 'usercenterid' in attr.lower():
                            if api_ids['user_center_id'] == 'unknown':
                                api_ids['user_center_id'] = element.get(attr)
                        elif 'terminal-id' in attr.lower() or 'terminalid' in attr.lower():
                            if api_ids['terminal_id'] == 'unknown':
                                api_ids['terminal_id'] = element.get(attr)
            
            # Method 3: Extract from form inputs or hidden fields
            form_inputs = soup.find_all(['input', 'select', 'textarea'])
            for input_elem in form_inputs:
                name = input_elem.get('name', '').lower()
                value = input_elem.get('value', '')
                
                if value and len(value) > 5:  # Reasonable ID length
                    if 'center' in name and 'id' in name:
                        if api_ids['center_id'] == 'unknown':
                            api_ids['center_id'] = value
                    elif 'service' in name and 'id' in name:
                        if api_ids['service_id'] == 'unknown':
                            api_ids['service_id'] = value
                    elif 'terminal' in name and 'id' in name:
                        if api_ids['terminal_id'] == 'unknown':
                            api_ids['terminal_id'] = value
            
            return api_ids
            
        except Exception as e:
            logger.error(f"Error in enhanced API ID extraction: {e}")
            return api_ids
    
    @staticmethod
    def _try_alternative_id_extraction(url: str, slug: str) -> Optional[Dict[str, str]]:
        """تلاش برای استخراج ID ها از منابع جایگزین"""
        try:
            # Method 1: Try to find API endpoints in the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': url
            }
            
            # Try common API endpoints
            api_endpoints = [
                f"https://www.paziresh24.com/api/v1/doctors/{slug}",
                f"https://www.paziresh24.com/api/doctors/{slug}",
                f"https://api.paziresh24.com/v1/doctors/{slug}",
                f"https://www.paziresh24.com/api/v1/centers/doctor/{slug}"
            ]
            
            for endpoint in api_endpoints:
                try:
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract IDs from API response
                        api_ids = {}
                        if 'center_id' in data:
                            api_ids['center_id'] = str(data['center_id'])
                        if 'service_id' in data:
                            api_ids['service_id'] = str(data['service_id'])
                        if 'user_center_id' in data:
                            api_ids['user_center_id'] = str(data['user_center_id'])
                        if 'terminal_id' in data:
                            api_ids['terminal_id'] = str(data['terminal_id'])
                        
                        if api_ids:
                            logger.info(f"Found IDs from API endpoint: {endpoint}")
                            return api_ids
                            
                except Exception as e:
                    logger.debug(f"API endpoint {endpoint} failed: {e}")
                    continue
            
            # Method 2: Try to extract from network tab simulation
            # This would require more complex implementation
            
            return None
            
        except Exception as e:
            logger.error(f"Error in alternative ID extraction: {e}")
            return None
    
    @staticmethod
    def _generate_placeholder_ids(slug: str) -> Dict[str, str]:
        """تولید ID های placeholder با هشدار"""
        import hashlib
        import uuid
        
        # Create a more sophisticated hash-based ID generation
        slug_hash = hashlib.sha256(slug.encode()).hexdigest()
        
        # Generate UUID-like IDs but mark them as placeholders
        placeholder_ids = {
            'center_id': f"placeholder-center-{slug_hash[:8]}-{slug_hash[8:12]}-{slug_hash[12:16]}-{slug_hash[16:20]}-{slug_hash[20:32]}",
            'service_id': f"placeholder-service-{slug_hash[8:16]}-{slug_hash[16:20]}-{slug_hash[20:24]}-{slug_hash[24:28]}-{slug_hash[28:32]}{slug_hash[:8]}",
            'user_center_id': f"placeholder-user-{slug_hash[16:24]}-{slug_hash[24:28]}-{slug_hash[28:32]}-{slug_hash[:4]}-{slug_hash[4:16]}",
            'terminal_id': f"placeholder-terminal-{slug_hash[:16]}"
        }
        
        logger.warning(f"Generated placeholder IDs for {slug} - API functionality may be limited")
        logger.warning("Consider manually updating these IDs with real values from Paziresh24")
        
        return placeholder_ids
    
    @staticmethod
    async def _update_env_variable_safe(variable_name: str, new_value: str) -> bool:
        """به‌روزرسانی امن متغیر .env با backup و validation"""
        import os
        import shutil
        from datetime import datetime
        from pathlib import Path
        
        try:
            env_path = Path(".env")
            
            # بررسی وجود فایل .env
            if not env_path.exists():
                logger.error("فایل .env یافت نشد")
                return False
            
            # ایجاد backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path(f".env.backup_{timestamp}")
            
            try:
                shutil.copy2(env_path, backup_path)
                logger.info(f"Backup created: {backup_path}")
            except Exception as e:
                logger.error(f"خطا در ایجاد backup: {e}")
                return False
            
            # خواندن فایل فعلی
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"خطا در خواندن فایل .env: {e}")
                return False
            
            # Validation: بررسی فرمت فایل
            lines = content.split('\n')
            valid_format = True
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and '=' not in line:
                    logger.warning(f"خط نامعتبر در .env: {line}")
                    valid_format = False
            
            if not valid_format:
                logger.error("فرمت فایل .env نامعتبر است")
                return False
            
            # به‌روزرسانی متغیر
            pattern = rf'^{re.escape(variable_name)}=.*
            new_line = f"{variable_name}={new_value}"
            
            # بررسی وجود متغیر
            if re.search(pattern, content, re.MULTILINE):
                # به‌روزرسانی متغیر موجود
                updated_content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
                logger.info(f"Updated existing variable: {variable_name}")
            else:
                # اضافه کردن متغیر جدید
                if content and not content.endswith('\n'):
                    content += '\n'
                updated_content = content + new_line + '\n'
                logger.info(f"Added new variable: {variable_name}")
            
            # Validation: بررسی تغییرات
            if updated_content == content:
                logger.warning("هیچ تغییری اعمال نشد")
                return True
            
            # نوشتن فایل جدید
            try:
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                logger.info(f"Successfully updated {variable_name} in .env")
            except Exception as e:
                logger.error(f"خطا در نوشتن فایل .env: {e}")
                # بازگردانی از backup
                try:
                    shutil.copy2(backup_path, env_path)
                    logger.info("فایل از backup بازگردانی شد")
                except Exception as restore_error:
                    logger.error(f"خطا در بازگردانی backup: {restore_error}")
                return False
            
            # Validation نهایی: بررسی خوانایی فایل جدید
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    test_content = f.read()
                    if variable_name not in test_content:
                        raise ValueError(f"متغیر {variable_name} در فایل جدید یافت نشد")
                logger.info("Validation successful")
            except Exception as e:
                logger.error(f"Validation failed: {e}")
                # بازگردانی از backup
                try:
                    shutil.copy2(backup_path, env_path)
                    logger.info("فایل از backup بازگردانی شد")
                except Exception as restore_error:
                    logger.error(f"خطا در بازگردانی backup: {restore_error}")
                return False
            
            # حذف backup های قدی��ی (نگه داشتن 5 backup اخیر)
            try:
                backup_files = list(Path('.').glob('.env.backup_*'))
                if len(backup_files) > 5:
                    backup_files.sort(key=lambda x: x.stat().st_mtime)
                    for old_backup in backup_files[:-5]:
                        old_backup.unlink()
                        logger.info(f"Removed old backup: {old_backup}")
            except Exception as e:
                logger.warning(f"خطا در حذف backup های قدیمی: {e}")
            
            # بارگذاری مجدد متغیرهای محیطی
            try:
                from dotenv import load_dotenv
                load_dotenv(override=True)
                logger.info("Environment variables reloaded")
            except ImportError:
                logger.warning("python-dotenv not available, manual restart required")
            except Exception as e:
                logger.warning(f"خطا در بارگذاری مجدد متغیرها: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی امن .env: {e}")
            return False
    
    @staticmethod
    async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لغو مکالمه"""
        await update.message.reply_text(
            "❌ عملیات لغو شد.\n\n"
            "🔄 برای بازگشت: /admin"
        )
        return ConversationHandler.END