"""
مدل‌های دیتابیس SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """مدل کاربر تلگرام"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(50))
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"
    
    @property
    def full_name(self):
        """نام کامل کاربر"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.username or str(self.telegram_id)


class Doctor(Base):
    """مدل دکتر"""
    __tablename__ = 'doctors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    center_id = Column(String(100), nullable=False)
    service_id = Column(String(100), nullable=False)
    user_center_id = Column(String(100), nullable=False)
    terminal_id = Column(String(100), nullable=False)
    specialty = Column(String(100))
    center_name = Column(String(200))
    center_address = Column(Text)
    center_phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    subscriptions = relationship("Subscription", back_populates="doctor", cascade="all, delete-orphan")
    appointment_logs = relationship("AppointmentLog", back_populates="doctor", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Doctor(name={self.name}, slug={self.slug})>"
    
    @property
    def subscription_count(self):
        """تعداد مشترکین فعال"""
        return len([sub for sub in self.subscriptions if sub.is_active])


class Subscription(Base):
    """مدل اشتراک کاربر در دکتر"""
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    user = relationship("User", back_populates="subscriptions")
    doctor = relationship("Doctor", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(user_id={self.user_id}, doctor_id={self.doctor_id})>"


class AppointmentLog(Base):
    """لاگ نوبت‌های پیدا شده"""
    __tablename__ = 'appointment_logs'
    
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    appointment_date = Column(DateTime, nullable=False)  # تاریخ نوبت
    appointment_count = Column(Integer, default=1)  # تعداد نوبت‌های پیدا شده
    notified_users = Column(Integer, default=0)  # تعداد کاربران اطلاع‌رسانی شده
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    doctor = relationship("Doctor", back_populates="appointment_logs")
    
    def __repr__(self):
        return f"<AppointmentLog(doctor_id={self.doctor_id}, date={self.appointment_date})>"
