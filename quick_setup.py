#!/usr/bin/env python3
"""
Quick setup script for P24_SlotHunter
Creates virtual environment and installs dependencies
"""
import os
import sys
import subprocess
import venv
from pathlib import Path

def main():
    """Main setup function"""
    print("🎯 P24_SlotHunter Quick Setup")
    print("=" * 40)
    
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"
    
    # Step 1: Create virtual environment
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        try:
            venv.create(venv_path, with_pip=True)
            print("✅ Virtual environment created")
        except Exception as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Step 2: Get Python executable
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Linux/Mac
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Step 3: Upgrade pip
    print("📦 Upgrading pip...")
    try:
        subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
        print("✅ Pip upgraded")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to upgrade pip: {e}")
    
    # Step 4: Install requirements
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        print("📦 Installing requirements...")
        try:
            subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
            print("✅ Requirements installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
    else:
        print("⚠️ No requirements.txt found")
    
    # Step 5: Create necessary directories
    print("📁 Creating directories...")
    for dir_name in ["logs", "data", "config"]:
        dir_path = project_root / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created {dir_name}/ directory")
    
    # Step 6: Check for .env file
    env_file = project_root / ".env"
    if not env_file.exists():
        print("\n⚠️ .env file not found!")
        print("💡 Next steps:")
        print("   1. Run: python manager.py setup")
        print("   2. Or manually create .env file with your bot token")
        print("   3. Then run: python server_manager.py start")
    else:
        print("✅ .env file exists")
        print("\n🚀 Setup complete!")
        print("💡 You can now run: python server_manager.py start")
    
    print("\n" + "=" * 40)
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    input("Press Enter to exit...")