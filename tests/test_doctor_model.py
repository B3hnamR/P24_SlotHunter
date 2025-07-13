import pytest
from src.api.models import Doctor

def test_doctor_model_fields():
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
    assert doc.name == "دکتر تست"
    assert doc.slug == "test-doctor"
    assert doc.center_id == "123"
    assert doc.is_active is True
