# Alembic Migration Guide

برای مدیریت migration دیتابیس پروژه P24_SlotHunter از Alembic استفاده کنید.

## دستورات اصلی

- ایجاد migration جدید:
  ```
  alembic revision --autogenerate -m "توضیح تغییر"
  ```
- اعمال migrationها:
  ```
  alembic upgrade head
  ```
- مشاهده وضعیت migration:
  ```
  alembic current
  ```
- بازگشت به migration قبلی:
  ```
  alembic downgrade -1
  ```

## نکات مهم
- آدرس دیتابیس به صورت پیش‌فرض sqlite:///data/slothunter.db است (یا از متغیر env: DATABASE_URL)
- مدل‌های دیتابیس در src/database/models.py تعریف شده‌اند
- قبل از هر تغییر در مدل‌ها، migration جدید بسازید و اعمال کنید
- برای اطلاعات بیشتر به مستندات Alembic مراجعه کنید: https://alembic.sqlalchemy.org
