import pytest
import asyncio
from src.api.models import Doctor
from src.api.paziresh_client import PazireshAPI

import os
import sys

@pytest.mark.asyncio
async def test_paziresh_api_init():
    doc = Doctor(
        name="دکتر تست",
        slug="test-doctor",
        center_id="123",
        service_id="456",
        user_center_id="789",
        terminal_id="111",
        specialty="عمومی",
        center_name="مرکز تست",
        center_address="تهران",
        center_phone="02112345678",
        is_active=True
    )
    api = PazireshAPI(doc, timeout=2)
    # فقط تست مقداردهی اولیه و فراخوانی متد (بدون انتظار نتیجه واقعی)
    result = await api.get_available_appointments(days_ahead=1)
    assert isinstance(result, list)
