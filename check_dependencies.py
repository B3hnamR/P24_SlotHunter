#!/usr/bin/env python3
"""
بررسی و نصب dependencies مورد نیاز
"""
import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """بررسی نسخه پایتون"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_venv():
    """بررسی virtual environment"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found")
        return False
    
    # بررسی فعال بودن venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
        return True
    else:
        print("⚠️ Virtual environment exists but not activated")
        return False

def check_module(module_name, package_name=None):
    """بررسی وجود ماژول"""
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError:
        print(f"❌ {module_name} not found")
        return False

def install_requirements():
    """نصب requirements"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        return False

def create_venv():
    """ایجاد virtual environment"""
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🔍 P24_SlotHunter Dependency Checker")
    print("=" * 50)
    
    # بررسی پایتون
    if not check_python_version():
        sys.exit(1)
    
    # بررسی virtual environment
    venv_exists = Path("venv").exists()
    venv_active = check_venv()
    
    if not venv_exists:
        print("\n📦 Creating virtual environment...")
        if create_venv():
            print("✅ Virtual environment created")
            print("⚠️ Please activate it and run this script again:")
            print("   source venv/bin/activate")
            print("   python check_dependencies.py")
            sys.exit(0)
        else:
            print("❌ Failed to create virtual environment")
            sys.exit(1)
    
    if not venv_active:
        print("\n⚠️ Please activate virtual environment:")
        print("   source venv/bin/activate")
        print("   python check_dependencies.py")
        sys.exit(1)
    
    # بررسی ماژول‌های ضروری
    print("\n📦 Checking core modules...")
    required_modules = [
        "yaml",
        "dotenv", 
        "pydantic",
        "httpx",
        "telegram",
        "sqlalchemy",
        "aiosqlite",
        "bs4"
    ]
    
    missing_modules = []
    for module in required_modules:
        if not check_module(module):
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
        print("📦 Installing requirements...")
        if install_requirements():
            print("✅ Requirements installed successfully")
        else:
            print("❌ Failed to install requirements")
            sys.exit(1)
    else:
        print("\n✅ All required modules are available")
    
    # تست import پروژه
    print("\n🧪 Testing project imports...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.utils.config import Config
        from src.api.models import Doctor
        print("✅ Project imports successful")
        
        # تست config
        config = Config()
        print("✅ Configuration loaded")
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        sys.exit(1)
    
    print("\n🎉 All dependencies are ready!")
    print("\n🚀 You can now run:")
    print("   ./server_manager.sh start")

if __name__ == "__main__":
    main()