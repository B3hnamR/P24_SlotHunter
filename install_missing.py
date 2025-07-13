#!/usr/bin/env python3
"""
نصب سریع dependencies گم شده
"""
import subprocess
import sys

def install_package(package):
    """نصب یک package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🔧 Installing Missing Dependencies")
    print("=" * 40)
    
    # لیست packages مورد نیاز
    missing_packages = [
        "beautifulsoup4>=4.12.0",
    ]
    
    success_count = 0
    
    for package in missing_packages:
        print(f"📦 Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
            success_count += 1
        else:
            print(f"❌ Failed to install {package}")
    
    print(f"\n📊 Results: {success_count}/{len(missing_packages)} packages installed")
    
    if success_count == len(missing_packages):
        print("🎉 All missing dependencies installed!")
        print("\n🧪 Testing imports...")
        
        # تست import
        try:
            import bs4
            print("✅ bs4 (BeautifulSoup) import successful")
            
            # تست import پروژه
            sys.path.insert(0, ".")
            from src.telegram_bot.bot import SlotHunterBot
            print("✅ SlotHunterBot import successful")
            
            print("\n🚀 Ready to start service!")
            return True
            
        except Exception as e:
            print(f"❌ Import test failed: {e}")
            return False
    else:
        print("❌ Some packages failed to install")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)