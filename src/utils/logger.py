"""
تنظیم سیستم لاگ
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "SlotHunter",
    level: str = "INFO",
    log_file: Optional[str] = None,
    max_size: str = "10MB",
    backup_count: int = 5
) -> logging.Logger:
    """
    تنظیم logger برای پروژه
    
    Args:
        name: نام logger
        level: سطح لاگ (DEBUG, INFO, WARNING, ERROR)
        log_file: مسیر فایل لاگ
        max_size: حداکثر اندازه فایل لاگ
        backup_count: تعداد فایل‌های backup
    
    Returns:
        logger تنظیم شده
    """
    
    # تبدیل سطح لاگ
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # ایجاد logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # جلوگیری از duplicate handlers
    if logger.handlers:
        return logger
    
    # فرمت لاگ
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (اختیاری)
    if log_file:
        # ایجاد پوشه لاگ در صورت عدم وجود
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # تبدیل اندازه فایل
        size_bytes = _parse_size(max_size)
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=size_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def _parse_size(size_str: str) -> int:
    """تبدیل رشته اندازه به بایت"""
    size_str = size_str.upper().strip()
    
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        # فرض بر بایت
        return int(size_str)


def get_logger(name: str) -> logging.Logger:
    """دریافت logger موجود"""
    return logging.getLogger(f"SlotHunter.{name}")