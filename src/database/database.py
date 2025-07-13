"""
مدیریت دیتابیس
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator

from .models import Base
from src.utils.logger import get_logger

logger = get_logger("Database")


class DatabaseManager:
    """مدیر دیتابیس"""
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            # SQLite پیش‌فرض
            database_url = "sqlite:///data/slothunter.db"
        
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        
        self._setup_database()
    
    def _setup_database(self):
        """تنظیم دیتابیس"""
        try:
            # ایجاد پوشه data در صورت عدم وجود
            if self.database_url.startswith("sqlite:///"):
                from pathlib import Path
                db_path = Path(self.database_url.replace("sqlite:///", "")).resolve()
                db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ایجاد engine
            self.engine = create_engine(
                self.database_url,
                echo=False,  # تغییر به True برای debug
                pool_pre_ping=True
            )
            
            # ایجاد session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # ایجاد جداول
            Base.metadata.create_all(bind=self.engine)
            
            logger.info(f"✅ دیتابیس با موفقیت راه‌اندازی شد: {self.database_url}")
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی دیتابیس: {e}")
            raise
    
    def _get_session(self) -> Session:
        """دریافت session جدید (متد داخلی)"""
        if self.SessionLocal is None:
            raise RuntimeError("دیتابیس راه‌اندازی نشده است")
        return self.SessionLocal()

    @contextmanager
    def _session_scope(self) -> Generator[Session, None, None]:
        """Context manager برای session (متد داخلی)"""
        session = self._get_session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            logger.error("❌ خطای دیتابیس رخ داد. Rollback انجام شد.")
            raise
        finally:
            session.close()
    
    def close(self):
        """بستن اتصال دیتابیس"""
        if self.engine:
            self.engine.dispose()
            logger.info("🔒 اتصال دیتابیس بسته شد")


# Instance سراسری
_db_manager = None


def init_database(database_url: str = None) -> DatabaseManager:
    """راه‌اندازی دیتابیس"""
    global _db_manager
    _db_manager = DatabaseManager(database_url)
    return _db_manager


def get_db_manager() -> DatabaseManager:
    """دریافت مدیر دیتابیس"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager برای session دیتابیس"""
    with get_db_manager()._session_scope() as session:
        yield session