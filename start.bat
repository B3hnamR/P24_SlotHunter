@echo off
echo 🎯 P24_SlotHunter Windows Startup
echo ================================

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.9+ and add it to PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

REM Activate virtual environment and install requirements
echo 📦 Installing/updating requirements...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ���️ .env file not found
    echo 💡 Please run 'python manager.py setup' first to configure the bot
    pause
    exit /b 1
)

REM Run the application
echo 🚀 Starting P24_SlotHunter...
python src\main.py

pause