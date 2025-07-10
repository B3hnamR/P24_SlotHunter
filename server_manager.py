#!/usr/bin/env python3
"""
P24_SlotHunter Windows Server Management Script
Cross-platform server management for P24 appointment hunter
"""
import os
import sys
import subprocess
import signal
import time
import psutil
from pathlib import Path
import json

class P24ServerManager:
    """P24_SlotHunter Server Manager"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.venv_dir = self.project_dir / "venv"
        self.log_file = self.project_dir / "logs" / "slothunter.log"
        self.pid_file = self.project_dir / "slothunter.pid"
        self.env_file = self.project_dir / ".env"
        self.config_file = self.project_dir / "config" / "config.yaml"
        self.db_file = self.project_dir / "data" / "slothunter.db"
        
        # Create necessary directories
        self.log_file.parent.mkdir(exist_ok=True)
        self.db_file.parent.mkdir(exist_ok=True)
        
    def show_banner(self):
        """Display banner"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    🎯 P24_SlotHunter                         ║")
        print("║                  Server Management Panel                     ║")
        print("║                                                              ║")
        print("║              Complete P24 Appointment Hunter                 ║")
        print("║                    Management System                         ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
    
    def get_python_executable(self):
        """Get Python executable path"""
        if os.name == 'nt':  # Windows
            return self.venv_dir / "Scripts" / "python.exe"
        else:  # Linux/Mac
            return self.venv_dir / "bin" / "python"
    
    def check_status(self):
        """Check service status"""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    if process.is_running():
                        print(f"✅ Service is running (PID: {pid})")
                        return True
                    else:
                        print("❌ PID file exists but service is not running")
                        self.pid_file.unlink()
                        return False
                else:
                    print("❌ PID file exists but process not found")
                    self.pid_file.unlink()
                    return False
            except (ValueError, FileNotFoundError, psutil.NoSuchProcess):
                print("❌ Invalid PID file")
                if self.pid_file.exists():
                    self.pid_file.unlink()
                return False
        else:
            print("❌ Service is not running")
            return False
    
    def start_service(self):
        """Start service"""
        print("🚀 Starting P24_SlotHunter service...")
        
        if self.check_status():
            print("⚠️ Service is already running")
            return False
        
        if not self.check_prerequisites():
            print("❌ Prerequisites check failed")
            return False
        
        try:
            python_exe = self.get_python_executable()
            main_script = self.project_dir / "src" / "main.py"
            
            # Start the process
            if os.name == 'nt':  # Windows
                process = subprocess.Popen(
                    [str(python_exe), str(main_script)],
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:  # Linux/Mac
                process = subprocess.Popen(
                    [str(python_exe), str(main_script)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setsid
                )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait a moment and check if it's still running
            time.sleep(3)
            
            if self.check_status():
                print("✅ Service started successfully")
                return True
            else:
                print("❌ Failed to start service")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start service: {e}")
            return False
    
    def stop_service(self):
        """Stop service"""
        print("🛑 Stopping P24_SlotHunter service...")
        
        if not self.pid_file.exists():
            print("⚠️ PID file not found")
            return True
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                
                # Try graceful shutdown first
                if os.name == 'nt':  # Windows
                    process.terminate()
                else:  # Linux/Mac
                    process.send_signal(signal.SIGTERM)
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except psutil.TimeoutExpired:
                    print("⚠️ Service still running, force killing...")
                    process.kill()
                
                print("✅ Service stopped successfully")
            else:
                print("⚠️ Service is not running")
            
            # Remove PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            return True
            
        except (ValueError, FileNotFoundError, psutil.NoSuchProcess) as e:
            print(f"❌ Error stopping service: {e}")
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
    
    def restart_service(self):
        """Restart service"""
        print("🔄 Restarting P24_SlotHunter service...")
        self.stop_service()
        time.sleep(2)
        return self.start_service()
    
    def show_logs(self):
        """Show logs"""
        print("📋 System Logs:")
        print("=" * 40)
        
        if self.log_file.exists():
            print("Last 50 log entries:")
            print()
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-50:]:
                        print(line.rstrip())
            except Exception as e:
                print(f"❌ Error reading log file: {e}")
        else:
            print("❌ Log file not found")
        
        print()
        print("=" * 40)
        input("Press Enter to continue...")
    
    def show_stats(self):
        """Show system statistics"""
        print("📊 System Statistics:")
        print("=" * 40)
        
        # Service status
        print("🔄 Service Status:")
        self.check_status()
        print()
        
        # File statistics
        print("📁 File Statistics:")
        if self.log_file.exists():
            log_size = self.log_file.stat().st_size
            print(f"  📋 Log size: {log_size / 1024:.1f} KB")
            
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    log_lines = sum(1 for _ in f)
                print(f"  📝 Log lines: {log_lines}")
            except:
                print("  📝 Log lines: Unable to count")
        else:
            print("  ❌ Log file not found")
        
        if self.db_file.exists():
            db_size = self.db_file.stat().st_size
            print(f"  💾 Database size: {db_size / 1024:.1f} KB")
        else:
            print("  ❌ Database file not found")
        
        print()
        
        # System statistics
        print("💻 System Resources:")
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            print(f"  🖥️ CPU Usage: {cpu_percent}%")
            print(f"  💾 RAM Usage: {memory.percent}%")
            print(f"  💿 Disk Usage: {disk.percent}%")
        except Exception as e:
            print(f"  ❌ Unable to get system stats: {e}")
        
        # Project statistics
        print()
        print("📊 Project Statistics:")
        python_exe = self.get_python_executable()
        if python_exe.exists():
            try:
                result = subprocess.run([str(python_exe), "--version"], 
                                      capture_output=True, text=True)
                print(f"  🐍 Python Version: {result.stdout.strip()}")
            except:
                print("  🐍 Python Version: Unable to determine")
        
        if self.project_dir.joinpath("requirements.txt").exists():
            try:
                with open(self.project_dir / "requirements.txt", 'r') as f:
                    package_count = sum(1 for line in f if line.strip() and not line.startswith('#'))
                print(f"  📦 Required Packages: {package_count}")
            except:
                print("  📦 Required Packages: Unable to count")
        
        print()
        print("=" * 40)
        input("Press Enter to continue...")
    
    def check_prerequisites(self):
        """Check prerequisites"""
        errors = 0
        
        # Check Python virtual environment
        python_exe = self.get_python_executable()
        if not python_exe.exists():
            print("❌ Python virtual environment not found")
            errors += 1
        
        # Check environment file
        if not self.env_file.exists():
            print("❌ Environment file not found")
            errors += 1
        
        # Check configuration file
        if not self.config_file.exists():
            print("❌ Configuration file not found")
            errors += 1
        
        # Create required directories
        for dir_name in ["logs", "data", "config"]:
            dir_path = self.project_dir / dir_name
            if not dir_path.exists():
                print(f"⚠️ Creating missing directory: {dir_name}")
                dir_path.mkdir(parents=True, exist_ok=True)
        
        return errors == 0
    
    def test_system(self):
        """Test system"""
        print("🧪 System Test:")
        print("=" * 40)
        
        print("1. Testing Prerequisites...")
        if self.check_prerequisites():
            print("✅ Prerequisites check passed")
        else:
            print("❌ Prerequisites check failed")
        print()
        
        print("2. Testing Python Dependencies...")
        python_exe = self.get_python_executable()
        if python_exe.exists():
            try:
                result = subprocess.run([
                    str(python_exe), "-c", 
                    "import requests, telegram, sqlalchemy, yaml"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Python dependencies available")
                else:
                    print("❌ Missing Python dependencies")
                    print(f"Error: {result.stderr}")
            except Exception as e:
                print(f"❌ Error testing dependencies: {e}")
        else:
            print("❌ Python virtual environment not found")
        print()
        
        print("3. Testing Configuration...")
        if self.env_file.exists() and self.config_file.exists():
            print("✅ Configuration files found")
        else:
            print("❌ Configuration files missing")
        print()
        
        print("4. Testing Import...")
        if python_exe.exists():
            test_script = self.project_dir / "test_imports.py"
            if test_script.exists():
                try:
                    result = subprocess.run([str(python_exe), str(test_script)], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print("✅ Import test passed")
                    else:
                        print("❌ Import test failed")
                        print(f"Error: {result.stderr}")
                except Exception as e:
                    print(f"❌ Error running import test: {e}")
            else:
                print("⚠️ Import test script not found")
        
        print()
        print("=" * 40)
        input("Press Enter to continue...")
    
    def setup_system(self):
        """Setup system"""
        print("🔧 System Setup:")
        print("=" * 40)
        
        # Run manager.py setup if available
        manager_script = self.project_dir / "manager.py"
        if manager_script.exists():
            print("Running automated setup...")
            try:
                if self.get_python_executable().exists():
                    subprocess.run([str(self.get_python_executable()), str(manager_script), "setup"])
                else:
                    subprocess.run([sys.executable, str(manager_script), "setup"])
            except Exception as e:
                print(f"❌ Setup failed: {e}")
        else:
            print("❌ Manager script not found")
            print("Please run 'python manager.py setup' manually")
        
        print()
        print("=" * 40)
        input("Press Enter to continue...")
    
    def main_menu(self):
        """Main menu"""
        while True:
            self.show_banner()
            
            # Show service status
            print("📊 Service Status:")
            self.check_status()
            print()
            
            print("🎛️ Management Menu:")
            print()
            print("1. Start Service")
            print("2. Stop Service")
            print("3. Restart Service")
            print("4. View Logs")
            print("5. System Statistics")
            print("6. Test System")
            print("7. Setup System")
            print("0. Exit")
            print()
            
            try:
                choice = input("Your choice: ").strip()
                
                if choice == "1":
                    self.start_service()
                    input("Press Enter to continue...")
                elif choice == "2":
                    self.stop_service()
                    input("Press Enter to continue...")
                elif choice == "3":
                    self.restart_service()
                    input("Press Enter to continue...")
                elif choice == "4":
                    self.show_logs()
                elif choice == "5":
                    self.show_stats()
                elif choice == "6":
                    self.test_system()
                elif choice == "7":
                    self.setup_system()
                elif choice == "0":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice")
                    time.sleep(2)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(2)

def main():
    """Main function"""
    manager = P24ServerManager()
    
    # Command line interface
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            manager.start_service()
        elif command == "stop":
            manager.stop_service()
        elif command == "restart":
            manager.restart_service()
        elif command == "status":
            manager.check_status()
        elif command == "logs":
            manager.show_logs()
        elif command == "stats":
            manager.show_stats()
        elif command == "test":
            manager.test_system()
        elif command == "setup":
            manager.setup_system()
        else:
            print("Usage: python server_manager.py [start|stop|restart|status|logs|stats|test|setup]")
            print("Or run without arguments for interactive menu")
            sys.exit(1)
    else:
        # Interactive menu
        manager.main_menu()

if __name__ == "__main__":
    main()