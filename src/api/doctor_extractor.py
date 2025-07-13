"""
سرویس استخراج اطلاعات دکتر از لینک پذیرش24
"""
import httpx
import json
import re
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, unquote
from datetime import datetime
import time
import random

logger = logging.getLogger(__name__)


class DoctorExtractor:
    """کلاس استخراج اطلاعات دکتر از صفحه پذیرش24"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.base_url = "https://www.paziresh24.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'fa-IR,fa;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
    
    def normalize_doctor_url(self, url: str) -> str:
        """نرمال‌سازی URL دکتر"""
        try:
            # حذف فضاهای خالی
            url = url.strip()
            
            # اگر فقط slug است
            if url.startswith('dr/') or url.startswith('/dr/'):
                url = url.lstrip('/')
                return f"{self.base_url}/{url}"
            
            # اگر URL کامل است
            if url.startswith('http'):
                parsed = urlparse(url)
                if 'paziresh24.com' in parsed.netloc:
                    return url
                else:
                    raise ValueError("URL باید از دامنه paziresh24.com باشد")
            
            # اگر فقط slug بدون dr/ است
            if not url.startswith('dr/'):
                url = f"dr/{url}"
            
            return f"{self.base_url}/{url}"
            
        except Exception as e:
            logger.error(f"❌ خطا در نرمال‌سازی URL: {e}")
            raise ValueError(f"URL نامعتبر: {url}")
    
    def extract_slug_from_url(self, url: str) -> str:
        """استخراج slug از URL"""
        try:
            normalized_url = self.normalize_doctor_url(url)
            parsed = urlparse(normalized_url)
            path = parsed.path
            
            # استخراج slug از path
            # مثال: /dr/دکتر-سیدمحمدمجتبی-موسوی-0/
            if '/dr/' in path:
                slug_part = path.split('/dr/')[-1].rstrip('/')
                # URL decode کردن
                slug = unquote(slug_part)
                return slug
            else:
                raise ValueError("URL شامل /dr/ نیست")
                
        except Exception as e:
            logger.error(f"❌ خطا در استخراج slug: {e}")
            raise ValueError(f"نمی‌توان slug را از URL استخراج کرد: {url}")
    
    async def fetch_doctor_page(self, url: str) -> str:
        """دریافت محتوای صفحه دکتر"""
        try:
            normalized_url = self.normalize_doctor_url(url)
            logger.info(f"🔍 دریافت صفحه: {normalized_url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(normalized_url, headers=self.headers)
                response.raise_for_status()
                
                if response.status_code != 200:
                    raise ValueError(f"خطا در دریافت صفحه: {response.status_code}")
                
                content = response.text
                
                # بررسی وجود __NEXT_DATA__
                if '__NEXT_DATA__' not in content:
                    raise ValueError("صفحه دکتر معتبر نیست - __NEXT_DATA__ یافت نشد")
                
                logger.info(f"✅ صفحه با موفقیت دریافت شد ({len(content)} کاراکتر)")
                return content
                
        except httpx.TimeoutException:
            raise ValueError("زمان انتظار برای دریافت صفحه تمام شد")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError("صفحه دکتر یافت نشد (404)")
            else:
                raise ValueError(f"خطا در دریافت صفحه: {e.response.status_code}")
        except Exception as e:
            logger.error(f"❌ خطا در دریافت صفحه: {e}")
            raise ValueError(f"خطا در دریافت صفحه: {str(e)}")
    
    def extract_next_data(self, html_content: str) -> Dict:
        """استخراج __NEXT_DATA__ از HTML"""
        try:
            # پیدا کردن script tag حاوی __NEXT_DATA__
            pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                raise ValueError("__NEXT_DATA__ در صفحه یافت نشد")
            
            json_str = match.group(1)
            
            # Parse کردن JSON
            next_data = json.loads(json_str)
            
            logger.info("✅ __NEXT_DATA__ با موفقیت استخراج شد")
            return next_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ خطا در parse کردن JSON: {e}")
            raise ValueError("خطا در parse کردن اطلاعات صفحه")
        except Exception as e:
            logger.error(f"❌ خطا در استخراج __NEXT_DATA__: {e}")
            raise ValueError(f"خطا در استخراج اطلاعات: {str(e)}")
    
    def parse_doctor_data(self, next_data: Dict) -> Dict:
        """تجزیه اطلاعات دکتر از __NEXT_DATA__"""
        try:
            page_props = next_data.get('props', {}).get('pageProps', {})
            
            # اطلاعات اصلی دکتر
            information = page_props.get('information', {})
            centers_data = page_props.get('centers', [])
            expertises = page_props.get('expertises', {})
            
            if not information:
                raise ValueError("اطلاعات دکتر در صفحه یافت نشد")
            
            # استخراج اطلاعات اصلی
            doctor_info = {
                'doctor_id': information.get('id'),
                'name': information.get('display_name') or f"{information.get('name', '')} {information.get('family', '')}".strip(),
                'first_name': information.get('name'),
                'last_name': information.get('family'),
                'provider_id': information.get('provider_id'),
                'user_id': information.get('user_id'),
                'server_id': information.get('server_id', 1),
                'biography': information.get('biography', ''),
                'image_url': information.get('image', ''),
                'slug': page_props.get('slug', ''),
                'specialty': self._extract_specialty(expertises),
                'centers': []
            }
            
            # استخراج اطلاعات مراکز
            for center_data in centers_data:
                center_info = {
                    'center_id': center_data.get('id'),
                    'center_name': center_data.get('name'),
                    'center_type': center_data.get('center_type_name'),
                    'center_address': center_data.get('address'),
                    'center_phone': center_data.get('tell'),
                    'user_center_id': center_data.get('user_center_id'),
                    'services': []
                }
                
                # استخراج سرویس‌ها
                for service_data in center_data.get('services', []):
                    service_info = {
                        'service_id': service_data.get('id'),
                        'service_name': service_data.get('alias_title', 'ویزیت'),
                        'user_center_id': service_data.get('user_center_id'),
                        'price': service_data.get('free_price', 0),
                        'duration': service_data.get('duration', ''),
                    }
                    center_info['services'].append(service_info)
                
                doctor_info['centers'].append(center_info)
            
            # اعتبارسنجی
            if not doctor_info['doctor_id']:
                raise ValueError("شناسه دکتر یافت نشد")
            
            if not doctor_info['name']:
                raise ValueError("نام دکتر یافت نشد")
            
            if not doctor_info['centers']:
                raise ValueError("هیچ مرکز درمانی برای این دکتر یافت نشد")
            
            # بررسی وجود سرویس در هر مرکز
            for center in doctor_info['centers']:
                if not center['services']:
                    logger.warning(f"⚠️ مرکز {center['center_name']} هیچ سرویسی ندارد")
            
            logger.info(f"✅ اطلاعات دکتر {doctor_info['name']} با {len(doctor_info['centers'])} مرکز استخراج شد")
            return doctor_info
            
        except Exception as e:
            logger.error(f"❌ خطا در تجزیه اطلاعات دکتر: {e}")
            raise ValueError(f"خطا در تجزیه اطلاعات دکتر: {str(e)}")
    
    def _extract_specialty(self, expertises: Dict) -> str:
        """استخراج تخصص دکتر"""
        try:
            # استخراج از expertises
            expertises_list = expertises.get('expertises', [])
            if expertises_list:
                # ترکیب تمام تخصص‌ها
                specialties = []
                for exp in expertises_list:
                    alias_title = exp.get('alias_title', '')
                    if alias_title:
                        specialties.append(alias_title)
                
                if specialties:
                    return ', '.join(specialties)
            
            # استخراج از group_expertises
            group_expertises = expertises.get('group_expertises', [])
            if group_expertises:
                group_names = [group.get('name', '') for group in group_expertises if group.get('name')]
                if group_names:
                    return ', '.join(group_names)
            
            return 'عمومی'
            
        except Exception as e:
            logger.warning(f"⚠️ خطا در استخراج تخصص: {e}")
            return 'عمومی'
    
    def generate_terminal_id(self) -> str:
        """تولید terminal_id"""
        try:
            # الگوی terminal_id: clinic-{timestamp}.{random}
            timestamp = str(int(time.time() * 1000))[-12:]  # 12 رقم آخر timestamp
            random_part = str(random.randint(10000000, 99999999))  # 8 رقم تصادفی
            
            terminal_id = f"clinic-{timestamp}.{random_part}"
            logger.debug(f"🔧 terminal_id تولید شد: {terminal_id}")
            return terminal_id
            
        except Exception as e:
            logger.error(f"❌ خطا در تولید terminal_id: {e}")
            # fallback
            return f"clinic-{int(time.time())}.{random.randint(10000000, 99999999)}"
    
    async def extract_doctor_from_url(self, url: str) -> Dict:
        """استخراج کامل اطلاعات دکتر از URL"""
        try:
            logger.info(f"🚀 شروع استخراج اطلاعات دکتر از: {url}")
            
            # 1. نرمال‌سازی URL و استخراج slug
            normalized_url = self.normalize_doctor_url(url)
            slug = self.extract_slug_from_url(url)
            
            # 2. دریافت محتوای صفحه
            html_content = await self.fetch_doctor_page(normalized_url)
            
            # 3. استخراج __NEXT_DATA__
            next_data = self.extract_next_data(html_content)
            
            # 4. تجزیه اطلاعات دکتر
            doctor_data = self.parse_doctor_data(next_data)
            
            # 5. اضافه کردن اطلاعات اضافی
            doctor_data['original_url'] = normalized_url
            doctor_data['extracted_slug'] = slug
            doctor_data['terminal_id'] = self.generate_terminal_id()
            doctor_data['extraction_time'] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ استخراج کامل شد: {doctor_data['name']} ({len(doctor_data['centers'])} مرکز)")
            return doctor_data
            
        except Exception as e:
            logger.error(f"❌ خطا در استخراج اطلاعات دکتر: {e}")
            raise ValueError(f"خطا در استخراج اطلاعات دکتر: {str(e)}")


# تست سریع
async def test_extractor():
    """تست سریع extractor"""
    extractor = DoctorExtractor()
    
    test_urls = [
        "dr/دکتر-سیدمحمدمجتبی-موسوی-0/",
        "https://www.paziresh24.com/dr/%D8%AF%DA%A9%D8%AA%D8%B1-%D8%B3%DB%8C%D8%AF%D9%85%D8%AD%D9%85%D8%AF%D9%85%D8%AC%D8%AA%D8%A8%DB%8C-%D9%85%D9%88%D8%B3%D9%88%DB%8C-0/"
    ]
    
    for url in test_urls:
        try:
            print(f"\n🔍 تست URL: {url}")
            result = await extractor.extract_doctor_from_url(url)
            print(f"✅ نام: {result['name']}")
            print(f"✅ تخصص: {result['specialty']}")
            print(f"✅ تعداد مراکز: {len(result['centers'])}")
            for center in result['centers']:
                print(f"  - {center['center_name']} ({len(center['services'])} سرویس)")
        except Exception as e:
            print(f"❌ خطا: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_extractor())