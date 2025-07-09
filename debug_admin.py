#!/usr/bin/env python3
"""
Debug admin functionality
"""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from src.utils.config import Config
from src.telegram_bot.admin_handlers import TelegramAdminHandlers

async def debug_admin():
    """Debug admin functionality"""
    print("🔍 Debugging Admin Functionality...")
    
    # Test config loading
    try:
        config = Config()
        print(f"✅ Config loaded successfully")
        print(f"📋 Bot Token: {config.telegram_bot_token[:10]}...")
        print(f"📋 Admin Chat ID: {config.admin_chat_id}")
        print(f"📋 Admin Chat ID Type: {type(config.admin_chat_id)}")
    except Exception as e:
        print(f"❌ Config loading error: {e}")
        return
    
    # Test admin check
    test_user_id = 262182607
    try:
        is_admin = TelegramAdminHandlers.is_admin(test_user_id)
        print(f"✅ Admin check for {test_user_id}: {is_admin}")
    except Exception as e:
        print(f"❌ Admin check error: {e}")
    
    # Test with different user ID
    test_user_id_2 = 123456789
    try:
        is_admin_2 = TelegramAdminHandlers.is_admin(test_user_id_2)
        print(f"✅ Admin check for {test_user_id_2}: {is_admin_2}")
    except Exception as e:
        print(f"❌ Admin check error for test user: {e}")

if __name__ == "__main__":
    asyncio.run(debug_admin())