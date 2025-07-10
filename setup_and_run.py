#!/usr/bin/env python3
"""
Setup and run script for P24_SlotHunter on Windows
"""
import os
import sys
import subprocess
import venv
from pathlib import Path

def main():
    """Main setup and run function"""
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"
    
    print("🎯 P24_SlotHunter Setup and Run")
    print("=" * 50)
    
    # Check if virtual environment exists
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        try:
            venv.create(venv_path, with_pip=True)
            print("✅ Virtual environment created successfully")
        except Exception as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Get Python executable path
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Linux/Mac
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Install requirements
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        print("📦 Installing requirements...")
        try:
            subprocess.run([str(pip_exe), "install", "-r", str(requirements_file)], check=True)
            print("✅ Requirements installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
    else:
        print("⚠️ No requirements.txt found")
    
    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️ .env file not found")
        print("💡 Please run 'python manager.py setup' first to configure the bot")
        return False
    
    # Run the main application
    print("🚀 Starting P24_SlotHunter...")
    try:
        main_script = project_root / "src" / "main.py"
        subprocess.run([str(python_exe), str(main_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        return True
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)