#!/usr/bin/env python3
"""
Test script to check for import errors
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing imports...")
    
    # Test basic imports
    print("✓ Testing basic imports...")
    from src.utils.config import Config
    from src.utils.logger import setup_logger
    
    # Test database imports
    print("✓ Testing database imports...")
    from src.database.database import init_database, db_session
    from src.database.models import User, Doctor, Subscription, AppointmentLog
    
    # Test API imports
    print("✓ Testing API imports...")
    from src.api.paziresh_client import PazireshAPI
    from src.api.models import Appointment
    
    # Test telegram bot imports
    print("✓ Testing telegram bot imports...")
    from src.telegram_bot.bot import SlotHunterBot
    from src.telegram_bot.handlers import TelegramHandlers
    from src.telegram_bot.menu_handlers import MenuHandlers
    from src.telegram_bot.callback_handlers import CallbackHandlers
    from src.telegram_bot.messages import MessageFormatter
    
    # Test main module
    print("✓ Testing main module...")
    from src.main import SlotHunter
    
    print("\n✅ All imports successful!")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    sys.exit(1)