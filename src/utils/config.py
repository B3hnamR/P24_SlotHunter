"""
مدیریت تنظیمات پروژه
"""
import os
import yaml
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

from typing import TYPE_CHECKING
from src.utils.logger import get_logger

if TYPE_CHECKING:
    from src.api.models import Doctor


class DatabaseConfig(BaseModel):
    url: str = Field("sqlite+aiosqlite:///data/slothunter.db", env="DATABASE_URL")

class ApiConfig(BaseModel):
    base_url: str = Field("https://apigw.paziresh24.com/booking/v2", env="API_BASE_URL")

class TelegramConfig(BaseModel):
    bot_token: str = Field("", env="TELEGRAM_BOT_TOKEN")
    admin_chat_id: int = Field(0, env="ADMIN_CHAT_ID")

class MonitoringConfig(BaseModel):
    check_interval: int = Field(30, env="CHECK_INTERVAL")
    max_retries: int = 3
    timeout: int = 10
    days_ahead: int = 7

class LoggingConfig(BaseModel):
    level: str = Field("INFO", env="LOG_LEVEL")
    file: str = "logs/slothunter.log"
    max_size: str = "10MB"
    backup_count: int = 5

class AppConfig(BaseModel):
    database: DatabaseConfig = DatabaseConfig()
    api: ApiConfig = ApiConfig()
    telegram: TelegramConfig = TelegramConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    logging: LoggingConfig = LoggingConfig()
    doctors: List[Dict[str, Any]] = []

class Config:
    """کلاس مدیریت تنظیمات"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        load_dotenv()
        self.config_path = Path(config_path)
        self.logger = get_logger("Config")
        self._config = self._load_and_validate_config()
    
    def _load_and_validate_config(self) -> AppConfig:
        """بارگذاری و اعتبارسنجی تنظیمات"""
        config_data = self._load_config_from_file()
        # پردازش متغیرهای محیطی
        config_data = self._replace_env_vars(config_data)
        try:
            return AppConfig(**config_data)
        except ValidationError as e:
            self.logger.error(f"❌ خطای اعتبارسنجی تنظیمات: {e}")
            # در صورت خطا، از تنظیمات پیش‌فرض استفاده کن
            return AppConfig(**self._get_default_config())

    def _load_config_from_file(self) -> Dict[str, Any]:
        """بارگذاری تنظیمات از فایل"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _replace_env_vars(self, obj: Any) -> Any:
        """جایگزینی متغیرهای محیطی در تنظیمات"""
        if isinstance(obj, dict):
            return {k: self._replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            value = os.getenv(env_var, obj)
            # تبدیل رشته‌های عددی
            if env_var == 'ADMIN_CHAT_ID' and value.isdigit():
                return int(value)
            return value
        return obj
    
    def _get_default_config(self) -> Dict[str, Any]:
        """تنظیمات پیش‌فرض"""
        admin_chat_id = os.getenv('ADMIN_CHAT_ID', '0')
        if admin_chat_id.isdigit():
            admin_chat_id = int(admin_chat_id)
        else:
            admin_chat_id = 0
            
        return {
            'database': {
                'url': os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///data/slothunter.db')
            },
            'api': {
                'base_url': os.getenv('API_BASE_URL', 'https://apigw.paziresh24.com/booking/v2')
            },
            'telegram': {
                'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
                'admin_chat_id': admin_chat_id
            },
            'monitoring': {
                'check_interval': int(os.getenv('CHECK_INTERVAL', '30')),
                'max_retries': 3,
                'timeout': 10,
                'days_ahead': 7
            },
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'file': 'logs/slothunter.log',
                'max_size': '10MB',
                'backup_count': 5
            },
            'doctors': []
        }
    
    @property
    def telegram_bot_token(self) -> str:
        return self._config.telegram.bot_token

    @property
    def admin_chat_id(self) -> int:
        return self._config.telegram.admin_chat_id

    @property
    def check_interval(self) -> int:
        return self._config.monitoring.check_interval

    @property
    def max_retries(self) -> int:
        return self._config.monitoring.max_retries

    @property
    def api_timeout(self) -> int:
        return self._config.monitoring.timeout

    @property
    def days_ahead(self) -> int:
        return self._config.monitoring.days_ahead

    @property
    def log_level(self) -> str:
        return self._config.logging.level

    @property
    def log_file(self) -> str:
        return self._config.logging.file

    @property
    def database_url(self) -> str:
        return self._config.database.url

    @property
    def api_base_url(self) -> str:
        return self._config.api.base_url
    
    def get_doctors(self) -> List["Doctor"]:
        """دریافت لیست دکترها"""
        from src.api.models import Doctor
        doctors = []
        for doctor_data in self._config.doctors:
            if isinstance(doctor_data, dict):
                doctors.append(Doctor(**doctor_data))
            else:
                doctors.append(doctor_data)
        return doctors
    
    def reload(self):
        """بارگذاری مجدد تنظیمات"""
        load_dotenv()
        self._config = self._load_and_validate_config()