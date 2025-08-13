#!/usr/bin/env python3
"""
Deployment script for Deriv Telegram Bot
Handles installation, configuration, and deployment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print deployment banner"""
    print("=" * 60)
    print("🚀 DERIV TELEGRAM BOT DEPLOYMENT")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    print("\n📦 Setting up virtual environment...")
    
    if os.path.exists('.venv'):
        print("✅ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("\n📋 Installing dependencies...")
    
    pip_cmd = '.venv/bin/pip' if os.name != 'nt' else '.venv\\Scripts\\pip.exe'
    
    try:
        # Upgrade pip
        subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], check=True)
        
        # Install main requirements
        subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Main dependencies installed")
        
        # Install MT5 requirements if requested
        if input("\n🔧 Install MT5 CFD trading support? (y/N): ").lower() == 'y':
            if os.path.exists('requirements_mt5.txt'):
                subprocess.run([pip_cmd, 'install', '-r', 'requirements_mt5.txt'], check=True)
                print("✅ MT5 dependencies installed")
            else:
                print("⚠️ MT5 requirements file not found")
        
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def setup_configuration():
    """Setup configuration files"""
    print("\n⚙️ Setting up configuration...")
    
    # Copy environment template
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ Environment file created from template")
        else:
            print("⚠️ No .env.example found, creating basic .env")
            with open('.env', 'w') as f:
                f.write("# Telegram Bot Token\n")
                f.write("TELEGRAM_BOT_TOKEN=your_token_here\n")
                f.write("# Deriv API\n")
                f.write("DERIV_APP_ID=1089\n")
                f.write("DERIV_API_TOKEN=optional_token\n")
    else:
        print("✅ Environment file already exists")
    
    # Setup tokens interactively
    if input("\n🔑 Configure tokens now? (Y/n): ").lower() != 'n':
        try:
            subprocess.run([sys.executable, 'setup_tokens.py'], check=True)
            print("✅ Tokens configured")
        except subprocess.CalledProcessError:
            print("⚠️ Token setup failed, you can run setup_tokens.py manually later")
    
    return True

def run_tests():
    """Run basic tests"""
    print("\n🧪 Running tests...")
    
    try:
        # Run basic connection test
        if os.path.exists('test_api_simple.py'):
            subprocess.run([sys.executable, 'test_api_simple.py'], check=True)
            print("✅ Basic tests passed")
        else:
            print("⚠️ Test files not found, skipping tests")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Some tests failed, check configuration")
        return True  # Don't fail deployment for test failures

def create_startup_script():
    """Create startup script"""
    print("\n📜 Creating startup scripts...")
    
    # Linux/Mac startup script
    startup_script = """#!/bin/bash
# Deriv Telegram Bot Startup Script

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Start the bot
echo "🚀 Starting Deriv Telegram Bot..."
python telegram_bot.py
"""
    
    with open('start_bot.sh', 'w') as f:
        f.write(startup_script)
    os.chmod('start_bot.sh', 0o755)
    print("✅ Linux/Mac startup script created: start_bot.sh")
    
    # Windows startup script
    windows_script = """@echo off
REM Deriv Telegram Bot Startup Script

cd /d "%~dp0"

REM Activate virtual environment
call .venv\\Scripts\\activate.bat

REM Start the bot
echo 🚀 Starting Deriv Telegram Bot...
python telegram_bot.py
pause
"""
    
    with open('start_bot.bat', 'w') as f:
        f.write(windows_script)
    print("✅ Windows startup script created: start_bot.bat")

def create_systemd_service():
    """Create systemd service file for Linux"""
    if os.name != 'posix':
        return
    
    if input("\n🔧 Create systemd service for auto-start? (y/N): ").lower() != 'y':
        return
    
    current_dir = os.getcwd()
    user = os.getenv('USER', 'ubuntu')
    
    service_content = f"""[Unit]
Description=Deriv Telegram Trading Bot
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={current_dir}
Environment=PATH={current_dir}/.venv/bin
ExecStart={current_dir}/.venv/bin/python {current_dir}/telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = 'deriv-telegram-bot.service'
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print(f"✅ Systemd service file created: {service_file}")
    print(f"To install: sudo cp {service_file} /etc/systemd/system/")
    print("Then: sudo systemctl enable deriv-telegram-bot")
    print("Start: sudo systemctl start deriv-telegram-bot")

def print_next_steps():
    """Print next steps for user"""
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("1. Configure your .env file with actual tokens")
    print("2. Test the bot: python telegram_bot.py")
    print("3. For production: ./start_bot.sh (Linux/Mac) or start_bot.bat (Windows)")
    print("\n🔧 CONFIGURATION:")
    print("• Edit .env file for API tokens")
    print("• Run setup_tokens.py for interactive setup")
    print("• Check config.py for advanced settings")
    print("\n📖 DOCUMENTATION:")
    print("• README.md - Complete usage guide")
    print("• docs/ - Additional documentation")
    print("• /help in Telegram - Bot commands")
    print("\n🆘 SUPPORT:")
    print("• Check logs: tail -f bot.log")
    print("• Test API: python test_api_simple.py")
    print("• GitHub Issues for problems")
    print("\n⚠️ SECURITY REMINDER:")
    print("• Never commit your .env file")
    print("• Keep API tokens secure")
    print("• Start with demo accounts")

def main():
    """Main deployment function"""
    print_banner()
    
    # Check requirements
    if not check_python_version():
        return False
    
    # Setup steps
    steps = [
        create_virtual_environment,
        install_dependencies,
        setup_configuration,
        run_tests,
        create_startup_script,
        create_systemd_service
    ]
    
    for step in steps:
        if not step():
            print(f"❌ Deployment failed at step: {step.__name__}")
            return False
    
    print_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)
