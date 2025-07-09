"""
کلاینت API پذیرش۲۴ - بدون نیاز به web scraping
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from .models import Doctor, Appointment, APIResponse


class PazireshAPI:
    """کلاینت API پذیرش۲۴"""
    
    BASE_URL = "https://apigw.paziresh24.com/booking/v2"
    
    def __init__(self, doctor: Doctor, timeout: int = 10):
        self.doctor = doctor
        self.timeout = timeout
        self.logger = logging.getLogger(f"PazireshAPI.{doctor.slug}")
        
        # تنظیم session
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'origin': 'https://www.paziresh24.com',
            'referer': 'https://www.paziresh24.com/',
            'center_id': doctor.center_id,
            'terminal_id': doctor.terminal_id,
            'user-agent': 'Mozilla/5.0 (compatible; SlotHunter/1.0)'
        })
    
    def get_available_appointments(self, days_ahead: int = 7) -> List[Appointment]:
        """
        دریافت تمام نوبت‌های موجود
        
        Args:
            days_ahead: تعداد روزهای آینده برای بررسی
            
        Returns:
            لیست نوبت‌های موجود
        """
        try:
            self.logger.info(f"🔍 شروع بررسی نوبت‌های {self.doctor.name}")
            
            # 1. دریافت روزهای موجود
            free_days_response = self._get_free_days()
            if not free_days_response.is_success:
                self.logger.warning(f"⚠️ خطا در دریافت روزهای موجود: {free_days_response.message}")
                return []
            
            available_days = free_days_response.data.get('calendar', {}).get('turns', [])
            if not available_days:
                self.logger.info("📅 هیچ روز موجودی پیدا نشد")
                return []
            
            # 2. محدود کردن به تعداد روزهای مشخص
            today = int(datetime.now().timestamp())
            future_days = [day for day in available_days if day >= today][:days_ahead]
            
            # 3. دریافت نوبت‌های هر روز
            all_appointments = []
            for day_timestamp in future_days:
                day_appointments = self._get_day_appointments(day_timestamp)
                if day_appointments:
                    # اضافه کردن slug دکتر به هر نوبت
                    for apt in day_appointments:
                        apt.doctor_slug = self.doctor.slug
                    all_appointments.extend(day_appointments)
            
            self.logger.info(f"✅ {len(all_appointments)} نوبت موجود پیدا شد")
            return all_appointments
            
        except Exception as e:
            self.logger.error(f"❌ خطا در دریافت نوبت‌ها: {e}")
            return []
    
    def _get_free_days(self) -> APIResponse:
        """دریافت روزهای موجود"""
        try:
            data = {
                'center_id': self.doctor.center_id,
                'service_id': self.doctor.service_id,
                'user_center_id': self.doctor.user_center_id,
                'return_free_turns': 'false',
                'return_type': 'calendar',
                'terminal_id': self.doctor.terminal_id
            }
            
            response = self.session.post(
                f"{self.BASE_URL}/getFreeDays",
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return APIResponse(
                status=result.get('status', 0),
                message=result.get('message', ''),
                data=result
            )
            
        except requests.RequestException as e:
            return APIResponse(
                status=0,
                message="خطا در ارتباط با سرور",
                error=str(e)
            )
        except Exception as e:
            return APIResponse(
                status=0,
                message="خطای غیرمنتظره",
                error=str(e)
            )
    
    def _get_day_appointments(self, day_timestamp: int) -> List[Appointment]:
        """دریافت نوبت‌های یک روز خاص"""
        try:
            data = {
                'center_id': self.doctor.center_id,
                'service_id': self.doctor.service_id,
                'user_center_id': self.doctor.user_center_id,
                'date': str(day_timestamp),
                'terminal_id': self.doctor.terminal_id
            }
            
            response = self.session.post(
                f"{self.BASE_URL}/getFreeTurns",
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('status') == 1:
                appointments = []
                for apt_data in result.get('result', []):
                    appointment = Appointment(
                        from_time=apt_data['from'],
                        to_time=apt_data['to'],
                        workhour_turn_num=apt_data['workhour_turn_num']
                    )
                    appointments.append(appointment)
                
                date_str = datetime.fromtimestamp(day_timestamp).strftime('%Y/%m/%d')
                self.logger.debug(f"📅 {date_str}: {len(appointments)} نوبت موجود")
                return appointments
            
            return []
            
        except Exception as e:
            self.logger.error(f"❌ خطا در دریافت نوبت‌های روز {day_timestamp}: {e}")
            return []
    
    def reserve_appointment(self, appointment: Appointment) -> APIResponse:
        """رزرو موقت نوبت"""
        try:
            data = {
                'center_id': self.doctor.center_id,
                'service_id': self.doctor.service_id,
                'user_center_id': self.doctor.user_center_id,
                'from': str(appointment.from_time),
                'to': str(appointment.to_time),
                'terminal_id': self.doctor.terminal_id
            }
            
            response = self.session.post(
                f"{self.BASE_URL}/suspend",
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return APIResponse(
                status=result.get('status', 0),
                message=result.get('message', ''),
                data=result
            )
            
        except Exception as e:
            return APIResponse(
                status=0,
                message="خطا در رزرو نوبت",
                error=str(e)
            )
    
    def cancel_reservation(self, request_code: str) -> APIResponse:
        """لغو رزرو نوبت"""
        try:
            data = {
                'center_id': self.doctor.center_id,
                'request_code': request_code,
                'terminal_id': self.doctor.terminal_id
            }
            
            response = self.session.post(
                f"{self.BASE_URL}/unsuspend",
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return APIResponse(
                status=result.get('status', 0),
                message=result.get('message', ''),
                data=result
            )
            
        except Exception as e:
            return APIResponse(
                status=0,
                message="خطا در لغو رزرو",
                error=str(e)
            )