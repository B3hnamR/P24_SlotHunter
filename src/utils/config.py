"""
مدیریت تنظیمات پروژه
"""
import os
import yaml
from typing import Dict, List, Any
from pathlib import Path

from src.api.models import Doctor


class Config:
    """کلاس مدیریت تنظیمات"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """بارگذاری فایل تنظیمات"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                # جایگزینی متغیرهای محیطی
                config = self._replace_env_vars(config)
                return config
            else:
                return self._get_default_config()
        except Exception as e:
            print(f"❌ خطا در بارگذاری تنظیمات: {e}")
            return self._get_default_config()
    
    def _replace_env_vars(self, obj: Any) -> Any:
        """جایگزینی متغیرهای محیطی در تنظیمات"""
        if isinstance(obj, dict):
            return {k: self._replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        return obj
    
    def _get_default_config(self) -> Dict[str, Any]:
        """تنظیمات پیش‌فرض"""
        return {
            'telegram': {
                'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
                'admin_chat_id': int(os.getenv('ADMIN_CHAT_ID', '0'))
            },
            'monitoring': {
                'check_interval': 30,
                'max_retries': 3,
                'timeout': 10,
                'days_ahead': 7
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/slothunter.log',
                'max_size': '10MB',
                'backup_count': 5
            },
            'doctors': []
        }
    
    @property
    def telegram_bot_token(self) -> str:
        """توکن ربات تلگرام"""
        return self._config.get('telegram', {}).get('bot_token', '')
    
    @property
    def admin_chat_id(self) -> int:
        """شناسه چت ادمین"""
        return self._config.get('telegram', {}).get('admin_chat_id', 0)
    
    @property
    def check_interval(self) -> int:
        """فاصله زمانی بررسی (ثانیه)"""
        return self._config.get('monitoring', {}).get('check_interval', 30)
    
    @property
    def max_retries(self) -> int:
        """حداکثر تعداد تلاش مجدد"""
        return self._config.get('monitoring', {}).get('max_retries', 3)
    
    @property
    def api_timeout(self) -> int:
        """timeout درخواست‌های API"""
        return self._config.get('monitoring', {}).get('timeout', 10)
    
    @property
    def days_ahead(self) -> int:
        """تعداد روزهای آینده برای بررسی"""
        return self._config.get('monitoring', {}).get('days_ahead', 7)
    
    @property
    def log_level(self) -> str:
        """سطح لاگ"""
        return self._config.get('logging', {}).get('level', 'INFO')
    
    @property
    def log_file(self) -> str:
        """مسیر فایل لاگ"""
        return self._config.get('logging', {}).get('file', 'logs/slothunter.log')
    
    def get_doctors(self) -> List[Doctor]:
        """دریافت لیست دکترها"""
        doctors = []
        for doctor_data in self._config.get('doctors', []):
            try:
                doctor = Doctor(
                    name=doctor_data['name'],
                    slug=doctor_data['slug'],
                    center_id=doctor_data['center_id'],
                    service_id=doctor_data['service_id'],
                    user_center_id=doctor_data['user_center_id'],
                    terminal_id=doctor_data['terminal_id'],
                    specialty=doctor_data.get('specialty', ''),
                    center_name=doctor_data.get('center_name', ''),
                    center_address=doctor_data.get('center_address', ''),
                    center_phone=doctor_data.get('center_phone', ''),
                    is_active=doctor_data.get('is_active', True)
                )
                doctors.append(doctor)
            except KeyError as e:
                print(f"❌ خطا در بارگذاری دکتر: فیلد {e} موجود نیست")
        
        return doctors
    
    def reload(self):
        """بارگذاری مجدد ��نظیمات"""
        self._config = self._load_config()