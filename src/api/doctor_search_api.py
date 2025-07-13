"""
API جستجوی دکتر در پذیرش۲۴
"""
import httpx
import re
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from .models import Doctor


class DoctorSearchAPI:
    """API جستجو و استخراج اطلاعات دکتر"""
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.base_url = "https://www.paziresh24.com"
        self.api_base = "https://apigw.paziresh24.com"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fa,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def search_doctors(self, query: str, city: str = "", specialty: str = "") -> List[Dict]:
        """
        جستجوی دکتر در پذیرش۲۴
        
        Args:
            query: نام دکتر یا کلمه کلیدی
            city: شهر (اختیاری)
            specialty: تخصص (اختیاری)
            
        Returns:
            لیست دکترهای یافت شده
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # ساخت URL جستجو
                search_url = f"{self.base_url}/search"
                params = {
                    'q': query,
                    'city': city,
                    'specialty': specialty
                }
                
                response = await client.get(search_url, params=params, headers=self.headers)
                response.raise_for_status()
                
                # پارس کردن نتایج
                soup = BeautifulSoup(response.text, 'html.parser')
                doctors = self._parse_search_results(soup)
                
                return doctors
                
        except Exception as e:
            print(f"❌ خطا در جستجوی دکتر: {e}")
            return []
    
    async def get_doctor_from_url(self, doctor_url: str) -> Optional[Doctor]:
        """
        استخراج اطلاعات کامل دکتر از URL صفحه
        
        Args:
            doctor_url: لینک صفحه دکتر
            
        Returns:
            اطلاعات کامل دکتر یا None
        """
        try:
            # اعتبارسنجی URL
            if not self._validate_doctor_url(doctor_url):
                return None
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # دریافت صفحه دکتر
                response = await client.get(doctor_url, headers=self.headers)
                response.raise_for_status()
                
                # استخراج اطلاعات پایه
                basic_info = await self._extract_basic_info(response.text, doctor_url)
                if not basic_info:
                    return None
                
                # استخراج اطلاعات API
                api_info = await self._extract_api_info(client, doctor_url, basic_info['slug'])
                if not api_info:
                    return None
                
                # ترکیب اطلاعات
                doctor_data = {**basic_info, **api_info}
                
                return Doctor(
                    name=doctor_data['name'],
                    slug=doctor_data['slug'],
                    center_id=str(doctor_data['center_id']),
                    service_id=str(doctor_data['service_id']),
                    user_center_id=str(doctor_data['user_center_id']),
                    terminal_id=str(doctor_data['terminal_id']),
                    specialty=doctor_data.get('specialty', ''),
                    center_name=doctor_data.get('center_name', ''),
                    center_address=doctor_data.get('center_address', ''),
                    center_phone=doctor_data.get('center_phone', ''),
                    is_active=True
                )
                
        except Exception as e:
            print(f"❌ خطا در استخراج اطلاعات دکتر: {e}")
            return None
    
    def _validate_doctor_url(self, url: str) -> bool:
        """اعتبارسنجی URL دکتر"""
        pattern = r'https?://(?:www\.)?paziresh24\.com/dr/[^/]+/?'
        return re.match(pattern, url) is not None
    
    async def _extract_basic_info(self, html: str, url: str) -> Optional[Dict]:
        """استخراج اطلاعات پایه از HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # استخراج slug از URL
            slug_match = re.search(r'/dr/([^/]+)/?', url)
            if not slug_match:
                return None
            slug = slug_match.group(1)
            
            # استخراج نام دکتر
            name_element = (
                soup.find('h1') or 
                soup.find('title') or
                soup.find('meta', {'property': 'og:title'})
            )
            
            if name_element:
                if name_element.name == 'meta':
                    name = name_element.get('content', '')
                else:
                    name = name_element.get_text().strip()
            else:
                name = f"دکتر {slug}"
            
            # پاک کردن کلمات اضافی
            name = re.sub(r'^(دکتر|Dr\.?)\s*', '', name)
            name = re.sub(r'\s*-.*$', '', name)
            name = name.strip()
            
            # استخراج تخصص
            specialty = self._extract_specialty(soup)
            
            # استخراج اطلاعات مرکز
            center_info = self._extract_center_info(soup)
            
            return {
                'name': name,
                'slug': slug,
                'specialty': specialty,
                **center_info
            }
            
        except Exception as e:
            print(f"❌ خطا در استخراج اطلاعات پایه: {e}")
            return None
    
    def _extract_specialty(self, soup: BeautifulSoup) -> str:
        """استخراج تخصص دکتر"""
        try:
            # جستجوی کلمات کلیدی تخصص
            specialty_keywords = ['تخصص', 'متخصص', 'فوق تخصص']
            
            for keyword in specialty_keywords:
                elements = soup.find_all(text=re.compile(keyword))
                for element in elements:
                    parent = element.parent
                    if parent:
                        text = parent.get_text().strip()
                        # استخراج تخصص از متن
                        if 'متخصص' in text:
                            specialty = re.sub(r'.*متخصص\s*', '', text)
                            specialty = re.sub(r'\s*\(.*\)', '', specialty)
                            if specialty.strip():
                                return specialty.strip()
            
            # جستجو در meta tags
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                desc = meta_desc.get('content', '')
                if 'متخصص' in desc:
                    specialty_match = re.search(r'متخصص\s+([^،\-\(\)]+)', desc)
                    if specialty_match:
                        return specialty_match.group(1).strip()
            
            return "عمومی"
            
        except Exception:
            return "عمومی"
    
    def _extract_center_info(self, soup: BeautifulSoup) -> Dict:
        """استخراج اطلاعات مرکز درمانی"""
        try:
            center_info = {
                'center_name': '',
                'center_address': '',
                'center_phone': ''
            }
            
            # جستجوی نام مرکز
            center_keywords = ['مطب', 'کلینیک', 'بیمارستان', 'مرکز']
            for keyword in center_keywords:
                elements = soup.find_all(text=re.compile(keyword))
                if elements:
                    center_info['center_name'] = elements[0].strip()
                    break
            
            if not center_info['center_name']:
                center_info['center_name'] = "مرکز درمانی"
            
            # جستجوی آدرس
            address_elements = soup.find_all(text=re.compile(r'آدرس|نشانی'))
            for element in address_elements:
                parent = element.parent
                if parent:
                    siblings = parent.find_next_siblings()
                    for sibling in siblings:
                        text = sibling.get_text().strip()
                        if len(text) > 10:  # آدرس معمولاً طولانی است
                            center_info['center_address'] = text
                            break
                    if center_info['center_address']:
                        break
            
            # جستجوی تلفن
            phone_pattern = r'(\d{3,4}[-\s]?\d{7,8}|\d{11})'
            phone_elements = soup.find_all(text=re.compile(phone_pattern))
            if phone_elements:
                phone_match = re.search(phone_pattern, phone_elements[0])
                if phone_match:
                    center_info['center_phone'] = phone_match.group(1)
            
            return center_info
            
        except Exception:
            return {
                'center_name': 'مرکز درمانی',
                'center_address': '',
                'center_phone': ''
            }
    
    async def _extract_api_info(self, client: httpx.AsyncClient, doctor_url: str, slug: str) -> Optional[Dict]:
        """
        استخراج اطلاعات API از درخواست‌های AJAX
        
        این بخش پیچیده‌ترین قسمت است که نیاز به reverse engineering دارد
        """
        try:
            # روش 1: جستجو در JavaScript کدها
            response = await client.get(doctor_url, headers=self.headers)
            html = response.text
            
            # جستجوی اطلاعات API در JavaScript
            api_info = self._extract_from_javascript(html)
            if api_info:
                return api_info
            
            # روش 2: تلاش برای دریافت از API جستجو
            search_api_info = await self._get_from_search_api(client, slug)
            if search_api_info:
                return search_api_info
            
            # روش 3: مقادیر پیش‌فرض (برای تست)
            return {
                'center_id': '0',
                'service_id': '0', 
                'user_center_id': '0',
                'terminal_id': '0'
            }
            
        except Exception as e:
            print(f"❌ خطا در استخراج اطلاعات API: {e}")
            return None
    
    def _extract_from_javascript(self, html: str) -> Optional[Dict]:
        """استخراج اطلاعات API از کدهای JavaScript"""
        try:
            # جستجوی الگوهای مختلف در JavaScript
            patterns = [
                r'center_id["\']?\s*:\s*["\']?(\d+)',
                r'service_id["\']?\s*:\s*["\']?(\d+)',
                r'user_center_id["\']?\s*:\s*["\']?(\d+)',
                r'terminal_id["\']?\s*:\s*["\']?(\d+)',
                r'centerId["\']?\s*:\s*["\']?(\d+)',
                r'serviceId["\']?\s*:\s*["\']?(\d+)',
            ]
            
            api_info = {}
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    field_name = pattern.split('[')[0].lower()
                    if 'center' in field_name and 'user' not in field_name:
                        api_info['center_id'] = matches[0]
                    elif 'service' in field_name:
                        api_info['service_id'] = matches[0]
                    elif 'user_center' in field_name:
                        api_info['user_center_id'] = matches[0]
                    elif 'terminal' in field_name:
                        api_info['terminal_id'] = matches[0]
            
            # بررسی کامل بودن اطلاعات
            required_fields = ['center_id', 'service_id', 'user_center_id', 'terminal_id']
            if all(field in api_info for field in required_fields):
                return api_info
            
            return None
            
        except Exception:
            return None
    
    async def _get_from_search_api(self, client: httpx.AsyncClient, slug: str) -> Optional[Dict]:
        """تلاش برای دریافت اطلاعات از API جستجو"""
        try:
            # این بخش نیاز به تحقیق بیشتر دارد
            # ممکن است API جستجوی عمومی وجود داشته باشد
            
            search_url = f"{self.api_base}/search/doctors"
            params = {'q': slug}
            
            response = await client.get(search_url, params=params)
            if response.status_code == 200:
                data = response.json()
                # پردازش نتایج...
                pass
            
            return None
            
        except Exception:
            return None
    
    def _parse_search_results(self, soup: BeautifulSoup) -> List[Dict]:
        """پارس کردن نتایج جستجو"""
        try:
            doctors = []
            
            # جستجوی کارت‌های دکتر در صفحه
            doctor_cards = soup.find_all(['div', 'article'], class_=re.compile(r'doctor|card|result'))
            
            for card in doctor_cards:
                doctor_info = self._parse_doctor_card(card)
                if doctor_info:
                    doctors.append(doctor_info)
            
            return doctors
            
        except Exception as e:
            print(f"❌ خطا در پارس نتایج جستجو: {e}")
            return []
    
    def _parse_doctor_card(self, card) -> Optional[Dict]:
        """پارس ��ردن کارت یک دکتر"""
        try:
            # استخراج لینک
            link_element = card.find('a', href=re.compile(r'/dr/'))
            if not link_element:
                return None
            
            doctor_url = urljoin(self.base_url, link_element['href'])
            
            # استخراج نام
            name_element = card.find(['h1', 'h2', 'h3', 'h4'])
            name = name_element.get_text().strip() if name_element else "نامشخص"
            
            # استخراج تخصص
            specialty_element = card.find(text=re.compile(r'متخصص|تخصص'))
            specialty = specialty_element.strip() if specialty_element else ""
            
            return {
                'name': name,
                'url': doctor_url,
                'specialty': specialty
            }
            
        except Exception:
            return None


# ==================== USAGE EXAMPLE ====================

async def example_usage():
    """مثال استفاده از API"""
    
    search_api = DoctorSearchAPI()
    
    # جستجوی دکتر
    doctors = await search_api.search_doctors("کاردیولوژی", city="تهران")
    print(f"🔍 {len(doctors)} دکتر پیدا شد")
    
    # استخراج اطلاعات از URL
    doctor_url = "https://www.paziresh24.com/dr/doctor-name/"
    doctor = await search_api.get_doctor_from_url(doctor_url)
    
    if doctor:
        print(f"✅ دکتر {doctor.name} با موفقیت استخراج شد")
        print(f"   تخصص: {doctor.specialty}")
        print(f"   مرکز: {doctor.center_name}")
    else:
        print("❌ خطا در استخراج اطلاعات دکتر")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())