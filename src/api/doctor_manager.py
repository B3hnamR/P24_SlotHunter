"""
سرویس مدیریت دکترها - اضافه کردن، به‌روزرسانی، حذف
"""
import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime

from src.database.models import Doctor, DoctorCenter, DoctorService
from src.api.doctor_extractor import DoctorExtractor

logger = logging.getLogger(__name__)


class DoctorManager:
    """کلاس مدیریت دکترها"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.extractor = DoctorExtractor()
    
    async def add_doctor_from_url(self, url: str, user_id: int = None) -> Tuple[bool, str, Optional[Doctor]]:
        """
        اضافه کردن دکتر از URL
        
        Returns:
            Tuple[success, message, doctor_object]
        """
        try:
            logger.info(f"🚀 شروع اضافه کردن دکتر از URL: {url}")
            
            # 1. استخراج اطلاعات از URL
            try:
                doctor_data = await self.extractor.extract_doctor_from_url(url)
            except Exception as e:
                return False, f"خطا در استخراج اطلاعات: {str(e)}", None
            
            # 2. بررسی وجود دکتر قبلی
            async with self.db_manager.session_scope() as session:
                existing_result = await session.execute(
                    select(Doctor).filter(
                        (Doctor.slug == doctor_data['extracted_slug']) |
                        (Doctor.doctor_id == doctor_data['doctor_id'])
                    )
                )
                existing_doctor = existing_result.scalar_one_or_none()
                
                if existing_doctor:
                    return False, f"دکتر {existing_doctor.name} قبلاً در سیستم موجود است", existing_doctor
                
                # 3. ایجاد دکتر جدید
                new_doctor = Doctor(
                    name=doctor_data['name'],
                    slug=doctor_data['extracted_slug'],
                    doctor_id=doctor_data['doctor_id'],
                    provider_id=doctor_data.get('provider_id'),
                    user_id=doctor_data.get('user_id'),
                    server_id=doctor_data.get('server_id', 1),
                    specialty=doctor_data.get('specialty', 'عمومی'),
                    biography=doctor_data.get('biography', ''),
                    image_url=doctor_data.get('image_url', ''),
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                session.add(new_doctor)
                await session.flush()  # برای دریافت ID
                
                # 4. اضافه کردن مراکز و سرویس‌ها
                centers_added = 0
                services_added = 0
                
                for center_data in doctor_data['centers']:
                    # بررسی وجود سرویس‌ها
                    if not center_data.get('services'):
                        logger.warning(f"⚠️ مرکز {center_data.get('center_name')} سرویسی ندارد، رد می‌شود")
                        continue
                    
                    # ایجاد مرکز
                    new_center = DoctorCenter(
                        doctor_id=new_doctor.id,
                        center_id=center_data['center_id'],
                        center_name=center_data['center_name'],
                        center_type=center_data.get('center_type', 'نامشخص'),
                        center_address=center_data.get('center_address'),
                        center_phone=center_data.get('center_phone'),
                        user_center_id=center_data['user_center_id'],
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    
                    session.add(new_center)
                    await session.flush()  # برای دریافت ID
                    centers_added += 1
                    
                    # اضافه کردن سرویس‌ها
                    for service_data in center_data['services']:
                        new_service = DoctorService(
                            center_id=new_center.id,
                            service_id=service_data['service_id'],
                            service_name=service_data['service_name'],
                            user_center_id=service_data['user_center_id'],
                            price=service_data.get('price', 0),
                            duration=service_data.get('duration', ''),
                            is_active=True,
                            created_at=datetime.utcnow()
                        )
                        
                        session.add(new_service)
                        services_added += 1
                
                if centers_added == 0:
                    # اگر هیچ مرکزی اضافه نشد، دکتر را حذف کن
                    await session.delete(new_doctor)
                    return False, "هیچ مرکز فعالی برای این دکتر یافت نشد", None
                
                # 5. ذخیره تغییرات
                await session.commit()
                
                success_message = f"""
✅ دکتر با موفقیت اضافه شد!

👨‍⚕️ **نام:** {new_doctor.name}
🏥 **تخصص:** {new_doctor.specialty}
🏢 **مراکز:** {centers_added} مرکز
🔧 **سرویس‌ها:** {services_added} سرویس

🔗 **لینک:** https://www.paziresh24.com/dr/{new_doctor.slug}/
                """.strip()
                
                logger.info(f"✅ دکتر {new_doctor.name} با موفقیت اضافه شد ({centers_added} مرکز، {services_added} سرویس)")
                return True, success_message, new_doctor
                
        except Exception as e:
            logger.error(f"❌ خطا در اضافه کردن دکتر: {e}")
            return False, f"خطا در اضافه کردن دکتر: {str(e)}", None
    
    async def get_doctor_with_details(self, doctor_id: int) -> Optional[Doctor]:
        """دریافت دکتر با جزئیات کامل"""
        try:
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(Doctor)
                    .options(
                        selectinload(Doctor.centers).selectinload(DoctorCenter.services)
                    )
                    .filter(Doctor.id == doctor_id)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت دکتر: {e}")
            return None
    
    async def get_all_doctors_with_details(self) -> List[Doctor]:
        """دریافت تمام دکترها با جزئیات"""
        try:
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(Doctor)
                    .options(
                        selectinload(Doctor.centers).selectinload(DoctorCenter.services)
                    )
                    .filter(Doctor.is_active == True)
                    .order_by(Doctor.created_at.desc())
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"❌ خطا در دریافت دکترها: {e}")
            return []
    
    async def update_doctor_status(self, doctor_id: int, is_active: bool) -> Tuple[bool, str]:
        """به‌روزرسانی وضعیت دکتر"""
        try:
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(Doctor).filter(Doctor.id == doctor_id)
                )
                doctor = result.scalar_one_or_none()
                
                if not doctor:
                    return False, "دکتر یافت نشد"
                
                doctor.is_active = is_active
                await session.commit()
                
                status_text = "فعال" if is_active else "غیرفعال"
                return True, f"وضعیت دکتر {doctor.name} به {status_text} تغییر یافت"
                
        except Exception as e:
            logger.error(f"❌ خطا در به‌روزرسانی وضعیت دکتر: {e}")
            return False, f"خطا در به‌روزرسانی: {str(e)}"
    
    async def delete_doctor(self, doctor_id: int) -> Tuple[bool, str]:
        """حذف دکتر (soft delete)"""
        try:
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(Doctor).filter(Doctor.id == doctor_id)
                )
                doctor = result.scalar_one_or_none()
                
                if not doctor:
                    return False, "دکتر یافت نشد"
                
                doctor.is_active = False
                await session.commit()
                
                return True, f"دکتر {doctor.name} حذف شد"
                
        except Exception as e:
            logger.error(f"❌ خطا در حذف دکتر: {e}")
            return False, f"خطا در حذف: {str(e)}"
    
    async def refresh_doctor_data(self, doctor_id: int) -> Tuple[bool, str]:
        """به‌روزرسانی اطلاعات دکتر از سایت"""
        try:
            async with self.db_manager.session_scope() as session:
                result = await session.execute(
                    select(Doctor).filter(Doctor.id == doctor_id)
                )
                doctor = result.scalar_one_or_none()
                
                if not doctor:
                    return False, "دکتر یافت نشد"
                
                # دریافت اطلاعات جدید
                doctor_url = f"https://www.paziresh24.com/dr/{doctor.slug}/"
                try:
                    new_data = await self.extractor.extract_doctor_from_url(doctor_url)
                except Exception as e:
                    return False, f"خطا در دریافت اطلاعات جدید: {str(e)}"
                
                # به‌روزرسانی اطلاعات اصلی
                doctor.name = new_data['name']
                doctor.specialty = new_data.get('specialty', doctor.specialty)
                doctor.biography = new_data.get('biography', doctor.biography)
                doctor.image_url = new_data.get('image_url', doctor.image_url)
                doctor.last_checked = datetime.utcnow()
                
                await session.commit()
                
                return True, f"اطلاعات دکتر {doctor.name} به‌روزرسانی شد"
                
        except Exception as e:
            logger.error(f"❌ خطا در به‌روزرسانی دکتر: {e}")
            return False, f"خطا در به‌روزرسانی: {str(e)}"
    
    def validate_doctor_url(self, url: str) -> Tuple[bool, str]:
        """اعتبارسنجی URL دکتر"""
        try:
            normalized_url = self.extractor.normalize_doctor_url(url)
            slug = self.extractor.extract_slug_from_url(url)
            
            if not slug:
                return False, "URL نامعتبر - slug یافت نشد"
            
            return True, f"URL معتبر - slug: {slug}"
            
        except Exception as e:
            return False, f"URL نامعتبر: {str(e)}"
    
    async def get_doctor_stats(self) -> Dict:
        """دریافت آمار دکترها"""
        try:
            async with self.db_manager.session_scope() as session:
                # تعداد دکترهای فعال
                active_result = await session.execute(
                    select(Doctor).filter(Doctor.is_active == True)
                )
                active_doctors = active_result.scalars().all()
                
                # تعداد مراکز
                centers_result = await session.execute(
                    select(DoctorCenter).filter(DoctorCenter.is_active == True)
                )
                total_centers = len(centers_result.scalars().all())
                
                # تعداد سرویس‌ها
                services_result = await session.execute(
                    select(DoctorService).filter(DoctorService.is_active == True)
                )
                total_services = len(services_result.scalars().all())
                
                return {
                    'total_doctors': len(active_doctors),
                    'total_centers': total_centers,
                    'total_services': total_services,
                    'doctors_with_subscriptions': len([d for d in active_doctors if d.subscription_count > 0])
                }
                
        except Exception as e:
            logger.error(f"❌ خطا در دریافت آمار: {e}")
            return {
                'total_doctors': 0,
                'total_centers': 0,
                'total_services': 0,
                'doctors_with_subscriptions': 0
            }