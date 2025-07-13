#!/usr/bin/env python3
"""
تست استخراج اطلاعات دکتر از صفحه پذیرش۲۴
"""
import asyncio
import httpx
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class DoctorInfoExtractor:
    """استخراج اطلاعات دکتر از صفحه پذیرش۲۴"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fa,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
    
    async def extract_doctor_info(self, doctor_url: str):
        """استخراج اطلاعات دکتر از URL"""
        print(f"🔍 تحلیل URL: {doctor_url}")
        
        # 1. اعتبارسنجی URL
        if not self._validate_url(doctor_url):
            print("❌ URL نامعتبر")
            return None
        
        # 2. استخراج slug
        slug = self._extract_slug(doctor_url)
        print(f"📝 Slug: {slug}")
        
        # 3. دریافت صفحه
        html_content = await self._fetch_page(doctor_url)
        if not html_content:
            print("❌ خطا در دریافت صفحه")
            return None
        
        # 4. تحلیل محتوا
        doctor_info = await self._analyze_page_content(html_content, slug)
        
        return doctor_info
    
    def _validate_url(self, url: str) -> bool:
        """اعتبارسنجی URL"""
        pattern = r'https?://(?:www\.)?paziresh24\.com/dr/[^/]+/?'
        return re.match(pattern, url) is not None
    
    def _extract_slug(self, url: str) -> str:
        """استخراج slug از URL"""
        match = re.search(r'/dr/([^/]+)/?', url)
        return match.group(1) if match else ""
    
    async def _fetch_page(self, url: str) -> str:
        """دریافت محتوای صفحه"""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"❌ خطا در دریافت صفحه: {e}")
            return ""
    
    async def _analyze_page_content(self, html: str, slug: str) -> dict:
        """تحلیل محتوای صفحه"""
        print("\n🔍 شروع تحلیل محتوا...")
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # اطلاعات پایه
        basic_info = self._extract_basic_info(soup, slug)
        print(f"✅ اطلاعات پایه: {basic_info}")
        
        # جستجوی اطلاعات API
        api_info = self._search_api_info(html, soup)
        print(f"🔑 اطلاعات API: {api_info}")
        
        # ترکیب اطلاعات
        result = {**basic_info, **api_info}
        
        # نمایش نتیجه نهایی
        self._display_results(result)
        
        return result
    
    def _extract_basic_info(self, soup: BeautifulSoup, slug: str) -> dict:
        """استخراج اطلاعات پایه"""
        info = {'slug': slug}
        
        # نام دکتر
        name_selectors = [
            'h1',
            '[data-testid="doctor-name"]',
            '.doctor-name',
            'title'
        ]
        
        for selector in name_selectors:
            element = soup.select_one(selector)
            if element:
                name = element.get_text().strip()
                name = re.sub(r'^(دکتر|Dr\.?)\s*', '', name)
                name = re.sub(r'\s*-.*$', '', name)
                if name:
                    info['name'] = name
                    break
        
        # تخصص
        specialty_patterns = [
            r'متخصص\s+([^،\-\(\)]+)',
            r'تخصص[:\s]*([^،\-\(\)]+)',
            r'specialty["\']?\s*:\s*["\']([^"\']+)'
        ]
        
        for pattern in specialty_patterns:
            matches = re.findall(pattern, str(soup), re.IGNORECASE)
            if matches:
                info['specialty'] = matches[0].strip()
                break
        
        # نام مرکز
        center_patterns = [
            r'(مطب|کلینیک|بیمارستان|مرکز)\s+([^،\-\(\)]+)',
            r'center["\']?\s*:\s*["\']([^"\']+)'
        ]
        
        for pattern in center_patterns:
            matches = re.findall(pattern, str(soup), re.IGNORECASE)
            if matches:
                info['center_name'] = matches[0] if isinstance(matches[0], str) else matches[0][1]
                break
        
        return info
    
    def _search_api_info(self, html: str, soup: BeautifulSoup) -> dict:
        """جستجوی اطلاعات API"""
        api_info = {}
        
        print("\n🔍 جستجوی اطلاعات API...")
        
        # 1. جستجو در JavaScript variables
        js_patterns = [
            r'center_id["\']?\s*:\s*["\']?(\d+)',
            r'service_id["\']?\s*:\s*["\']?(\d+)',
            r'user_center_id["\']?\s*:\s*["\']?(\d+)',
            r'terminal_id["\']?\s*:\s*["\']?(\d+)',
            r'centerId["\']?\s*:\s*["\']?(\d+)',
            r'serviceId["\']?\s*:\s*["\']?(\d+)',
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                field_name = pattern.split('[')[0].lower()
                if 'center' in field_name and 'user' not in field_name:
                    api_info['center_id'] = matches[0]
                    print(f"  ✅ center_id: {matches[0]}")
                elif 'service' in field_name:
                    api_info['service_id'] = matches[0]
                    print(f"  ✅ service_id: {matches[0]}")
                elif 'user_center' in field_name:
                    api_info['user_center_id'] = matches[0]
                    print(f"  ✅ user_center_id: {matches[0]}")
                elif 'terminal' in field_name:
                    api_info['terminal_id'] = matches[0]
                    print(f"  ✅ terminal_id: {matches[0]}")
        
        # 2. جستجو در JSON objects
        json_patterns = [
            r'doctorData\s*=\s*({[^}]+})',
            r'appointmentData\s*=\s*({[^}]+})',
            r'bookingConfig\s*=\s*({[^}]+})',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                try:
                    data = json.loads(match)
                    print(f"  📋 JSON object found: {data}")
                    
                    # استخراج اطلاعات از JSON
                    for key in ['center_id', 'service_id', 'user_center_id', 'terminal_id']:
                        if key in data:
                            api_info[key] = str(data[key])
                            print(f"  ✅ {key}: {data[key]}")
                            
                except json.JSONDecodeError:
                    continue
        
        # 3. جستجو در data attributes
        data_attrs = soup.find_all(attrs=lambda x: x and any(
            attr.startswith('data-') and any(keyword in attr for keyword in ['center', 'service', 'terminal'])
            for attr in x.keys()
        ))
        
        for element in data_attrs:
            print(f"  📋 Data attribute element: {element.attrs}")
            for attr, value in element.attrs.items():
                if 'center' in attr and 'user' not in attr:
                    api_info['center_id'] = str(value)
                elif 'service' in attr:
                    api_info['service_id'] = str(value)
                elif 'user_center' in attr or 'user-center' in attr:
                    api_info['user_center_id'] = str(value)
                elif 'terminal' in attr:
                    api_info['terminal_id'] = str(value)
        
        return api_info
    
    def _display_results(self, result: dict):
        """نمایش نتایج"""
        print("\n" + "="*50)
        print("📊 نتایج استخراج:")
        print("="*50)
        
        # اطلاعات پایه
        print("\n✅ اطلاعات پایه:")
        for key in ['name', 'slug', 'specialty', 'center_name']:
            value = result.get(key, 'یافت نشد')
            print(f"  {key}: {value}")
        
        # اطلاعات API
        print("\n🔑 اطلاعات API:")
        api_fields = ['center_id', 'service_id', 'user_center_id', 'terminal_id']
        found_api_fields = 0
        
        for field in api_fields:
            value = result.get(field, '❌ یافت نشد')
            status = "✅" if field in result else "❌"
            print(f"  {status} {field}: {value}")
            if field in result:
                found_api_fields += 1
        
        # خلاصه
        print(f"\n📈 خلاصه: {found_api_fields}/{len(api_fields)} فیلد API یافت شد")
        
        if found_api_fields == len(api_fields):
            print("🎉 تمام اطلاعات مورد نیاز یافت شد!")
        elif found_api_fields > 0:
            print("⚠️ برخی اطلاعات API یافت شد، ولی ناقص است")
        else:
            print("❌ هیچ اطلاعات API یافت نشد")
        
        print("="*50)


async def main():
    """تست اصلی"""
    print("🧪 تست استخراج اطلاعات دکتر از پذیرش۲۴")
    print("="*50)
    
    # URL نمونه - شما URL واقعی وارد کنید
    test_urls = [
        "https://www.paziresh24.com/dr/دکتر-سیدمحمدمجتبی-موسوی-0/",
        "https://www.paziresh24.com/dr/دکتر-محمدرضا-کریمی-1/",
        "https://www.paziresh24.com/dr/دکتر-فاطمه-احمدی-2/",
        # شما URL های بیشتری اضافه کنید
    ]
    
    print("💡 نکته: اگر URL خاصی دارید، آن را به جای URL های نمونه قرار دهید")
    print("📝 یا می‌توانید URL را به عنوان آرگومان وارد کنید:")
    print("   python test_doctor_extraction.py 'https://www.paziresh24.com/dr/doctor-name/'")
    
    # بررسی آرگومان خط فرمان
    import sys
    if len(sys.argv) > 1:
        custom_url = sys.argv[1]
        if custom_url.startswith('http'):
            test_urls = [custom_url]
            print(f"🎯 استفاده از URL سفارشی: {custom_url}")
    
    extractor = DoctorInfoExtractor()
    
    for url in test_urls:
        print(f"\n🔍 تست URL: {url}")
        result = await extractor.extract_doctor_info(url)
        
        if result:
            print("✅ استخراج موفق")
        else:
            print("❌ استخراج ناموفق")
        
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())