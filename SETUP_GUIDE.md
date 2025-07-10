# 🎯 P24_SlotHunter Setup Guide

Complete setup guide for P24_SlotHunter appointment hunter bot.

## 📋 Prerequisites

- **Python 3.9+** installed and added to PATH
- **Internet connection** for downloading dependencies
- **Telegram Bot Token** (get from @BotFather)

## 🚀 Quick Setup (Recommended)

### Option 1: Automatic Setup
```bash
# Run the quick setup script
python quick_setup.py

# Configure the bot
python manager.py setup

# Start the service
python server_manager.py start
```

### Option 2: Windows Batch File
```bash
# Double-click start.bat or run:
start.bat
```

### Option 3: Manual Setup
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure bot
python manager.py setup

# 5. Run the bot
python src/main.py
```

## ⚙️ Configuration

### 1. Get Telegram Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` command
3. Enter bot name and username
4. Copy the token

### 2. Get Your Chat ID
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your Chat ID

### 3. Configure Environment
Run the setup command and follow the prompts:
```bash
python manager.py setup
```

Or manually create `.env` file:
```env
# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Admin Chat ID (for receiving reports)
ADMIN_CHAT_ID=your_chat_id_here

# Optional Settings
CHECK_INTERVAL=30
LOG_LEVEL=INFO
```

## 🎛️ Service Management

### Using Server Manager (Recommended)
```bash
# Interactive menu
python server_manager.py

# Command line
python server_manager.py start    # Start service
python server_manager.py stop     # Stop service
python server_manager.py restart  # Restart service
python server_manager.py status   # Check status
python server_manager.py logs     # View logs
python server_manager.py stats    # System statistics
```

### Using Manager Script
```bash
python manager.py run              # Run with Telegram bot
python manager.py run --no-telegram # Run without Telegram
python manager.py status           # Show status
python manager.py config           # Reconfigure
```

## 📁 Project Structure

```
P24_SlotHunter/
├── src/                    # Source code
│   ├── main.py            # Main application
│   ├── api/               # API clients
│   ├── database/          # Database models
│   ├── telegram_bot/      # Telegram bot
│   └── utils/             # Utilities
├── config/                # Configuration files
├── logs/                  # Log files
├── data/                  # Database files
├── venv/                  # Virtual environment
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── manager.py            # Project manager
├── server_manager.py     # Service manager
├── quick_setup.py        # Quick setup script
└── start.bat             # Windows startup script
```

## 🔧 Troubleshooting

### Common Issues

#### 1. "Virtual environment not found"
```bash
# Create virtual environment
python quick_setup.py
```

#### 2. "Import errors"
```bash
# Install dependencies
python -m pip install -r requirements.txt
```

#### 3. "Bot token not configured"
```bash
# Configure bot
python manager.py setup
```

#### 4. "Service won't start"
```bash
# Check prerequisites
python server_manager.py test

# View logs
python server_manager.py logs
```

#### 5. "Permission denied" (Linux/Mac)
```bash
# Make scripts executable
chmod +x server_manager.sh
chmod +x manager.py
```

### Testing

#### Test Imports
```bash
python test_imports.py
```

#### Test System
```bash
python server_manager.py test
```

#### Test Configuration
```bash
python manager.py test
```

## 📊 Monitoring

### View Logs
```bash
# Real-time logs
python server_manager.py logs

# Log file location
tail -f logs/slothunter.log
```

### System Statistics
```bash
python server_manager.py stats
```

### Service Status
```bash
python server_manager.py status
```

## 🔄 Updates

### Update Dependencies
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Update packages
pip install -r requirements.txt --upgrade
```

### Update Configuration
```bash
python manager.py config
```

## 🛡️ Security

### Environment Variables
- Never commit `.env` file to git
- Keep bot token secure
- Use restricted access mode for production

### Access Control
```bash
# Configure access control
python manager.py config
```

## 📞 Support

### Getting Help
1. Check this guide first
2. Run system tests: `python server_manager.py test`
3. Check logs: `python server_manager.py logs`
4. Create an issue on GitHub

### Useful Commands
```bash
# Complete system check
python server_manager.py test

# View system statistics
python server_manager.py stats

# Restart service
python server_manager.py restart

# Reconfigure bot
python manager.py setup
```

## 🎯 Next Steps

After successful setup:

1. **Test the bot**: Send `/start` to your bot on Telegram
2. **Add doctors**: Use admin commands to add doctors to monitor
3. **Subscribe**: Subscribe to doctors you want to monitor
4. **Monitor**: Check logs and statistics regularly

## 📝 Notes

- The service runs in the background
- Logs are stored in `logs/slothunter.log`
- Database is stored in `data/slothunter.db`
- Configuration is in `config/config.yaml` and `.env`

---

**Happy hunting! 🎯**