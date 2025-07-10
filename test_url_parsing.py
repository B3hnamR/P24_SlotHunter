#!/usr/bin/env python3
"""
Test URL parsing and doctor info fetching
"""
import sys
from pathlib import Path
import urllib.parse
import re
import requests
from bs4 import BeautifulSoup

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_url_parsing():
    """Test URL parsing with different formats"""
    
    # Test URLs
    test_urls = [
        "https://www.paziresh24.com/dr/دکتر-نام-خانوادگی-0/",
        "https://www.paziresh24.com/dr/%D8%AF%DA%A9%D8%AA%D8%B1-%D9%86%D8%A7%D9%85-%D8%AE%D8%A7%D9%86%D9%88%D8%A7%D8%AF%DA%AF%DB%8C-0/",
        "https://www.paziresh24.com/dr/دکتر-سیدمحمدمجتبی-موسوی-0/",
        "https://www.paziresh24.com/dr/%D8%AF%DA%A9%D8%AA%D8%B1-%D8%B3%DB%8C%D8%AF%D9%85%D8%AD%D9%85%D8%AF%D9%85%D8%AC%D8%AA%D8%A8%DB%8C-%D9%85%D9%88%D8%B3%D9%88%DB%8C-0/"
    ]
    
    print("🧪 Testing URL Parsing...")
    print("=" * 60)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing URL:")
        print(f"   Original: {url}")
        
        # Extract slug
        if '/dr/' in url:
            slug = url.split('/dr/')[1].rstrip('/')
            print(f"   Extracted slug: {slug}")
            
            # URL decode
            decoded_slug = urllib.parse.unquote(slug)
            print(f"   Decoded slug: {decoded_slug}")
            
            # Check regex match
            regex_match = re.match(r'https://www\.paziresh24\.com/dr/.+', url)
            print(f"   Regex match: {regex_match is not None}")
        
        print("-" * 40)

def fetch_doctor_info_real(slug: str) -> dict:
    """
    Real implementation to fetch doctor info from Paziresh24
    """
    try:
        # URL decode the slug
        decoded_slug = urllib.parse.unquote(slug)
        
        # Construct the URL
        url = f"https://www.paziresh24.com/dr/{slug}/"
        
        print(f"🔍 Fetching doctor info from: {url}")
        
        # Headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fa,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Make request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract doctor information
        doctor_info = {
            'name': 'نامشخص',
            'slug': decoded_slug,
            'specialty': 'نامشخص',
            'center_name': 'نامشخص',
            'center_address': 'نامشخص',
            'center_phone': 'نامشخص',
            'center_id': 'unknown',
            'service_id': 'unknown',
            'user_center_id': 'unknown',
            'terminal_id': 'unknown'
        }
        
        # Try to extract doctor name
        name_selectors = [
            'h1[data-testid="doctor-name"]',
            'h1.doctor-name',
            '.doctor-info h1',
            'h1',
            '.profile-header h1'
        ]
        
        for selector in name_selectors:
            name_element = soup.select_one(selector)
            if name_element:
                doctor_info['name'] = name_element.get_text().strip()
                break
        
        # Try to extract specialty
        specialty_selectors = [
            '[data-testid="doctor-specialty"]',
            '.doctor-specialty',
            '.specialty',
            '.doctor-info .specialty'
        ]
        
        for selector in specialty_selectors:
            specialty_element = soup.select_one(selector)
            if specialty_element:
                doctor_info['specialty'] = specialty_element.get_text().strip()
                break
        
        # Try to extract center information
        center_selectors = [
            '[data-testid="center-name"]',
            '.center-name',
            '.clinic-name',
            '.center-info h2'
        ]
        
        for selector in center_selectors:
            center_element = soup.select_one(selector)
            if center_element:
                doctor_info['center_name'] = center_element.get_text().strip()
                break
        
        # Try to extract address
        address_selectors = [
            '[data-testid="center-address"]',
            '.center-address',
            '.address',
            '.clinic-address'
        ]
        
        for selector in address_selectors:
            address_element = soup.select_one(selector)
            if address_element:
                doctor_info['center_address'] = address_element.get_text().strip()
                break
        
        # Try to extract phone
        phone_selectors = [
            '[data-testid="center-phone"]',
            '.center-phone',
            '.phone',
            '.clinic-phone'
        ]
        
        for selector in phone_selectors:
            phone_element = soup.select_one(selector)
            if phone_element:
                doctor_info['center_phone'] = phone_element.get_text().strip()
                break
        
        # Try to extract API IDs from JavaScript or data attributes
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                script_content = script.string
                
                # Look for center_id patterns
                center_id_match = re.search(r'"center_id":\s*"([^"]+)"', script_content)
                if center_id_match:
                    doctor_info['center_id'] = center_id_match.group(1)
                
                # Look for service_id patterns
                service_id_match = re.search(r'"service_id":\s*"([^"]+)"', script_content)
                if service_id_match:
                    doctor_info['service_id'] = service_id_match.group(1)
                
                # Look for user_center_id patterns
                user_center_id_match = re.search(r'"user_center_id":\s*"([^"]+)"', script_content)
                if user_center_id_match:
                    doctor_info['user_center_id'] = user_center_id_match.group(1)
                
                # Look for terminal_id patterns
                terminal_id_match = re.search(r'"terminal_id":\s*"([^"]+)"', script_content)
                if terminal_id_match:
                    doctor_info['terminal_id'] = terminal_id_match.group(1)
        
        return doctor_info
        
    except Exception as e:
        print(f"❌ Error fetching doctor info: {e}")
        return None

def test_doctor_info_fetching():
    """Test real doctor info fetching"""
    
    # Test with a real doctor URL (you can replace with actual URL)
    test_slug = "دکتر-سیدمحمدمجتبی-موسوی-0"
    
    print(f"\n🧪 Testing Doctor Info Fetching...")
    print("=" * 60)
    print(f"Testing slug: {test_slug}")
    
    doctor_info = fetch_doctor_info_real(test_slug)
    
    if doctor_info:
        print("\n✅ Doctor info fetched successfully:")
        for key, value in doctor_info.items():
            print(f"   {key}: {value}")
    else:
        print("\n❌ Failed to fetch doctor info")

if __name__ == "__main__":
    test_url_parsing()
    test_doctor_info_fetching()