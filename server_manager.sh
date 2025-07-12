#!/bin/bash

# P24_SlotHunter Professional Server Management Script
# Complete automated server management for P24 appointment hunter
# Version: 2.0 - Enhanced with auto-setup and intelligent management

set -uo pipefail  # Exit on undefined vars, pipe failures (but not on command errors)

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/logs/slothunter.log"
MANAGER_LOG="$PROJECT_DIR/logs/manager.log"
PID_FILE="$PROJECT_DIR/slothunter.pid"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"
CONFIG_FILE="$PROJECT_DIR/config/config.yaml"
DB_FILE="$PROJECT_DIR/data/slothunter.db"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
MAIN_SCRIPT="$PROJECT_DIR/src/main.py"
SERVICE_NAME="slothunter"
BACKUP_DIR="$PROJECT_DIR/backups"

# System detection
DISTRO=""
PACKAGE_MANAGER=""
PYTHON_CMD=""

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
    echo "║                    🎯 P24_SlotHunter v2.0                   ║"
    echo "║                Professional Server Manager                   ║"
    echo "║                                                              ║"
    echo "║          Complete P24 Appointment Hunter System             ║"
    echo "║              Auto-Setup & Intelligent Management            ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Enhanced logging function
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_entry="[$timestamp] [$level] $message"
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$MANAGER_LOG")"
    
    # Write to log file
    echo "$log_entry" >> "$MANAGER_LOG"
    
    # Also display based on level
    case $level in
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "WARN") echo -e "${YELLOW}⚠️ $message${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️ $message${NC}" ;;
        *) echo -e "${WHITE}$message${NC}" ;;
    esac
}

# System detection function
detect_system() {
    log_message "INFO" "Detecting system configuration..."
    
    # Detect Linux distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    elif [ -f /etc/redhat-release ]; then
        DISTRO="rhel"
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
    else
        DISTRO="unknown"
    fi
    
    # Detect package manager
    if command -v apt >/dev/null 2>&1; then
        PACKAGE_MANAGER="apt"
    elif command -v yum >/dev/null 2>&1; then
        PACKAGE_MANAGER="yum"
    elif command -v dnf >/dev/null 2>&1; then
        PACKAGE_MANAGER="dnf"
    elif command -v pacman >/dev/null 2>&1; then
        PACKAGE_MANAGER="pacman"
    else
        PACKAGE_MANAGER="unknown"
    fi
    
    # Detect Python command
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1)
        if [ "$PYTHON_VERSION" = "3" ]; then
            PYTHON_CMD="python"
        fi
    fi
    
    log_message "INFO" "System detected: $DISTRO with $PACKAGE_MANAGER package manager"
    log_message "INFO" "Python command: $PYTHON_CMD"
}

# Install system dependencies
install_system_dependencies() {
    log_message "INFO" "Installing system dependencies..."
    
    case $PACKAGE_MANAGER in
        "apt")
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv git curl wget nano htop
            ;;
        "yum")
            sudo yum update -y
            sudo yum install -y python3 python3-pip git curl wget nano htop
            ;;
        "dnf")
            sudo dnf update -y
            sudo dnf install -y python3 python3-pip git curl wget nano htop
            ;;
        "pacman")
            sudo pacman -Syu --noconfirm
            sudo pacman -S --noconfirm python python-pip git curl wget nano htop
            ;;
        *)
            log_message "WARN" "Unknown package manager. Please install dependencies manually:"
            log_message "INFO" "Required: python3, python3-pip, python3-venv, git, curl, wget, nano"
            return 1
            ;;
    esac
    
    log_message "SUCCESS" "System dependencies installed successfully"
}

# Setup Python virtual environment
setup_virtual_environment() {
    log_message "INFO" "Setting up Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        if [ -n "$PYTHON_CMD" ]; then
            $PYTHON_CMD -m venv "$VENV_DIR"
            log_message "SUCCESS" "Virtual environment created"
        else
            log_message "ERROR" "Python 3 not found. Please install Python 3.8+"
            return 1
        fi
    else
        log_message "INFO" "Virtual environment already exists"
    fi
    
    # Activate and upgrade pip
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    
    # Install requirements if file exists
    if [ -f "$REQUIREMENTS_FILE" ]; then
        log_message "INFO" "Installing Python dependencies..."
        pip install -r "$REQUIREMENTS_FILE"
        log_message "SUCCESS" "Python dependencies installed"
    else
        log_message "WARN" "Requirements file not found. Installing basic dependencies..."
        pip install requests python-telegram-bot sqlalchemy pyyaml python-dotenv beautifulsoup4
    fi
    
    deactivate
}

# Create project structure
create_project_structure() {
    log_message "INFO" "Creating project directory structure..."
    
    # Create necessary directories
    local dirs=("logs" "data" "config" "backups" "src")
    for dir in "${dirs[@]}"; do
        if [ ! -d "$PROJECT_DIR/$dir" ]; then
            mkdir -p "$PROJECT_DIR/$dir"
            log_message "INFO" "Created directory: $dir"
        fi
    done
    
    # Create config file if not exists
    if [ ! -f "$CONFIG_FILE" ]; then
        log_message "INFO" "Creating default configuration file..."
        cat > "$CONFIG_FILE" << 'EOF'
# P24_SlotHunter Configuration
telegram:
  bot_token: ${TELEGRAM_BOT_TOKEN}
  admin_chat_id: ${ADMIN_CHAT_ID}

monitoring:
  check_interval: ${CHECK_INTERVAL:30}
  max_retries: 3
  timeout: 10
  days_ahead: 7

logging:
  level: ${LOG_LEVEL:INFO}
  file: logs/slothunter.log
  max_size: 10MB
  backup_count: 5

doctors: []
EOF
        log_message "SUCCESS" "Default configuration file created"
    fi
}

# Setup environment file
setup_environment_file() {
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            log_message "INFO" "Creating environment file from example..."
            cp "$ENV_EXAMPLE" "$ENV_FILE"
        else
            log_message "INFO" "Creating new environment file..."
            cat > "$ENV_FILE" << 'EOF'
# P24_SlotHunter Environment Variables
# Configure these values for your setup

# Telegram Bot Token (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Admin Chat ID (get from @userinfobot)
ADMIN_CHAT_ID=your_chat_id_here

# Optional Settings
CHECK_INTERVAL=30
LOG_LEVEL=INFO
EOF
        fi
        
        chmod 600 "$ENV_FILE"  # Secure permissions
        log_message "SUCCESS" "Environment file created"
        log_message "WARN" "Please edit .env file with your actual values"
        return 1  # Indicate that manual configuration is needed
    fi
    
    return 0
}

# Validate environment configuration
validate_environment() {
    log_message "INFO" "Validating environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        log_message "ERROR" "Environment file not found"
        return 1
    fi
    
    # Check required variables
    local required_vars=("TELEGRAM_BOT_TOKEN" "ADMIN_CHAT_ID")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" "$ENV_FILE" || grep -q "^$var=your_" "$ENV_FILE"; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_message "ERROR" "Missing or unconfigured variables: ${missing_vars[*]}"
        log_message "INFO" "Please edit $ENV_FILE and set proper values"
        return 1
    fi
    
    log_message "SUCCESS" "Environment configuration is valid"
    return 0
}

# Check if service is running
check_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Service is running (PID: $pid)${NC}"
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

# Enhanced service start with better error handling
start_service() {
    log_message "INFO" "Starting P24_SlotHunter service..."
    
    if check_status > /dev/null 2>&1; then
        log_message "WARN" "Service is already running"
        return 1
    fi
    
    # Validate prerequisites
    if ! validate_prerequisites; then
        log_message "ERROR" "Prerequisites validation failed"
        return 1
    fi
    
    # Validate environment
    if ! validate_environment; then
        log_message "ERROR" "Environment validation failed"
        return 1
    fi
    
    cd "$PROJECT_DIR"
    
    # Start service with proper logging
    log_message "INFO" "Activating virtual environment and starting service..."
    
    # Create startup script for better process management
    cat > "$PROJECT_DIR/start_service.sh" << EOF
#!/bin/bash
cd "$PROJECT_DIR"
source "$VENV_DIR/bin/activate"
exec python src/main.py
EOF
    chmod +x "$PROJECT_DIR/start_service.sh"
    
    # Start service in background
    nohup "$PROJECT_DIR/start_service.sh" > "$LOG_FILE" 2>&1 &
    local service_pid=$!
    echo $service_pid > "$PID_FILE"
    
    # Wait and verify startup
    sleep 5
    
    if check_status > /dev/null 2>&1; then
        log_message "SUCCESS" "Service started successfully (PID: $service_pid)"
        return 0
    else
        log_message "ERROR" "Failed to start service"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Enhanced service stop
stop_service() {
    log_message "INFO" "Stopping P24_SlotHunter service..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            # Graceful shutdown
            kill -TERM "$pid"
            sleep 3
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                log_message "WARN" "Service still running, force killing..."
                kill -KILL "$pid"
                sleep 1
            fi
            
            rm -f "$PID_FILE"
            log_message "SUCCESS" "Service stopped successfully"
        else
            log_message "WARN" "Service was not running"
            rm -f "$PID_FILE"
        fi
    else
        log_message "WARN" "PID file not found"
    fi
    
    # Cleanup startup script
    rm -f "$PROJECT_DIR/start_service.sh"
}

# Restart service with update check
restart_service() {
    log_message "INFO" "Restarting P24_SlotHunter service..."
    
    # Check for git updates if in git repository
    if [ -d "$PROJECT_DIR/.git" ]; then
        log_message "INFO" "Checking for updates..."
        cd "$PROJECT_DIR"
        
        # Fetch latest changes
        git fetch origin > /dev/null 2>&1
        
        # Check if updates are available
        local local_commit=$(git rev-parse HEAD)
        local remote_commit=$(git rev-parse origin/main 2>/dev/null || git rev-parse origin/master 2>/dev/null)
        
        if [ "$local_commit" != "$remote_commit" ]; then
            log_message "INFO" "Updates available, pulling latest changes..."
            
            # Backup current .env
            if [ -f "$ENV_FILE" ]; then
                cp "$ENV_FILE" "$ENV_FILE.backup"
            fi
            
            # Pull updates
            git pull origin main 2>/dev/null || git pull origin master 2>/dev/null
            
            # Restore .env if it was overwritten
            if [ -f "$ENV_FILE.backup" ]; then
                if [ -f "$ENV_FILE" ] && ! cmp -s "$ENV_FILE" "$ENV_FILE.backup"; then
                    log_message "INFO" "Restoring environment configuration..."
                    mv "$ENV_FILE.backup" "$ENV_FILE"
                else
                    rm -f "$ENV_FILE.backup"
                fi
            fi
            
            # Update dependencies
            if [ -f "$REQUIREMENTS_FILE" ]; then
                log_message "INFO" "Updating Python dependencies..."
                source "$VENV_DIR/bin/activate"
                pip install -r "$REQUIREMENTS_FILE" --upgrade
                deactivate
            fi
            
            log_message "SUCCESS" "Updates applied successfully"
        else
            log_message "INFO" "No updates available"
        fi
    fi
    
    stop_service
    sleep 2
    start_service
}

# Comprehensive system setup
full_system_setup() {
    log_message "INFO" "Starting comprehensive system setup..."
    
    # Detect system
    detect_system
    
    # Install system dependencies
    if ! command -v python3 >/dev/null 2>&1 || ! command -v git >/dev/null 2>&1; then
        log_message "INFO" "Installing system dependencies..."
        if ! install_system_dependencies; then
            log_message "ERROR" "Failed to install system dependencies"
            return 1
        fi
    fi
    
    # Create project structure
    create_project_structure
    
    # Setup virtual environment
    if ! setup_virtual_environment; then
        log_message "ERROR" "Failed to setup virtual environment"
        return 1
    fi
    
    # Setup environment file
    local env_needs_config=false
    if ! setup_environment_file; then
        env_needs_config=true
    fi
    
    # Setup systemd service if running as root or with sudo
    if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
        setup_systemd_service
    fi
    
    log_message "SUCCESS" "System setup completed successfully"
    
    if [ "$env_needs_config" = true ]; then
        echo ""
        log_message "WARN" "IMPORTANT: Please configure your environment variables:"
        echo -e "${YELLOW}1. Edit $ENV_FILE${NC}"
        echo -e "${YELLOW}2. Set your TELEGRAM_BOT_TOKEN (get from @BotFather)${NC}"
        echo -e "${YELLOW}3. Set your ADMIN_CHAT_ID (get from @userinfobot)${NC}"
        echo -e "${YELLOW}4. Run this script again to start the service${NC}"
        echo ""
    fi
}

# Setup systemd service
setup_systemd_service() {
    log_message "INFO" "Setting up systemd service..."
    
    local service_file="/etc/systemd/system/${SERVICE_NAME}.service"
    local current_user=$(whoami)
    
    if [ "$current_user" = "root" ]; then
        # If running as root, create a dedicated user
        if ! id "$SERVICE_NAME" &>/dev/null; then
            useradd -r -s /bin/false -d "$PROJECT_DIR" "$SERVICE_NAME"
            chown -R "$SERVICE_NAME:$SERVICE_NAME" "$PROJECT_DIR"
            current_user="$SERVICE_NAME"
        fi
    fi
    
    cat > "$service_file" << EOF
[Unit]
Description=P24 SlotHunter Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User=$current_user
Group=$current_user
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/python src/main.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStopSec=30

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    
    log_message "SUCCESS" "Systemd service configured and enabled"
    log_message "INFO" "Use 'sudo systemctl start $SERVICE_NAME' to start via systemd"
}

# Validate all prerequisites
validate_prerequisites() {
    log_message "INFO" "Validating system prerequisites..."
    
    local errors=0
    
    # Check Python virtual environment
    if [ ! -f "$VENV_DIR/bin/python" ]; then
        log_message "ERROR" "Python virtual environment not found"
        errors=$((errors + 1))
    fi
    
    # Check main script
    if [ ! -f "$MAIN_SCRIPT" ]; then
        log_message "ERROR" "Main script not found: $MAIN_SCRIPT"
        errors=$((errors + 1))
    fi
    
    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        log_message "ERROR" "Environment file not found: $ENV_FILE"
        errors=$((errors + 1))
    fi
    
    # Check Python dependencies
    if [ -f "$VENV_DIR/bin/python" ]; then
        local missing_deps=()
        local required_deps=("requests" "telegram" "sqlalchemy" "yaml")
        
        for dep in "${required_deps[@]}"; do
            if ! "$VENV_DIR/bin/python" -c "import $dep" 2>/dev/null; then
                missing_deps+=("$dep")
            fi
        done
        
        if [ ${#missing_deps[@]} -gt 0 ]; then
            log_message "ERROR" "Missing Python dependencies: ${missing_deps[*]}"
            errors=$((errors + 1))
        fi
    fi
    
    # Create missing directories
    local dirs=("logs" "data" "config" "backups")
    for dir in "${dirs[@]}"; do
        if [ ! -d "$PROJECT_DIR/$dir" ]; then
            mkdir -p "$PROJECT_DIR/$dir"
            log_message "INFO" "Created missing directory: $dir"
        fi
    done
    
    if [ $errors -eq 0 ]; then
        log_message "SUCCESS" "All prerequisites validated successfully"
        return 0
    else
        log_message "ERROR" "Prerequisites validation failed with $errors errors"
        return 1
    fi
}

# Enhanced log viewing
show_logs() {
    echo -e "${BLUE}📋 System Logs:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    if [ -f "$LOG_FILE" ]; then
        echo -e "${YELLOW}Application Logs (last 50 entries):${NC}"
        echo ""
        tail -n 50 "$LOG_FILE" | while IFS= read -r line; do
            # Colorize log levels
            if [[ $line == *"ERROR"* ]]; then
                echo -e "${RED}$line${NC}"
            elif [[ $line == *"WARN"* ]]; then
                echo -e "${YELLOW}$line${NC}"
            elif [[ $line == *"INFO"* ]]; then
                echo -e "${BLUE}$line${NC}"
            else
                echo "$line"
            fi
        done
    else
        echo -e "${RED}❌ Application log file not found${NC}"
    fi
    
    echo ""
    if [ -f "$MANAGER_LOG" ]; then
        echo -e "${YELLOW}Manager Logs (last 20 entries):${NC}"
        echo ""
        tail -n 20 "$MANAGER_LOG"
    fi
    
    echo ""
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Monitor live logs with colors
monitor_logs() {
    echo -e "${BLUE}📊 Live Log Monitor (Ctrl+C to exit):${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE" | while IFS= read -r line; do
            # Colorize log levels in real-time
            if [[ $line == *"ERROR"* ]]; then
                echo -e "${RED}$line${NC}"
            elif [[ $line == *"WARN"* ]]; then
                echo -e "${YELLOW}$line${NC}"
            elif [[ $line == *"INFO"* ]]; then
                echo -e "${BLUE}$line${NC}"
            elif [[ $line == *"SUCCESS"* ]]; then
                echo -e "${GREEN}$line${NC}"
            else
                echo "$line"
            fi
        done
    else
        echo -e "${RED}❌ Log file not found${NC}"
        echo -e "${YELLOW}Press Enter to continue...${NC}"
        read
    fi
}

# Enhanced system statistics
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
        local log_size=$(du -h "$LOG_FILE" | cut -f1)
        local log_lines=$(wc -l < "$LOG_FILE")
        echo -e "  📋 Application log: ${GREEN}$log_size ($log_lines lines)${NC}"
    fi
    
    if [ -f "$MANAGER_LOG" ]; then
        local mgr_size=$(du -h "$MANAGER_LOG" | cut -f1)
        local mgr_lines=$(wc -l < "$MANAGER_LOG")
        echo -e "  📋 Manager log: ${GREEN}$mgr_size ($mgr_lines lines)${NC}"
    fi
    
    if [ -f "$DB_FILE" ]; then
        local db_size=$(du -h "$DB_FILE" | cut -f1)
        echo -e "  💾 Database: ${GREEN}$db_size${NC}"
    fi
    
    echo ""
    
    # System resources
    echo -e "${YELLOW}💻 System Resources:${NC}"
    if command -v free >/dev/null 2>&1; then
        local ram_info=$(free -h | awk 'NR==2{printf "Used: %s/%s (%.1f%%)", $3,$2,$3*100/$2}')
        echo -e "  💾 RAM: ${GREEN}$ram_info${NC}"
    fi
    
    if command -v df >/dev/null 2>&1; then
        local disk_info=$(df -h "$PROJECT_DIR" | awk 'NR==2{printf "Used: %s/%s (%s)", $3,$2,$5}')
        echo -e "  💿 Disk: ${GREEN}$disk_info${NC}"
    fi
    
    # Process information
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            local cpu_usage=$(ps -p "$pid" -o %cpu --no-headers 2>/dev/null | tr -d ' ')
            local mem_usage=$(ps -p "$pid" -o %mem --no-headers 2>/dev/null | tr -d ' ')
            echo -e "  🖥️ Service CPU: ${GREEN}${cpu_usage}%${NC}"
            echo -e "  💾 Service RAM: ${GREEN}${mem_usage}%${NC}"
        fi
    fi
    
    echo ""
    
    # Project information
    echo -e "${YELLOW}📊 Project Information:${NC}"
    if [ -f "$VENV_DIR/bin/python" ]; then
        local python_version=$("$VENV_DIR/bin/python" --version 2>&1 | cut -d' ' -f2)
        echo -e "  🐍 Python: ${GREEN}$python_version${NC}"
    fi
    
    if [ -f "$REQUIREMENTS_FILE" ]; then
        local package_count=$(grep -c "^[^#]" "$REQUIREMENTS_FILE" 2>/dev/null || echo "0")
        echo -e "  📦 Dependencies: ${GREEN}$package_count packages${NC}"
    fi
    
    if [ -d "$PROJECT_DIR/.git" ]; then
        local git_branch=$(git -C "$PROJECT_DIR" branch --show-current 2>/dev/null || echo "unknown")
        local git_commit=$(git -C "$PROJECT_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")
        echo -e "  🌿 Git branch: ${GREEN}$git_branch${NC}"
        echo -e "  📝 Git commit: ${GREEN}$git_commit${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Quick health check
health_check() {
    echo -e "${BLUE}🏥 System Health Check:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    local issues=0
    
    # Check service status
    if check_status > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Service is running${NC}"
    else
        echo -e "${RED}❌ Service is not running${NC}"
        issues=$((issues + 1))
    fi
    
    # Check prerequisites
    if validate_prerequisites > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Prerequisites are satisfied${NC}"
    else
        echo -e "${RED}❌ Prerequisites check failed${NC}"
        issues=$((issues + 1))
    fi
    
    # Check environment
    if validate_environment > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Environment is configured${NC}"
    else
        echo -e "${RED}❌ Environment configuration issues${NC}"
        issues=$((issues + 1))
    fi
    
    # Check disk space
    local disk_usage=$(df "$PROJECT_DIR" | awk 'NR==2{print $5}' | sed 's/%//')
    if [ "$disk_usage" -lt 90 ]; then
        echo -e "${GREEN}✅ Disk space is adequate ($disk_usage% used)${NC}"
    else
        echo -e "${RED}❌ Disk space is low ($disk_usage% used)${NC}"
        issues=$((issues + 1))
    fi
    
    # Check log file size
    if [ -f "$LOG_FILE" ]; then
        local log_size_mb=$(du -m "$LOG_FILE" | cut -f1)
        if [ "$log_size_mb" -lt 100 ]; then
            echo -e "${GREEN}✅ Log file size is normal (${log_size_mb}MB)${NC}"
        else
            echo -e "${YELLOW}⚠️ Log file is large (${log_size_mb}MB)${NC}"
        fi
    fi
    
    echo ""
    if [ $issues -eq 0 ]; then
        echo -e "${GREEN}🎉 System health is excellent!${NC}"
    else
        echo -e "${RED}⚠️ Found $issues health issues${NC}"
    fi
    
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Interactive configuration wizard
config_wizard() {
    echo -e "${BLUE}🧙 Configuration Wizard:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    # Backup existing config
    if [ -f "$ENV_FILE" ]; then
        cp "$ENV_FILE" "$ENV_FILE.wizard.backup"
        log_message "INFO" "Backed up existing configuration"
    fi
    
    echo -e "${YELLOW}📱 Telegram Bot Setup:${NC}"
    echo "1. Go to @BotFather on Telegram"
    echo "2. Send /newbot command"
    echo "3. Follow instructions to create your bot"
    echo "4. Copy the token provided"
    echo ""
    
    echo -e -n "🤖 Enter your Telegram Bot Token: "
    read -r bot_token
    
    echo ""
    echo -e "${YELLOW}👤 Admin Chat ID Setup:${NC}"
    echo "1. Message @userinfobot on Telegram"
    echo "2. Copy your Chat ID from the response"
    echo ""
    
    echo -e -n "👤 Enter your Chat ID: "
    read -r chat_id
    
    echo ""
    echo -e -n "⏱️ Check interval in seconds [30]: "
    read -r check_interval
    check_interval=${check_interval:-30}
    
    echo -e -n "📝 Log level (DEBUG/INFO/WARNING/ERROR) [INFO]: "
    read -r log_level
    log_level=${log_level:-INFO}
    
    # Create new .env file
    cat > "$ENV_FILE" << EOF
# P24_SlotHunter Environment Variables
# Generated by Configuration Wizard

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=$bot_token
ADMIN_CHAT_ID=$chat_id

# Application Settings
CHECK_INTERVAL=$check_interval
LOG_LEVEL=$log_level

# Generated on: $(date)
EOF
    
    chmod 600 "$ENV_FILE"
    
    echo ""
    echo -e "${GREEN}✅ Configuration saved successfully!${NC}"
    
    # Validate new configuration
    if validate_environment > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Configuration validation passed${NC}"
        rm -f "$ENV_FILE.wizard.backup"
    else
        echo -e "${RED}❌ Configuration validation failed${NC}"
        echo -e "${YELLOW}Restoring backup...${NC}"
        if [ -f "$ENV_FILE.wizard.backup" ]; then
            mv "$ENV_FILE.wizard.backup" "$ENV_FILE"
        fi
    fi
    
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Main menu with enhanced options
main_menu() {
    while true; do
        show_banner
        
        # Show service status
        echo -e "${YELLOW}📊 Service Status:${NC}"
        check_status
        echo ""
        
        echo -e "${PURPLE}🎛️ Management Menu:${NC}"
        echo ""
        echo -e "${YELLOW} 1.${NC} Start Service"
        echo -e "${YELLOW} 2.${NC} Stop Service"
        echo -e "${YELLOW} 3.${NC} Restart Service (with update check)"
        echo -e "${YELLOW} 4.${NC} View Logs"
        echo -e "${YELLOW} 5.${NC} Monitor Live Logs"
        echo -e "${YELLOW} 6.${NC} System Statistics"
        echo -e "${YELLOW} 7.${NC} Health Check"
        echo -e "${YELLOW} 8.${NC} Configuration Wizard"
        echo -e "${YELLOW} 9.${NC} Full System Setup"
        echo -e "${YELLOW}10.${NC} Update System"
        echo -e "${YELLOW} 0.${NC} Exit"
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
            7) health_check ;;
            8) config_wizard ;;
            9) full_system_setup; echo -e "${YELLOW}Press Enter to continue...${NC}"; read ;;
            10) update_system; echo -e "${YELLOW}Press Enter to continue...${NC}"; read ;;
            0) echo -e "${GREEN}👋 Goodbye!${NC}"; exit 0 ;;
            *) echo -e "${RED}❌ Invalid choice${NC}"; sleep 2 ;;
        esac
    done
}

# Update system function
update_system() {
    log_message "INFO" "Updating system..."
    
    # Update system packages
    case $PACKAGE_MANAGER in
        "apt") sudo apt update && sudo apt upgrade -y ;;
        "yum") sudo yum update -y ;;
        "dnf") sudo dnf update -y ;;
        "pacman") sudo pacman -Syu --noconfirm ;;
    esac
    
    # Update Python dependencies
    if [ -f "$VENV_DIR/bin/python" ] && [ -f "$REQUIREMENTS_FILE" ]; then
        source "$VENV_DIR/bin/activate"
        pip install --upgrade pip
        pip install -r "$REQUIREMENTS_FILE" --upgrade
        deactivate
    fi
    
    log_message "SUCCESS" "System updated successfully"
}

# Command line interface with enhanced options
if [ $# -gt 0 ]; then
    case $1 in
        start) start_service ;;
        stop) stop_service ;;
        restart) restart_service ;;
        status) check_status ;;
        logs) show_logs ;;
        monitor) monitor_logs ;;
        stats) show_stats ;;
        health) health_check ;;
        setup) full_system_setup ;;
        config) config_wizard ;;
        update) update_system ;;
        *) 
            echo "P24_SlotHunter Server Manager v2.0"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start     - Start the service"
            echo "  stop      - Stop the service"
            echo "  restart   - Restart service (with update check)"
            echo "  status    - Show service status"
            echo "  logs      - View application logs"
            echo "  monitor   - Monitor live logs"
            echo "  stats     - Show system statistics"
            echo "  health    - Perform health check"
            echo "  setup     - Run full system setup"
            echo "  config    - Run configuration wizard"
            echo "  update    - Update system and dependencies"
            echo ""
            echo "Run without arguments for interactive menu"
            exit 1
            ;;
    esac
else
    # Initialize logging
    mkdir -p "$(dirname "$MANAGER_LOG")"
    
    # Check if running as root (show warning)
    if [ "$EUID" -eq 0 ]; then
        echo -e "${YELLOW}⚠️ Running as root. Consider using a regular user for security.${NC}"
        sleep 2
    fi
    
    # Detect system on first run
    detect_system
    
    # Check if this is first run (no virtual environment)
    if [ ! -d "$VENV_DIR" ] || [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}🔧 First run detected. Running automatic setup...${NC}"
        sleep 2
        full_system_setup
        echo -e "${YELLOW}Press Enter to continue to main menu...${NC}"
        read
    fi
    
    # Run main menu
    main_menu
fi