"""
کلاینت پیشرفته API پذیرش۲۴ - بهینه شده برای جلوگیری از Rate Limiting
"""
import asyncio
import httpx
import logging
import random
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import time

from .models import Appointment, APIResponse
from src.database.models import Doctor, DoctorCenter, DoctorService

logger = logging.getLogger(__name__)


class EnhancedPazireshAPI:
    """کلاینت پیشرفته API پذیرش۲۴ - بهینه شده"""

    def __init__(self, doctor: Doctor, client: httpx.AsyncClient = None, timeout: int = 15, base_url: str = None, request_delay: float = 1.5):
        self.doctor = doctor
        self.client = client
        self.timeout = timeout
        self.request_delay = request_delay
        self.BASE_URL = base_url or "https://apigw.paziresh24.com/booking/v2"
        self.logger = logging.getLogger("EnhancedPazireshAPI")
        
        # User-Agent متنوع برای جلوگیری از تشخیص
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        self.base_headers = {
            'accept': 'application/json, text/plain, */*',
            'origin': 'https://www.paziresh24.com',
            'referer': 'https://www.paziresh24.com/',
            'user-agent': random.choice(user_agents),
            'accept-language': 'fa-IR,fa;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'pragma': 'no-cache'
        }

    def generate_terminal_id(self) -> str:
        """تولید terminal_id جدید"""
        timestamp = str(int(time.time() * 1000))[-12:]
        random_part = str(random.randint(10000000, 99999999))
        return f"clinic-{timestamp}.{random_part}"

    async def get_all_available_appointments(self, days_ahead: int = 5) -> List[Appointment]:
        """
        دریافت تمام نوبت‌های موجود برای دکتر (بهینه شده)
        """
        try:
            self.logger.info(f"🔍 شروع بررسی نوبت‌های {self.doctor.name} (محدود به {days_ahead} روز)")
            all_appointments = []
            
            # محدود کردن به اولین مرکز و سرویس برای کاهش درخواست‌ها
            active_centers = [c for c in self.doctor.centers if c.is_active][:1]  # فقط اولین مرکز
            
            for center_idx, center in enumerate(active_centers):
                active_services = [s for s in center.services if s.is_active][:1]  # فقط اولین سرویس
                
                for service_idx, service in enumerate(active_services):
                    try:
                        # اضافه کردن delay بین سرویس‌ها
                        if center_idx > 0 or service_idx > 0:
                            await asyncio.sleep(self.request_delay)
                        
                        appointments = await self._get_service_appointments(
                            center, service, days_ahead
                        )
                        
                        # اضافه کردن اطلاعات مرکز و سرویس به نوبت‌ها
                        for apt in appointments:
                            apt.doctor_slug = self.doctor.slug
                            apt.center_name = center.center_name
                            apt.service_name = service.service_name
                            apt.center_id = center.center_id
                            apt.service_id = service.service_id
                        
                        all_appointments.extend(appointments)
                        
                    except Exception as e:
                        self.logger.warning(f"⚠️ خطا در دریافت نوبت‌های {center.center_name} - {service.service_name}: {e}")
                        continue
            
            self.logger.info(f"✅ {len(all_appointments)} نوبت موجود پیدا شد برای {self.doctor.name}")
            return all_appointments
            
        except Exception as e:
            self.logger.error(f"❌ خطا در دریافت نوبت‌های {self.doctor.name}: {e}")
            return []

    async def _get_service_appointments(self, center: DoctorCenter, 
                                      service: DoctorService, days_ahead: int) -> List[Appointment]:
        """دریافت نوبت‌های یک سرویس خاص (بهینه شده)"""
        try:
            terminal_id = self.generate_terminal_id()
            
            # 1. دریافت روزهای موجود
            free_days_response = await self._get_free_days(center, service, terminal_id)
            if not free_days_response.is_success:
                return []

            available_days = free_days_response.data.get('calendar', {}).get('turns', [])
            if not available_days:
                return []

            # 2. محدود کردن به تعداد روزهای مشخص
            today = int(datetime.now().timestamp())
            future_days = [day for day in available_days if day >= today][:days_ahead]

            # 3. دریافت نوبت‌های هر روز با delay بیشتر
            all_appointments = []
            for i, day_timestamp in enumerate(future_days):
                # اضافه کردن delay بین درخواست‌ها
                if i > 0:
                    await asyncio.sleep(self.request_delay)
                
                day_appointments = await self._get_day_appointments(
                    center, service, terminal_id, day_timestamp
                )
                all_appointments.extend(day_appointments)
                
                # اگر نوبت پیدا شد، ادامه ندهیم (برای کاهش درخواست)
                if len(all_appointments) > 50:  # محدود کردن تعداد نوبت��ها
                    break

            return all_appointments
            
        except Exception as e:
            self.logger.error(f"❌ خطا در دریافت نوبت‌های سرویس: {e}")
            return []

    async def _get_free_days(self, center: DoctorCenter, service: DoctorService, 
                           terminal_id: str) -> APIResponse:
        """دریافت روزهای موجود"""
        headers = {
            **self.base_headers,
            'center_id': center.center_id,
            'terminal_id': terminal_id
        }
        
        data = {
            'center_id': center.center_id,
            'service_id': service.service_id,
            'user_center_id': service.user_center_id,
            'return_free_turns': 'false',
            'return_type': 'calendar',
            'terminal_id': terminal_id
        }
        
        try:
            # استفاده از client مشترک یا ایجاد client جدید
            if self.client:
                response = await self.client.post(
                    f"{self.BASE_URL}/getFreeDays",
                    data=data,
                    headers=headers
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.BASE_URL}/getFreeDays",
                        data=data,
                        headers=headers
                    )
            
            response.raise_for_status()
            result = response.json()
            
            return APIResponse(
                status=result.get('status', 0),
                message=result.get('message', ''),
                data=result
            )
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                self.logger.warning(f"⚠️ Rate limit hit, waiting 5 seconds...")
                await asyncio.sleep(5)
                return APIResponse(status=0, message="Rate limit", error="429")
            return APIResponse(
                status=0,
                message="خطا در ارتباط با سرور",
                error=str(e)
            )
        except httpx.RequestError as e:
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

    async def _get_day_appointments(self, center: DoctorCenter, service: DoctorService,
                                  terminal_id: str, day_timestamp: int) -> List[Appointment]:
        """دریافت نوبت‌های یک روز خاص"""
        headers = {
            **self.base_headers,
            'center_id': center.center_id,
            'terminal_id': terminal_id
        }
        
        data = {
            'center_id': center.center_id,
            'service_id': service.service_id,
            'user_center_id': service.user_center_id,
            'date': str(day_timestamp),
            'terminal_id': terminal_id
        }
        
        try:
            # استفاده از client مشترک یا ایجاد client جدید
            if self.client:
                response = await self.client.post(
                    f"{self.BASE_URL}/getFreeTurns",
                    data=data,
                    headers=headers
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.BASE_URL}/getFreeTurns",
                        data=data,
                        headers=headers
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
                
                if appointments:
                    date_str = datetime.fromtimestamp(day_timestamp).strftime('%Y/%m/%d')
                    self.logger.debug(f"📅 {center.center_name} - {date_str}: {len(appointments)} نوبت")
                
                return appointments
            return []
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                self.logger.warning(f"⚠️ Rate limit hit for day {day_timestamp}, skipping...")
                await asyncio.sleep(3)
            else:
                self.logger.error(f"❌ خطا در دریافت نوبت‌های روز {day_timestamp}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"❌ خطا در دریافت نوبت‌های روز {day_timestamp}: {e}")
            return []

    async def reserve_appointment(self, center: DoctorCenter, service: DoctorService,
                                appointment: Appointment) -> APIResponse:
        """رزرو موقت نوبت"""
        terminal_id = self.generate_terminal_id()
        
        headers = {
            **self.base_headers,
            'center_id': center.center_id,
            'terminal_id': terminal_id
        }
        
        data = {
            'center_id': center.center_id,
            'service_id': service.service_id,
            'user_center_id': service.user_center_id,
            'from': str(appointment.from_time),
            'to': str(appointment.to_time),
            'terminal_id': terminal_id
        }
        
        try:
            # استفاده از client مشترک یا ایجاد client جدید
            if self.client:
                response = await self.client.post(
                    f"{self.BASE_URL}/suspend",
                    data=data,
                    headers=headers
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.BASE_URL}/suspend",
                        data=data,
                        headers=headers
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

    async def cancel_reservation(self, center: DoctorCenter, request_code: str) -> APIResponse:
        """لغو رزرو نوبت"""
        terminal_id = self.generate_terminal_id()
        
        headers = {
            **self.base_headers,
            'center_id': center.center_id,
            'terminal_id': terminal_id
        }
        
        data = {
            'center_id': center.center_id,
            'request_code': request_code,
            'terminal_id': terminal_id
        }
        
        try:
            # استفاده از client مشترک یا ایجاد client جدید
            if self.client:
                response = await self.client.post(
                    f"{self.BASE_URL}/unsuspend",
                    data=data,
                    headers=headers
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.BASE_URL}/unsuspend",
                        data=data,
                        headers=headers
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

    async def get_appointment_booking_url(self, center: DoctorCenter, 
                                        service: DoctorService) -> str:
        """تولید لینک رزرو نوبت"""
        try:
            base_url = "https://www.paziresh24.com/booking"
            params = [
                f"centerId={center.center_id}",
                f"serviceId={service.service_id}",
                f"cityName=tehran",  # پیش‌فرض
                f"providerId={getattr(self.doctor, 'provider_id', '')}",
                f"userId={getattr(self.doctor, 'user_id', '')}"
            ]
            
            booking_url = f"{base_url}/{self.doctor.slug}/?{'&'.join(params)}"
            return booking_url
            
        except Exception as e:
            self.logger.error(f"❌ خطا در تولید لینک رزرو: {e}")
            return f"https://www.paziresh24.com/dr/{self.doctor.slug}/"