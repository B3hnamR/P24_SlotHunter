#!/bin/bash

# P24_SlotHunter Server Fix Script
# حل مشکلات سرور و راه‌اندازی کامل

echo "🔧 P24_SlotHunter Server Fix Script"
echo "=================================="

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📁 Project Directory: $PROJECT_DIR${NC}"

# Step 1: Create .env file
echo -e "${BLUE}🔧 Step 1: Creating .env file...${NC}"
if [ ! -f "$PROJECT_DIR/.env" ]; then
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        echo -e "${YELLOW}📋 Copying .env.example to .env...${NC}"
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        
        # Update with actual values
        cat > "$PROJECT_DIR/.env" << 'EOF'
# متغیرهای محیطی P24_SlotHunter
# این فایل را در git commit نکنید!

# توکن ربات تلگرام (از @BotFather دریافت کنید)
TELEGRAM_BOT_TOKEN=7651903765:AAFV0zI_iSIAh7UvNWYN_UM0xRD-SY2YbtU

# شناسه چت ادمین (برای دریافت گزارش‌ها)
ADMIN_CHAT_ID=262182607

# تنظیمات اختیاری
CHECK_INTERVAL=30
LOG_LEVEL=INFO
EOF
        echo -e "${GREEN}✅ .env file created with your settings${NC}"
    else
        echo -e "${RED}❌ .env.example not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Step 2: Check virtual environment
echo -e "${BLUE}🔧 Step 2: Checking virtual environment...${NC}"
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv "$PROJECT_DIR/venv"
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
fi

# Step 3: Install dependencies
echo -e "${BLUE}🔧 Step 3: Installing dependencies...${NC}"
source "$PROJECT_DIR/venv/bin/activate"
pip install --upgrade pip
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    pip install -r "$PROJECT_DIR/requirements.txt"
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
fi

# Step 4: Create necessary directories
echo -e "${BLUE}🔧 Step 4: Creating directories...${NC}"
for dir in "logs" "data" "config"; do
    mkdir -p "$PROJECT_DIR/$dir"
    echo -e "${GREEN}✅ Created $dir/ directory${NC}"
done

# Step 5: Check config file
echo -e "${BLUE}🔧 Step 5: Checking config file...${NC}"
if [ ! -f "$PROJECT_DIR/config/config.yaml" ]; then
    echo -e "${YELLOW}📋 Creating basic config.yaml...${NC}"
    cat > "$PROJECT_DIR/config/config.yaml" << 'EOF'
# P24_SlotHunter Configuration
app:
  name: "P24_SlotHunter"
  version: "1.0.0"
  debug: false

telegram:
  check_interval: 30
  max_retries: 3

database:
  url: "sqlite:///data/slothunter.db"
  echo: false

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
doctors: []
EOF
    echo -e "${GREEN}✅ Basic config.yaml created${NC}"
else
    echo -e "${GREEN}✅ config.yaml exists${NC}"
fi

# Step 6: Test imports
echo -e "${BLUE}🔧 Step 6: Testing imports...${NC}"
cd "$PROJECT_DIR"
python3 -c "
try:
    from src.telegram_bot.decorators import admin_required, user_required
    print('✅ Decorators import successful')
except ImportError as e:
    print(f'❌ Decorators import failed: {e}')

try:
    from src.telegram_bot.bot import SlotHunterBot
    print('✅ Bot import successful')
except ImportError as e:
    print(f'❌ Bot import failed: {e}')

try:
    import requests, telegram, sqlalchemy, yaml
    print('✅ All dependencies available')
except ImportError as e:
    print(f'❌ Missing dependencies: {e}')
"

# Step 7: Set permissions
echo -e "${BLUE}🔧 Step 7: Setting permissions...${NC}"
chmod +x "$PROJECT_DIR/server_manager.sh"
chmod +x "$PROJECT_DIR/test_paths.sh"
echo -e "${GREEN}✅ Permissions set${NC}"

# Step 8: Final test
echo -e "${BLUE}🔧 Step 8: Final test...${NC}"
if [ -f "$PROJECT_DIR/.env" ] && [ -d "$PROJECT_DIR/venv" ] && [ -f "$PROJECT_DIR/config/config.yaml" ]; then
    echo -e "${GREEN}🎉 All prerequisites are ready!${NC}"
    echo ""
    echo -e "${BLUE}🚀 Next steps:${NC}"
    echo "   1. ./server_manager.sh start"
    echo "   2. Or: python3 manager.py run"
    echo ""
    echo -e "${BLUE}📋 Available commands:${NC}"
    echo "   ./server_manager.sh        - Interactive menu"
    echo "   ./server_manager.sh start  - Start service"
    echo "   ./server_manager.sh status - Check status"
    echo "   ./server_manager.sh logs   - View logs"
    echo ""
else
    echo -e "${RED}❌ Some prerequisites are still missing${NC}"
    exit 1
fi

echo "=================================="
echo -e "${GREEN}🎯 Server fix completed successfully!${NC}"