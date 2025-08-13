#!/usr/bin/env python3
"""
Bot status checker - Quick diagnostic tool
"""

import subprocess
import sys
import requests
from config import Config

def check_process():
    """Check if bot process is running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'telegram_bot.py' in result.stdout:
            lines = [line for line in result.stdout.split('\n') if 'telegram_bot.py' in line and 'grep' not in line]
            if lines:
                print("✅ Bot process is running")
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        print(f"   PID: {parts[1]}")
                return True
        
        print("❌ Bot process is not running")
        return False
    except Exception as e:
        print(f"❌ Error checking process: {e}")
        return False

def check_telegram_connection():
    """Check Telegram API connection"""
    try:
        token = Config.TELEGRAM_BOT_TOKEN
        if not token:
            print("❌ No Telegram bot token configured")
            return False
        
        url = f'https://api.telegram.org/bot{token}/getMe'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            bot_info = data['result']
            print("✅ Telegram connection OK")
            print(f"   Bot name: {bot_info.get('first_name', 'Unknown')}")
            print(f"   Username: @{bot_info.get('username', 'Unknown')}")
            return True
        else:
            print("❌ Telegram connection failed")
            print(f"   Error: {data.get('description', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram connection error: {e}")
        return False

def check_deriv_config():
    """Check Deriv configuration"""
    try:
        app_id = Config.DERIV_APP_ID
        api_token = Config.DERIV_API_TOKEN
        
        print(f"✅ Deriv App ID: {app_id}")
        print(f"✅ Deriv API Token: {'Configured' if api_token else 'Not configured'}")
        return True
        
    except Exception as e:
        print(f"❌ Deriv config error: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🔍 Bot Status Check")
    print("=" * 30)
    
    print("\n📋 Process Status:")
    process_ok = check_process()
    
    print("\n📡 Telegram Connection:")
    telegram_ok = check_telegram_connection()
    
    print("\n🔧 Deriv Configuration:")
    deriv_ok = check_deriv_config()
    
    print("\n📊 Summary:")
    print("=" * 30)
    
    if process_ok and telegram_ok and deriv_ok:
        print("🎉 All systems operational!")
        print("\n💡 If bot is still not responding:")
        print("   1. Send /start to your bot on Telegram")
        print("   2. Check if you're messaging the correct bot")
        print("   3. Verify bot permissions in Telegram")
    else:
        print("⚠️  Issues detected:")
        if not process_ok:
            print("   - Start bot with: python3 telegram_bot.py")
        if not telegram_ok:
            print("   - Check TELEGRAM_BOT_TOKEN in .env file")
        if not deriv_ok:
            print("   - Check Deriv configuration")
        
        print("\n🔧 Quick fixes:")
        print("   ./start_bot.sh         # Start the bot")
        print("   python3 setup_tokens.py  # Reconfigure tokens")
        print("   python3 test_bot.py      # Run full tests")

if __name__ == "__main__":
    main()
