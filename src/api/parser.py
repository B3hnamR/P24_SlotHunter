import requests
from bs4 import BeautifulSoup
import json
import re

def extract_doctor_info_from_url(url: str) -> dict:
    """
    Extracts doctor information from the given Paziresh24 URL.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the script tag containing the initial state
        script_tag = soup.find('script', string=re.compile('window.__INITIAL_STATE__'))

        if not script_tag:
            return None

        json_text = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});', script_tag.string).group(1)
        data = json.loads(json_text)

        doctor_page = data.get('doctorPage', {})
        doctor_info = doctor_page.get('doctor', {})
        center_info = doctor_page.get('center', {})

        if not doctor_info or not center_info:
            return None

        return {
            'name': doctor_info.get('displayName'),
            'specialty': doctor_info.get('speciality'),
            'slug': doctor_info.get('slug'),
            'center_id': center_info.get('id'),
            'service_id': next((item['id'] for item in center_info.get('services', []) if item['type'] == 'turn'), None),
            'user_center_id': center_info.get('userCenterId'),
            'terminal_id': center_info.get('terminalId'),
            'center_name': center_info.get('name'),
            'center_address': center_info.get('address'),
            'center_phone': center_info.get('phoneNumber'),
        }

    except (requests.RequestException, json.JSONDecodeError, AttributeError, KeyError) as e:
        print(f"Error extracting doctor info: {e}")
        return None
