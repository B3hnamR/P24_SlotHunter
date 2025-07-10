#!/bin/bash

# P24_SlotHunter Virtual Environment Setup Script
# This script creates the virtual environment and installs dependencies

echo "🎯 P24_SlotHunter Virtual Environment Setup"
echo "=========================================="

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3 first"
    exit 1
fi

echo -e "${BLUE}🐍 Python version:${NC}"
python3 --version

# Create virtual environment
echo -e "${BLUE}📦 Creating virtual environment...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}⚠️ Virtual environment already exists. Removing old one...${NC}"
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${RED}❌ Failed to create virtual environment${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo -e "${BLUE}📦 Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    echo -e "${BLUE}📦 Installing requirements...${NC}"
    pip install -r "$PROJECT_DIR/requirements.txt"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Requirements installed successfully${NC}"
    else
        echo -e "${RED}❌ Failed to install some requirements${NC}"
        echo -e "${YELLOW}⚠️ Continuing anyway...${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ requirements.txt not found${NC}"
fi

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
for dir in "logs" "data" "config"; do
    mkdir -p "$PROJECT_DIR/$dir"
    echo -e "${GREEN}✅ Created $dir/ directory${NC}"
done

# Check for .env file
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️ .env file not found${NC}"
    echo -e "${BLUE}💡 Next steps:${NC}"
    echo "   1. Copy .env.example to .env"
    echo "   2. Edit .env with your bot token"
    echo "   3. Run: ./server_manager.sh start"
    
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        echo -e "${YELLOW}📋 Copying .env.example to .env...${NC}"
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        echo -e "${GREEN}✅ .env file created from example${NC}"
        echo -e "${YELLOW}⚠️ Please edit .env file with your settings${NC}"
    fi
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Test the installation
echo -e "${BLUE}🧪 Testing installation...${NC}"
python -c "import requests, telegram, sqlalchemy, yaml; print('✅ All main dependencies imported successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Installation test passed${NC}"
else
    echo -e "${YELLOW}⚠️ Some dependencies might be missing, but basic setup is complete${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Virtual environment setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo -e "   Virtual environment: ${GREEN}$VENV_DIR${NC}"
echo -e "   Python executable: ${GREEN}$VENV_DIR/bin/python${NC}"
echo -e "   Pip executable: ${GREEN}$VENV_DIR/bin/pip${NC}"
echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo "   1. Edit .env file if needed"
echo "   2. Run: ./server_manager.sh start"
echo "   3. Or use: ./server_manager.sh (for interactive menu)"
echo ""
echo "=========================================="