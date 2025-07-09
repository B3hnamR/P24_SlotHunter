#!/usr/bin/env python3
"""
Test admin functionality
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.telegram_bot.admin_handlers import TelegramAdminHandlers
from src.utils.config import Config

def test_admin_access():
    """Test admin access functionality"""
    print("🧪 Testing Admin Access...")
    
    # Load config
    config = Config()
    admin_chat_id = config.admin_chat_id
    
    print(f"📋 Admin Chat ID from config: {admin_chat_id}")
    print(f"📋 Admin Chat ID type: {type(admin_chat_id)}")
    
    # Test admin check
    if admin_chat_id:
        is_admin = TelegramAdminHandlers.is_admin(int(admin_chat_id))
        print(f"✅ Admin check result: {is_admin}")
    else:
        print("❌ No admin chat ID configured")
    
    # Test with your actual ID
    test_id = 262182607
    is_admin_test = TelegramAdminHandlers.is_admin(test_id)
    print(f"✅ Test ID {test_id} admin check: {is_admin_test}")

if __name__ == "__main__":
    test_admin_access()