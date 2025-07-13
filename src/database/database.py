"""
مدیریت دیتابیس
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from .models import Base
from src.utils.logger import get_logger

logger = get_logger("Database")


from src.utils.config import Config

class DatabaseManager:
    """مدیر دیتابیس"""
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            # خواندن از کانفیگ
            database_url = Config().database_url
        
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
    
    async def _setup_database(self):
        """تنظیم دیتابیس"""
        try:
            # ایجاد پوشه data در صورت عدم وجود
            if self.database_url.startswith("sqlite+aiosqlite:///"):
                from pathlib import Path
                db_path = Path(self.database_url.replace("sqlite+aiosqlite:///", "")).resolve()
                db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ایجاد engine
            self.engine = create_async_engine(
                self.database_url,
                echo=False,  # تغییر به True برای debug
            )
            
            # ایجاد session factory
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            # ایجاد جداول
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info(f"✅ دیتابیس با موفقیت راه‌اندازی شد: {self.database_url}")
            
        except Exception as e:
            logger.error(f"❌ خطا در راه‌اندازی دیتابیس: {e}")
            raise
    
    def get_session(self) -> AsyncSession:
        """دریافت session جدید"""
        if self.SessionLocal is None:
            raise RuntimeError("دیتابیس راه‌اندازی نشده است")
        return self.SessionLocal()
    
    @asynccontextmanager
    async def session_scope(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager برای session"""
        session = self.get_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def close(self):
        """بستن اتصال دیتابیس"""
        if self.engine:
            await self.engine.dispose()
            logger.info("🔒 اتصال دیتابیس بسته شد")


@asynccontextmanager
async def db_session(db_manager: DatabaseManager) -> AsyncGenerator[AsyncSession, None]:
    """Context manager برای session دیتابیس"""
    async with db_manager.session_scope() as session:
        yield session