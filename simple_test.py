#!/usr/bin/env python3
"""
تست ساده برای بررسی آمادگی پروژه
این فایل بدون وابستگی خارجی کار می‌کند
"""
import sys
import os
from pathlib import Path

def test_basic_setup():
    """تست اولیه بدون وابستگی"""
    print("🔍 Basic Setup Test")
    print("=" * 40)
    
    # بررسی ساختار پروژه
    project_root = Path(__file__).parent
    required_dirs = ["src", "config", "logs", "data"]
    required_files = ["requirements.txt", ".env", "server_manager.sh"]
    
    print("📁 Checking project structure...")
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ missing")
            return False
    
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} missing")
            return False
    
    # بررسی environment variables
    print("\n⚙️ Checking environment...")
    env_file = project_root / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
            
        if "TELEGRAM_BOT_TOKEN=" in env_content and "your_bot_token_here" not in env_content:
            print("✅ Bot token configured")
        else:
            print("❌ Bot token not configured")
            
        if "ADMIN_CHAT_ID=" in env_content and "your_chat_id_here" not in env_content:
            print("✅ Admin chat ID configured")
        else:
            print("❌ Admin chat ID not configured")
    
    # بررسی virtual environment
    print("\n🐍 Checking virtual environment...")
    venv_path = project_root / "venv"
    if venv_path.exists():
        python_exe = venv_path / "bin" / "python"
        if python_exe.exists():
            print("✅ Virtual environment ready")
        else:
            print("❌ Virtual environment incomplete")
            return False
    else:
        print("❌ Virtual environment not found")
        return False
    
    print("\n🎉 Basic setup looks good!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment: source venv/bin/activate")
    print("2. Run dependency check: python check_dependencies.py")
    print("3. Start service: ./server_manager.sh start")
    
    return True

def test_with_venv():
    """تست با virtual environment"""
    print("\n" + "=" * 40)
    print("🧪 Testing with virtual environment...")
    
    # اضافه کردن مسیر پروژه
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        # تست import های اساسی
        print("📦 Testing core imports...")
        
        # تست yaml (built-in alternative)
        try:
            import yaml
            print("✅ yaml")
        except ImportError:
            print("❌ yaml - install with: pip install pyyaml")
            return False
        
        # تست config
        try:
            from src.utils.config import Config
            print("✅ Config")
        except Exception as e:
            print(f"❌ Config import failed: {e}")
            return False
        
        # تست ایجاد config instance
        try:
            config = Config()
            print("✅ Config instance created")
            
            # نمایش تنظیمات
            print(f"📱 Bot Token: {'Set' if config.telegram_bot_token else 'Not set'}")
            print(f"👤 Admin Chat ID: {config.admin_chat_id}")
            
        except Exception as e:
            print(f"❌ Config creation failed: {e}")
            return False
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    # تست اولیه
    if not test_basic_setup():
        print("\n❌ Basic setup failed")
        sys.exit(1)
    
    # تست با venv (اختیاری)
    try:
        if test_with_venv():
            print("\n✅ System is ready!")
            sys.exit(0)
        else:
            print("\n⚠️ Some issues found, but basic setup is OK")
            sys.exit(0)
    except Exception as e:
        print(f"\n⚠️ Advanced test failed: {e}")
        print("But basic setup is OK - you can proceed with setup")
        sys.exit(0)