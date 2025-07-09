#!/bin/bash

# P24_SlotHunter Server Management Script
# مدیریت کامل سرور نوبت‌یاب پذیرش۲۴

PROJECT_DIR="/root/P24_SlotHunter"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/logs/slothunter.log"
PID_FILE="$PROJECT_DIR/slothunter.pid"
ENV_FILE="$PROJECT_DIR/.env"

# رنگ‌ها برای نمایش بهتر
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# تابع نمایش بنر
show_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🎯 P24_SlotHunter                         ║"
    echo "║                  Server Management Panel                     ║"
    echo "║                                                              ║"
    echo "║              مدیریت کامل سرور نوبت‌یاب پذیرش۲۴               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# تابع بررسی وضعیت
check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ سرویس در حال اجرا است (PID: $PID)${NC}"
            return 0
        else
            echo -e "${RED}❌ فایل PID موجود است اما سرویس اجرا نمی‌شود${NC}"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo -e "${RED}❌ سرویس در حال اجرا نیست${NC}"
        return 1
    fi
}

# تابع شروع سرویس
start_service() {
    echo -e "${BLUE}🚀 شروع سرویس P24_SlotHunter...${NC}"
    
    if check_status > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ سرویس در حال حاضر در حال اجرا است${NC}"
        return 1
    fi
    
    cd "$PROJECT_DIR"
    
    # فعال‌سازی virtual environment و اجرای سرویس
    nohup "$VENV_DIR/bin/python" src/main.py > /dev/null 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 3
    
    if check_status > /dev/null 2>&1; then
        echo -e "${GREEN}✅ سرویس با موفقیت شروع شد${NC}"
        return 0
    else
        echo -e "${RED}❌ خطا در شروع سرویس${NC}"
        return 1
    fi
}

# تابع توقف سرویس
stop_service() {
    echo -e "${BLUE}🛑 توقف سرویس P24_SlotHunter...${NC}"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            sleep 2
            
            if ps -p $PID > /dev/null 2>&1; then
                echo -e "${YELLOW}⚠️ سرویس هنوز اجرا می‌شود، force kill...${NC}"
                kill -9 $PID
            fi
            
            rm -f "$PID_FILE"
            echo -e "${GREEN}✅ سرویس متوقف شد${NC}"
        else
            echo -e "${YELLOW}⚠️ سرویس در حال اجرا نیست${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}⚠️ فایل PID یافت نشد${NC}"
    fi
}

# تابع restart سرویس
restart_service() {
    echo -e "${BLUE}🔄 Restart سرویس P24_SlotHunter...${NC}"
    stop_service
    sleep 2
    start_service
}

# تابع نمایش لاگ‌ها
show_logs() {
    echo -e "${BLUE}📋 نمایش لاگ‌های سیستم:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    if [ -f "$LOG_FILE" ]; then
        echo -e "${YELLOW}آخرین 50 خط لاگ:${NC}"
        echo ""
        tail -n 50 "$LOG_FILE"
    else
        echo -e "${RED}❌ فایل لاگ یافت نشد${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}برای خروج Enter فشار دهید...${NC}"
    read
}

# تابع مانیتور لاگ زنده
monitor_logs() {
    echo -e "${BLUE}📊 مانیتور زنده لاگ‌ها (Ctrl+C برای خروج):${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}❌ فایل لاگ یافت نشد${NC}"
        echo -e "${YELLOW}برای خروج Enter فشار دهید...${NC}"
        read
    fi
}

# تابع نمایش آمار
show_stats() {
    echo -e "${BLUE}📊 آمار سیستم:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    # وضعیت سرویس
    echo -e "${YELLOW}🔄 وضعیت سرویس:${NC}"
    check_status
    echo ""
    
    # آمار فایل‌ها
    echo -e "${YELLOW}📁 آمار فایل‌ها:${NC}"
    if [ -f "$LOG_FILE" ]; then
        LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
        LOG_LINES=$(wc -l < "$LOG_FILE")
        echo -e "  📋 اندازه لاگ: ${GREEN}$LOG_SIZE${NC}"
        echo -e "  📝 تعداد خطوط لاگ: ${GREEN}$LOG_LINES${NC}"
    else
        echo -e "  ${RED}❌ فایل لاگ یافت نشد${NC}"
    fi
    
    # آمار دیتابیس
    if [ -f "$PROJECT_DIR/data/slothunter.db" ]; then
        DB_SIZE=$(du -h "$PROJECT_DIR/data/slothunter.db" | cut -f1)
        echo -e "  💾 اندازه دیتابیس: ${GREEN}$DB_SIZE${NC}"
    else
        echo -e "  ${RED}❌ فایل دیتابیس یافت نشد${NC}"
    fi
    
    echo ""
    
    # آمار سیستم
    echo -e "${YELLOW}💻 آمار سیستم:${NC}"
    echo -e "  🖥️ CPU: ${GREEN}$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%${NC}"
    echo -e "  💾 RAM: ${GREEN}$(free -h | awk 'NR==2{printf "%.1f%%", $3*100/$2}')${NC}"
    echo -e "  💿 Disk: ${GREEN}$(df -h / | awk 'NR==2{print $5}')${NC}"
    
    echo ""
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}برای خروج Enter فشار دهید...${NC}"
    read
}

# تابع تنظیمات
settings_menu() {
    while true; do
        show_banner
        echo -e "${PURPLE}⚙️ تنظیمات سیستم:${NC}"
        echo ""
        echo -e "${YELLOW}1.${NC} تنظیم زمان بررسی"
        echo -e "${YELLOW}2.${NC} تنظیم سطح لاگ"
        echo -e "${YELLOW}3.${NC} مشاهده تنظیمات فعلی"
        echo -e "${YELLOW}4.${NC} ویرایش فایل .env"
        echo -e "${YELLOW}5.${NC} تنظیم دسترسی کاربران"
        echo -e "${YELLOW}0.${NC} بازگشت به منوی اصلی"
        echo ""
        echo -e -n "${CYAN}انتخاب شما: ${NC}"
        read choice
        
        case $choice in
            1) set_check_interval ;;
            2) set_log_level ;;
            3) show_current_settings ;;
            4) edit_env_file ;;
            5) manage_user_access ;;
            0) break ;;
            *) echo -e "${RED}❌ انتخاب نامعتبر${NC}"; sleep 2 ;;
        esac
    done
}

# تابع تنظیم زمان بررسی
set_check_interval() {
    echo -e "${BLUE}⏱️ تنظیم زمان بررسی:${NC}"
    echo ""
    
    # نمایش مقدار فعلی
    if [ -f "$ENV_FILE" ]; then
        CURRENT=$(grep "CHECK_INTERVAL=" "$ENV_FILE" | cut -d'=' -f2)
        echo -e "مقدار فعلی: ${GREEN}$CURRENT ثانیه${NC}"
    fi
    
    echo ""
    echo -e -n "زمان بررسی جدید (ثانیه): "
    read new_interval
    
    if [[ "$new_interval" =~ ^[0-9]+$ ]] && [ "$new_interval" -gt 0 ]; then
        sed -i "s/CHECK_INTERVAL=.*/CHECK_INTERVAL=$new_interval/" "$ENV_FILE"
        echo -e "${GREEN}✅ زمان بررسی به $new_interval ثانیه تغییر کرد${NC}"
        echo -e "${YELLOW}⚠️ برای اعمال تغییرات، سرویس را restart کنید${NC}"
    else
        echo -e "${RED}❌ مقدار نامعتبر${NC}"
    fi
    
    echo -e "${YELLOW}برای ادامه Enter فشار دهید...${NC}"
    read
}

# تابع تنظیم سطح لاگ
set_log_level() {
    echo -e "${BLUE}📝 تنظیم سطح لاگ:${NC}"
    echo ""
    echo -e "${YELLOW}1.${NC} DEBUG (جزئیات کامل)"
    echo -e "${YELLOW}2.${NC} INFO (اطلاعات عمومی)"
    echo -e "${YELLOW}3.${NC} WARNING (هشدارها)"
    echo -e "${YELLOW}4.${NC} ERROR (فقط خطاها)"
    echo ""
    echo -e -n "${CYAN}انتخاب شما: ${NC}"
    read choice
    
    case $choice in
        1) LOG_LEVEL="DEBUG" ;;
        2) LOG_LEVEL="INFO" ;;
        3) LOG_LEVEL="WARNING" ;;
        4) LOG_LEVEL="ERROR" ;;
        *) echo -e "${RED}❌ انتخاب نامعتبر${NC}"; sleep 2; return ;;
    esac
    
    sed -i "s/LOG_LEVEL=.*/LOG_LEVEL=$LOG_LEVEL/" "$ENV_FILE"
    echo -e "${GREEN}✅ سطح لاگ به $LOG_LEVEL تغییر کرد${NC}"
    echo -e "${YELLOW}⚠️ برای اعمال تغییرات، سرویس را restart کنید${NC}"
    
    echo -e "${YELLOW}برای ادامه Enter فشار دهید...${NC}"
    read
}

# تابع نمایش تنظیمات فعلی
show_current_settings() {
    echo -e "${BLUE}📋 تنظیمات فعلی:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    if [ -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}📱 Bot Token:${NC} $(grep "TELEGRAM_BOT_TOKEN=" "$ENV_FILE" | cut -d'=' -f2 | cut -c1-10)..."
        echo -e "${YELLOW}👤 Admin Chat ID:${NC} $(grep "ADMIN_CHAT_ID=" "$ENV_FILE" | cut -d'=' -f2)"
        echo -e "${YELLOW}⏱️ Check Interval:${NC} $(grep "CHECK_INTERVAL=" "$ENV_FILE" | cut -d'=' -f2) ثانیه"
        echo -e "${YELLOW}📝 Log Level:${NC} $(grep "LOG_LEVEL=" "$ENV_FILE" | cut -d'=' -f2)"
    else
        echo -e "${RED}❌ فایل .env یافت نشد${NC}"
    fi
    
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}برای خروج Enter فشار دهید...${NC}"
    read
}

# تابع ویرایش فایل .env
edit_env_file() {
    echo -e "${BLUE}📝 ویرایش فایل .env:${NC}"
    echo ""
    
    if [ -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}در حال باز کردن ویرایشگر...${NC}"
        nano "$ENV_FILE"
        echo -e "${GREEN}✅ فایل .env ویرایش شد${NC}"
        echo -e "${YELLOW}⚠️ برای اعمال تغییرات، سرویس را restart کنید${NC}"
    else
        echo -e "${RED}❌ فایل .env یافت نشد${NC}"
    fi
    
    echo -e "${YELLOW}برای ادامه Enter فشار دهید...${NC}"
    read
}

# تابع مدیریت دسترسی کاربران
manage_user_access() {
    echo -e "${BLUE}🔒 مدیریت دسترسی کاربران:${NC}"
    echo ""
    echo -e "${YELLOW}این قابلیت در نسخه آینده اضافه خواهد شد${NC}"
    echo -e "${CYAN}فعلاً از دستور /admin در ربات تلگرام استفاده کنید${NC}"
    echo ""
    echo -e "${YELLOW}برای ادامه Enter فشار دهید...${NC}"
    read
}

# منوی اصلی
main_menu() {
    while true; do
        show_banner
        
        # نمایش وضعیت
        echo -e "${YELLOW}📊 وضعیت سرویس:${NC}"
        check_status
        echo ""
        
        echo -e "${PURPLE}🎛️ منوی مدیریت:${NC}"
        echo ""
        echo -e "${YELLOW}1.${NC} شروع سرویس (Start)"
        echo -e "${YELLOW}2.${NC} توقف سرویس (Stop)"
        echo -e "${YELLOW}3.${NC} راه‌اندازی مجدد (Restart)"
        echo -e "${YELLOW}4.${NC} نمایش لاگ‌ها"
        echo -e "${YELLOW}5.${NC} مانیتور زنده لاگ‌ها"
        echo -e "${YELLOW}6.${NC} آمار سیستم"
        echo -e "${YELLOW}7.${NC} تنظیمات"
        echo -e "${YELLOW}8.${NC} تست سیستم"
        echo -e "${YELLOW}0.${NC} خروج"
        echo ""
        echo -e -n "${CYAN}انتخاب شما: ${NC}"
        read choice
        
        case $choice in
            1) start_service; echo -e "${YELLOW}برای ادامه Enter فشار دهید...${NC}"; read ;;
            2) stop_service; echo -e "${YELLOW}برای ادامه Enter فشار دهید...${NC}"; read ;;
            3) restart_service; echo -e "${YELLOW}برای ادامه Enter فشار دهید...${NC}"; read ;;
            4) show_logs ;;
            5) monitor_logs ;;
            6) show_stats ;;
            7) settings_menu ;;
            8) test_system ;;
            0) echo -e "${GREEN}👋 خداحافظ!${NC}"; exit 0 ;;
            *) echo -e "${RED}❌ انتخاب نامعتبر${NC}"; sleep 2 ;;
        esac
    done
}

# تابع تست سیستم
test_system() {
    echo -e "${BLUE}🧪 تست سیستم P24_SlotHunter:${NC}"
    echo -e "${CYAN}════════════════════════════════════════${NC}"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}1. تست Dependencies...${NC}"
    "$VENV_DIR/bin/python" check_dependencies.py
    echo ""
    
    echo -e "${YELLOW}2. تست تنظیمات...${NC}"
    "$VENV_DIR/bin/python" test_config.py
    echo ""
    
    echo -e "${YELLOW}3. تست API...${NC}"
    "$VENV_DIR/bin/python" test_api.py
    
    echo ""
    echo -e "${CYAN}═══════════════��════════════════════════${NC}"
    echo -e "${YELLOW}برای خروج Enter فشار دهید...${NC}"
    read
}

# بررسی دسترسی root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ این اسکریپت باید با دسترسی root اجرا شود${NC}"
    echo -e "${YELLOW}لطفاً با sudo اجرا کنید: sudo $0${NC}"
    exit 1
fi

# بررسی وجود پروژه
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ پوشه پروژه یافت نشد: $PROJECT_DIR${NC}"
    exit 1
fi

# اجرای منوی اصلی
main_menu