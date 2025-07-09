#!/usr/bin/env python3
"""
تست ساده API پذیرش۲۴
"""
import sys
from pathlib import Path

# اضافه کردن مسیر src به Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.api.models import Doctor
from src.api.paziresh_client import PazireshAPI
from src.utils.logger import setup_logger


def test_api():
    """تست عملکرد API"""
    
    # تنظیم logger
    logger = setup_logger("TestAPI", level="INFO")
    
    # اطلاعات دکتر نمونه
    doctor = Doctor(
        name="دکتر مجتبی موسوی",
        slug="دکتر-سیدمحمدمجتبی-موسوی-0",
        center_id="9c95587c-0c20-4e94-974d-0dc025313f2d",
        service_id="9c95587c-ac9c-4e3c-b89d-b491a86926dc",
        user_center_id="9c95587c-47a6-4a55-a9b7-73fb8405e855",
        terminal_id="clinic-686dde06144236.30522977",
        specialty="آزمای��گاه و تصویربرداری",
        center_name="مطب دکتر سیدمحمدمجتبی موسوی"
    )
    
    logger.info("🚀 شروع تست API پذیرش۲۴")
    logger.info(f"👨‍⚕️ دکتر: {doctor.name}")
    logger.info(f"🏥 مرکز: {doctor.center_name}")
    
    # ایجاد کلاینت API
    api = PazireshAPI(doctor)
    
    # تست دریافت نوبت‌ها
    logger.info("🔍 در حال بررسی نوبت‌های موجود...")
    appointments = api.get_available_appointments(days_ahead=3)
    
    if appointments:
        logger.info(f"✅ {len(appointments)} نوبت موجود پیدا شد!")
        
        # نمایش 5 نوبت اول
        logger.info("📋 نوبت‌های موجود:")
        for i, apt in enumerate(appointments[:5], 1):
            logger.info(f"  {i}. {apt.time_str} (نوبت #{apt.workhour_turn_num})")
        
        if len(appointments) > 5:
            logger.info(f"  ... و {len(appointments) - 5} نوبت دیگر")
            
        # تست رزرو نوبت اول (فقط برای تست - بلافاصله لغو می‌شود)
        logger.info("🔄 تست رزرو نوبت...")
        first_appointment = appointments[0]
        
        reserve_result = api.reserve_appointment(first_appointment)
        if reserve_result.is_success:
            logger.info(f"✅ رزرو موفق: {reserve_result.message}")
            
            # لغو رزرو
            request_code = reserve_result.data.get('request_code')
            if request_code:
                cancel_result = api.cancel_reservation(request_code)
                if cancel_result.is_success:
                    logger.info(f"✅ لغو رزرو موفق: {cancel_result.message}")
                else:
                    logger.warning(f"⚠️ خطا در لغو رزرو: {cancel_result.message}")
        else:
            logger.warning(f"⚠️ خطا در رزرو: {reserve_result.message}")
    
    else:
        logger.info("📅 هیچ نوبت موجودی پیدا نشد")
    
    logger.info("🏁 تست به پایان رسید")


if __name__ == "__main__":
    test_api()