#!/bin/bash

# P24_SlotHunter Comprehensive Server Management Script
# Complete server management for P24 appointment hunter

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/logs/slothunter.log"
PID_FILE="$PROJECT_DIR/slothunter.pid"
ENV_FILE="$PROJECT_DIR/.env"
CONFIG_FILE="$PROJECT_DIR/config/config.yaml"
DB_FILE="$PROJECT_DIR/data/slothunter.db"

# Colors for better display
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Banner display function
show_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎯 P24_SlotHunter                         ║"
    echo "║                  Server Management Panel                     ║"
    echo "║                                                              ║"
    echo "║              Complete P24 Appointment Hunter                 ║"
    echo "║                    Management System                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Logging function
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$PROJECT_DIR/logs/manager.log"
}

# Check service status
check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Service is running (PID: $PID)${NC}"
            return 0
        else
            echo -e "${RED}❌ PID file exists but service is not running${NC}"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo -e "${RED}❌ Service is not running${NC}"
        return 1
    fi
}

# Start service
start_service() {
    echo -e "${BLUE}🚀 Starting P24_SlotHunter service...${NC}"
    
    if check_status > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ Service is already running${NC}"
        return 1
    fi
    
    # Check prerequisites
    if ! check_prerequisites; then
        echo -e "${RED}❌ Prerequisites check failed${NC}"
        return 1
    fi
    
    cd "$PROJECT_DIR"
    
    # Activate virtual environment and run service
    nohup "$VENV_DIR/bin/python" src/main.py > /dev/null 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 3
    
    if check_status > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Service started successfully${NC}"
        log_message "INFO" "Service started successfully"
        return 0
    else
        echo -e "${RED}❌ Failed to start service${NC}"
        log_message "ERROR" "Failed to start service"
        return 1
    fi
}

# Stop service
stop_service() {
    echo -e "${BLUE}🛑 Stopping P24_SlotHunter service...${NC}"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            sleep 2
            
            if ps -p $PID > /dev/null 2>&1; then
                echo -e "${YELLOW}⚠️ Service still running, force killing...${NC}"
                kill -9 $PID
            fi
            
            rm -f "$PID_FILE"
            echo -e "${GREEN}✅ Service stopped successfully${NC}"
            log_message "INFO" "Service stopped successfully"
        else
            echo -e "${YELLOW}⚠️ Service is not running${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}⚠️ PID file not found${NC}"
    fi
}

# Restart service
restart_service() {
    echo -e "${BLUE}🔄 Restarting P24_SlotHunter service...${NC}"
    stop_service
    sleep 2
    start_service
}

# Show logs
show_logs() {
    echo -e "${BLUE}📋 System Logs:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    if [ -f "$LOG_FILE" ]; then
        echo -e "${YELLOW}Last 50 log entries:${NC}"
        echo ""
        tail -n 50 "$LOG_FILE"
    else
        echo -e "${RED}❌ Log file not found${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Monitor live logs
monitor_logs() {
    echo -e "${BLUE}📊 Live Log Monitor (Ctrl+C to exit):${NC}"
    echo -e "${CYAN}═════════════════════════════���══════════${NC}"
    
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}❌ Log file not found${NC}"
        echo -e "${YELLOW}Press Enter to continue...${NC}"
        read
    fi
}

# Show system statistics
show_stats() {
    echo -e "${BLUE}📊 System Statistics:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    # Service status
    echo -e "${YELLOW}🔄 Service Status:${NC}"
    check_status
    echo ""
    
    # File statistics
    echo -e "${YELLOW}📁 File Statistics:${NC}"
    if [ -f "$LOG_FILE" ]; then
        LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
        LOG_LINES=$(wc -l < "$LOG_FILE")
        echo -e "  📋 Log size: ${GREEN}$LOG_SIZE${NC}"
        echo -e "  📝 Log lines: ${GREEN}$LOG_LINES${NC}"
    else
        echo -e "  ${RED}❌ Log file not found${NC}"
    fi
    
    # Database statistics
    if [ -f "$DB_FILE" ]; then
        DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
        echo -e "  💾 Database size: ${GREEN}$DB_SIZE${NC}"
    else
        echo -e "  ${RED}❌ Database file not found${NC}"
    fi
    
    echo ""
    
    # System statistics
    echo -e "${YELLOW}💻 System Resources:${NC}"
    if command -v top >/dev/null 2>&1; then
        CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 2>/dev/null || echo "N/A")
        echo -e "  🖥️ CPU Usage: ${GREEN}${CPU_USAGE}%${NC}"
    fi
    
    if command -v free >/dev/null 2>&1; then
        RAM_USAGE=$(free -h | awk 'NR==2{printf "%.1f%%", $3*100/$2}' 2>/dev/null || echo "N/A")
        echo -e "  💾 RAM Usage: ${GREEN}${RAM_USAGE}${NC}"
    fi
    
    if command -v df >/dev/null 2>&1; then
        DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' 2>/dev/null || echo "N/A")
        echo -e "  💿 Disk Usage: ${GREEN}${DISK_USAGE}${NC}"
    fi
    
    # Project statistics
    echo ""
    echo -e "${YELLOW}📊 Project Statistics:${NC}"
    if [ -f "$VENV_DIR/bin/python" ]; then
        PYTHON_VERSION=$("$VENV_DIR/bin/python" --version 2>&1 | cut -d' ' -f2)
        echo -e "  🐍 Python Version: ${GREEN}${PYTHON_VERSION}${NC}"
    fi
    
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        PACKAGE_COUNT=$(wc -l < "$PROJECT_DIR/requirements.txt")
        echo -e "  📦 Required Packages: ${GREEN}${PACKAGE_COUNT}${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}═════════════════════════════════════��══${NC}"
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Settings menu
settings_menu() {
    while true; do
        show_banner
        echo -e "${PURPLE}⚙️ System Settings:${NC}"
        echo ""
        echo -e "${YELLOW}1.${NC} Set Check Interval"
        echo -e "${YELLOW}2.${NC} Set Log Level"
        echo -e "${YELLOW}3.${NC} View Current Settings"
        echo -e "${YELLOW}4.${NC} Edit Environment File"
        echo -e "${YELLOW}5.${NC} Edit Configuration File"
        echo -e "${YELLOW}6.${NC} Manage User Access"
        echo -e "${YELLOW}7.${NC} Backup Settings"
        echo -e "${YELLOW}8.${NC} Restore Settings"
        echo -e "${YELLOW}0.${NC} Back to Main Menu"
        echo ""
        echo -e -n "${CYAN}Your choice: ${NC}"
        read choice
        
        case $choice in
            1) set_check_interval ;;
            2) set_log_level ;;
            3) show_current_settings ;;
            4) edit_env_file ;;
            5) edit_config_file ;;
            6) manage_user_access ;;
            7) backup_settings ;;
            8) restore_settings ;;
            0) break ;;
            *) echo -e "${RED}❌ Invalid choice${NC}"; sleep 2 ;;
        esac
    done
}

# Set check interval
set_check_interval() {
    echo -e "${BLUE}⏱️ Set Check Interval:${NC}"
    echo ""
    
    # Show current value
    if [ -f "$ENV_FILE" ]; then
        CURRENT=$(grep "CHECK_INTERVAL=" "$ENV_FILE" | cut -d'=' -f2)
        echo -e "Current value: ${GREEN}$CURRENT seconds${NC}"
    fi
    
    echo ""
    echo -e -n "New check interval (seconds): "
    read new_interval
    
    if [[ "$new_interval" =~ ^[0-9]+$ ]] && [ "$new_interval" -gt 0 ]; then
        if [ -f "$ENV_FILE" ]; then
            sed -i "s/CHECK_INTERVAL=.*/CHECK_INTERVAL=$new_interval/" "$ENV_FILE"
        else
            echo "CHECK_INTERVAL=$new_interval" >> "$ENV_FILE"
        fi
        echo -e "${GREEN}✅ Check interval changed to $new_interval seconds${NC}"
        echo -e "${YELLOW}⚠️ Restart service to apply changes${NC}"
        log_message "INFO" "Check interval changed to $new_interval seconds"
    else
        echo -e "${RED}❌ Invalid value${NC}"
    fi
    
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Set log level
set_log_level() {
    echo -e "${BLUE}📝 Set Log Level:${NC}"
    echo ""
    echo -e "${YELLOW}1.${NC} DEBUG (Detailed information)"
    echo -e "${YELLOW}2.${NC} INFO (General information)"
    echo -e "${YELLOW}3.${NC} WARNING (Warning messages)"
    echo -e "${YELLOW}4.${NC} ERROR (Error messages only)"
    echo ""
    echo -e -n "${CYAN}Your choice: ${NC}"
    read choice
    
    case $choice in
        1) LOG_LEVEL="DEBUG" ;;
        2) LOG_LEVEL="INFO" ;;
        3) LOG_LEVEL="WARNING" ;;
        4) LOG_LEVEL="ERROR" ;;
        *) echo -e "${RED}❌ Invalid choice${NC}"; sleep 2; return ;;
    esac
    
    if [ -f "$ENV_FILE" ]; then
        sed -i "s/LOG_LEVEL=.*/LOG_LEVEL=$LOG_LEVEL/" "$ENV_FILE"
    else
        echo "LOG_LEVEL=$LOG_LEVEL" >> "$ENV_FILE"
    fi
    echo -e "${GREEN}✅ Log level changed to $LOG_LEVEL${NC}"
    echo -e "${YELLOW}⚠️ Restart service to apply changes${NC}"
    log_message "INFO" "Log level changed to $LOG_LEVEL"
    
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Show current settings
show_current_settings() {
    echo -e "${BLUE}📋 Current Settings:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    if [ -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}Environment Variables:${NC}"
        BOT_TOKEN=$(grep "TELEGRAM_BOT_TOKEN=" "$ENV_FILE" | cut -d'=' -f2)
        if [ -n "$BOT_TOKEN" ]; then
            echo -e "  📱 Bot Token: ${GREEN}${BOT_TOKEN:0:10}...${NC}"
        fi
        
        ADMIN_ID=$(grep "ADMIN_CHAT_ID=" "$ENV_FILE" | cut -d'=' -f2)
        if [ -n "$ADMIN_ID" ]; then
            echo -e "  👤 Admin Chat ID: ${GREEN}$ADMIN_ID${NC}"
        fi
        
        CHECK_INT=$(grep "CHECK_INTERVAL=" "$ENV_FILE" | cut -d'=' -f2)
        if [ -n "$CHECK_INT" ]; then
            echo -e "  ⏱️ Check Interval: ${GREEN}$CHECK_INT seconds${NC}"
        fi
        
        LOG_LVL=$(grep "LOG_LEVEL=" "$ENV_FILE" | cut -d'=' -f2)
        if [ -n "$LOG_LVL" ]; then
            echo -e "  📝 Log Level: ${GREEN}$LOG_LVL${NC}"
        fi
    else
        echo -e "${RED}❌ Environment file not found${NC}"
    fi
    
    echo ""
    if [ -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}Configuration File:${NC}"
        echo -e "  📄 Config file: ${GREEN}Found${NC}"
        if command -v python3 >/dev/null 2>&1; then
            DOCTOR_COUNT=$(python3 -c "import yaml; print(len(yaml.safe_load(open('$CONFIG_FILE'))['doctors']))" 2>/dev/null || echo "N/A")
            echo -e "  👨‍⚕️ Configured Doctors: ${GREEN}$DOCTOR_COUNT${NC}"
        fi
    else
        echo -e "  📄 Config file: ${RED}Not found${NC}"
    fi
    
    echo -e "${CYAN}══════════════════════════════════��═════${NC}"
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Edit environment file
edit_env_file() {
    echo -e "${BLUE}📝 Edit Environment File:${NC}"
    echo ""
    
    if [ -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}Opening editor...${NC}"
        if command -v nano >/dev/null 2>&1; then
            nano "$ENV_FILE"
        elif command -v vi >/dev/null 2>&1; then
            vi "$ENV_FILE"
        else
            echo -e "${RED}❌ No text editor found${NC}"
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read
            return
        fi
        echo -e "${GREEN}✅ Environment file edited${NC}"
        echo -e "${YELLOW}⚠️ Restart service to apply changes${NC}"
        log_message "INFO" "Environment file edited"
    else
        echo -e "${RED}❌ Environment file not found${NC}"
        echo -e "${YELLOW}Creating new environment file...${NC}"
        create_env_file
    fi
    
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Edit configuration file
edit_config_file() {
    echo -e "${BLUE}📝 Edit Configuration File:${NC}"
    echo ""
    
    if [ -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}Opening editor...${NC}"
        if command -v nano >/dev/null 2>&1; then
            nano "$CONFIG_FILE"
        elif command -v vi >/dev/null 2>&1; then
            vi "$CONFIG_FILE"
        else
            echo -e "${RED}❌ No text editor found${NC}"
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read
            return
        fi
        echo -e "${GREEN}✅ Configuration file edited${NC}"
        echo -e "${YELLOW}⚠️ Restart service to apply changes${NC}"
        log_message "INFO" "Configuration file edited"
    else
        echo -e "${RED}❌ Configuration file not found${NC}"
    fi
    
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Create environment file
create_env_file() {
    echo -e "${BLUE}🔧 Create Environment File:${NC}"
    echo ""
    
    echo -e "${YELLOW}📱 Telegram Bot Setup:${NC}"
    echo "1. Message @BotFather on Telegram"
    echo "2. Send /newbot command"
    echo "3. Enter bot name and username"
    echo "4. Copy the token below"
    echo ""
    
    echo -e -n "🤖 Telegram Bot Token: "
    read bot_token
    
    echo ""
    echo -e "${YELLOW}👤 Admin Chat ID:${NC}"
    echo "Message @userinfobot to get your Chat ID"
    echo ""
    echo -e -n "👤 Your Chat ID: "
    read chat_id
    
    echo -e -n "⏱️ Check interval (seconds) [30]: "
    read check_interval
    check_interval=${check_interval:-30}
    
    echo -e -n "📝 Log level (DEBUG/INFO/WARNING/ERROR) [INFO]: "
    read log_level
    log_level=${log_level:-INFO}
    
    # Create .env file
    cat > "$ENV_FILE" << EOF
# P24_SlotHunter Environment Variables
# Do not commit this file to git!

# Telegram Bot Token (get from @BotFather)
TELEGRAM_BOT_TOKEN=$bot_token

# Admin Chat ID (for receiving reports)
ADMIN_CHAT_ID=$chat_id

# Optional Settings
CHECK_INTERVAL=$check_interval
LOG_LEVEL=$log_level
EOF
    
    echo -e "${GREEN}✅ Environment file created${NC}"
    log_message "INFO" "Environment file created"
}

# Manage user access
manage_user_access() {
    echo -e "${BLUE}🔒 Manage User Access:${NC}"
    echo ""
    echo -e "${YELLOW}This feature will be added in future version${NC}"
    echo -e "${CYAN}Currently use /admin command in Telegram bot${NC}"
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Backup settings
backup_settings() {
    echo -e "${BLUE}💾 Backup Settings:${NC}"
    echo ""
    
    BACKUP_DIR="$PROJECT_DIR/backups"
    BACKUP_FILE="$BACKUP_DIR/settings_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    tar -czf "$BACKUP_FILE" -C "$PROJECT_DIR" .env config/ data/ 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Settings backed up to: $BACKUP_FILE${NC}"
        log_message "INFO" "Settings backed up to $BACKUP_FILE"
    else
        echo -e "${RED}❌ Backup failed${NC}"
        log_message "ERROR" "Settings backup failed"
    fi
    
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Restore settings
restore_settings() {
    echo -e "${BLUE}📥 Restore Settings:${NC}"
    echo ""
    
    BACKUP_DIR="$PROJECT_DIR/backups"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        echo -e "${RED}❌ No backup directory found${NC}"
        echo -e "${YELLOW}Press Enter to continue...${NC}"
        read
        return
    fi
    
    echo -e "${YELLOW}Available backups:${NC}"
    ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null | nl
    
    echo ""
    echo -e -n "Enter backup number to restore (0 to cancel): "
    read backup_num
    
    if [ "$backup_num" = "0" ]; then
        return
    fi
    
    BACKUP_FILE=$(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | sed -n "${backup_num}p")
    
    if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
        echo -e "${YELLOW}⚠️ This will overwrite current settings. Continue? (y/N): ${NC}"
        read confirm
        
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            tar -xzf "$BACKUP_FILE" -C "$PROJECT_DIR"
            echo -e "${GREEN}✅ Settings restored from: $BACKUP_FILE${NC}"
            echo -e "${YELLOW}⚠️ Restart service to apply changes${NC}"
            log_message "INFO" "Settings restored from $BACKUP_FILE"
        fi
    else
        echo -e "${RED}❌ Invalid backup selection${NC}"
    fi
    
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Check prerequisites
check_prerequisites() {
    local errors=0
    
    # Check Python virtual environment
    if [ ! -f "$VENV_DIR/bin/python" ]; then
        echo -e "${RED}❌ Python virtual environment not found${NC}"
        errors=$((errors + 1))
    fi
    
    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}❌ Environment file not found${NC}"
        errors=$((errors + 1))
    fi
    
    # Check configuration file
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}❌ Configuration file not found${NC}"
        errors=$((errors + 1))
    fi
    
    # Check required directories
    for dir in "logs" "data" "config"; do
        if [ ! -d "$PROJECT_DIR/$dir" ]; then
            echo -e "${YELLOW}⚠️ Creating missing directory: $dir${NC}"
            mkdir -p "$PROJECT_DIR/$dir"
        fi
    done
    
    return $errors
}

# Test system
test_system() {
    echo -e "${BLUE}🧪 System Test:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}1. Testing Prerequisites...${NC}"
    if check_prerequisites; then
        echo -e "${GREEN}✅ Prerequisites check passed${NC}"
    else
        echo -e "${RED}❌ Prerequisites check failed${NC}"
    fi
    echo ""
    
    echo -e "${YELLOW}2. Testing Python Dependencies...${NC}"
    if [ -f "$VENV_DIR/bin/python" ]; then
        if "$VENV_DIR/bin/python" -c "import requests, telegram, sqlalchemy, yaml" 2>/dev/null; then
            echo -e "${GREEN}✅ Python dependencies available${NC}"
        else
            echo -e "${RED}❌ Missing Python dependencies${NC}"
        fi
    else
        echo -e "${RED}❌ Python virtual environment not found${NC}"
    fi
    echo ""
    
    echo -e "${YELLOW}3. Testing Configuration...${NC}"
    if [ -f "$ENV_FILE" ] && [ -f "$CONFIG_FILE" ]; then
        echo -e "${GREEN}✅ Configuration files found${NC}"
    else
        echo -e "${RED}❌ Configuration files missing${NC}"
    fi
    echo ""
    
    echo -e "${YELLOW}4. Testing API Connection...${NC}"
    if [ -f "$VENV_DIR/bin/python" ] && [ -f "test_api.py" ]; then
        if "$VENV_DIR/bin/python" test_api.py > /dev/null 2>&1; then
            echo -e "${GREEN}✅ API connection test passed${NC}"
        else
            echo -e "${YELLOW}⚠️ API connection test failed or not available${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ API test script not found${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Setup system
setup_system() {
    echo -e "${BLUE}🔧 System Setup:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    # Run manager.py setup if available
    if [ -f "$PROJECT_DIR/manager.py" ] && [ -f "$VENV_DIR/bin/python" ]; then
        echo -e "${YELLOW}Running automated setup...${NC}"
        "$VENV_DIR/bin/python" manager.py setup
    elif [ -f "$PROJECT_DIR/manager.py" ]; then
        echo -e "${YELLOW}Running setup with system Python...${NC}"
        python3 manager.py setup
    else
        echo -e "${YELLOW}Manual setup required...${NC}"
        
        # Create directories
        for dir in "logs" "data" "config"; do
            mkdir -p "$PROJECT_DIR/$dir"
            echo -e "${GREEN}✅ Created directory: $dir${NC}"
        done
        
        # Create environment file if not exists
        if [ ! -f "$ENV_FILE" ]; then
            create_env_file
        fi
    fi
    
    echo ""
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Main menu
main_menu() {
    while true; do
        show_banner
        
        # Show service status
        echo -e "${YELLOW}📊 Service Status:${NC}"
        check_status
        echo ""
        
        echo -e "${PURPLE}🎛️ Management Menu:${NC}"
        echo ""
        echo -e "${YELLOW}1.${NC} Start Service"
        echo -e "${YELLOW}2.${NC} Stop Service"
        echo -e "${YELLOW}3.${NC} Restart Service"
        echo -e "${YELLOW}4.${NC} View Logs"
        echo -e "${YELLOW}5.${NC} Monitor Live Logs"
        echo -e "${YELLOW}6.${NC} System Statistics"
        echo -e "${YELLOW}7.${NC} Settings"
        echo -e "${YELLOW}8.${NC} Test System"
        echo -e "${YELLOW}9.${NC} Setup System"
        echo -e "${YELLOW}0.${NC} Exit"
        echo ""
        echo -e -n "${CYAN}Your choice: ${NC}"
        read choice
        
        case $choice in
            1) start_service; echo -e "${YELLOW}Press Enter to continue...${NC}"; read ;;
            2) stop_service; echo -e "${YELLOW}Press Enter to continue...${NC}"; read ;;
            3) restart_service; echo -e "${YELLOW}Press Enter to continue...${NC}"; read ;;
            4) show_logs ;;
            5) monitor_logs ;;
            6) show_stats ;;
            7) settings_menu ;;
            8) test_system ;;
            9) setup_system ;;
            0) echo -e "${GREEN}👋 Goodbye!${NC}"; exit 0 ;;
            *) echo -e "${RED}❌ Invalid choice${NC}"; sleep 2 ;;
        esac
    done
}

# Command line interface
if [ $# -gt 0 ]; then
    case $1 in
        start) start_service ;;
        stop) stop_service ;;
        restart) restart_service ;;
        status) check_status ;;
        logs) show_logs ;;
        stats) show_stats ;;
        test) test_system ;;
        setup) setup_system ;;
        *) 
            echo "Usage: $0 [start|stop|restart|status|logs|stats|test|setup]"
            echo "Or run without arguments for interactive menu"
            exit 1
            ;;
    esac
else
    # Check if running as root (optional warning)
    if [ "$EUID" -eq 0 ]; then
        echo -e "${YELLOW}⚠️ Running as root. Consider using a regular user for security.${NC}"
        sleep 2
    fi
    
    # Check if project directory exists
    if [ ! -d "$PROJECT_DIR" ]; then
        echo -e "${RED}❌ Project directory not found: $PROJECT_DIR${NC}"
        exit 1
    fi
    
    # Create log directory if it doesn't exist
    mkdir -p "$PROJECT_DIR/logs"
    
    # Run main menu
    main_menu
fi