"""
مدل‌های داده برای API پذیرش۲۴
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Doctor:
    """مدل اطلاعات دکتر با اعتبارسنجی"""
    name: str
    slug: str
    center_id: str
    service_id: str
    user_center_id: str
    terminal_id: str
    specialty: str = ""
    center_name: str = ""
    center_address: str = ""
    center_phone: str = ""
    is_active: bool = True

    def __post_init__(self):
        required_fields = [
            ('name', self.name),
            ('slug', self.slug),
            ('center_id', self.center_id),
            ('service_id', self.service_id),
            ('user_center_id', self.user_center_id),
            ('terminal_id', self.terminal_id)
        ]
        for field, value in required_fields:
            if not value or not isinstance(value, str) or not value.strip():
                raise ValueError(f"Doctor: مقدار '{field}' نباید خالی یا نامعتبر باشد.")


@dataclass
class Appointment:
    """مدل نوبت ویزیت"""
    from_time: int  # Unix timestamp
    to_time: int    # Unix timestamp
    workhour_turn_num: int
    doctor_slug: str = ""
    
    @property
    def start_datetime(self) -> datetime:
        """تبدیل timestamp به datetime"""
        return datetime.fromtimestamp(self.from_time)
    
    @property
    def end_datetime(self) -> datetime:
        """تبدیل timestamp به datetime"""
        return datetime.fromtimestamp(self.to_time)
    
    @property
    def time_str(self) -> str:
        """نمایش زمان به صورت رشته"""
        return self.start_datetime.strftime('%Y/%m/%d %H:%M')


@dataclass
class APIResponse:
    """مدل پاسخ API"""
    status: int
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        """بررسی موفقیت درخواست"""
        return self.status == 1