import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# اضافه کردن src به مسیر
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# اینجا مدل‌های پروژه را ایمپورت می‌کنیم
from src.database.models import Base  # فقط Base کافی است
from src.utils.config import Config

# این فایل config را می‌خواند
config = context.config

# تنظیم لاگ
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    # خواندن آدرس دیتابیس از config یا env
    cfg = Config()
    db_url = os.getenv('DATABASE_URL') or 'sqlite:///data/slothunter.db'
    return db_url

def run_migrations_offline():
    url = get_url()
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
        url=get_url()
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
