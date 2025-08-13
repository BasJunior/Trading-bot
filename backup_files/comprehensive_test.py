#!/usr/bin/env python3
"""
Comprehensive bot functionality test
"""
import asyncio
import os
import sys
import subprocess
import time
from telegram import Bot
from telegram.ext import Application
from dotenv import load_dotenv

async def test_bot_commands():
    """Test bot basic functionality"""
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    print("🔍 Testing Bot Functionality")
    print("=" * 50)
    
    try:
        bot = Bot(token=token)
        
        # Test 1: Get bot info
        print("1. Testing bot connection...")
        bot_info = await bot.get_me()
        print(f"   ✅ Bot connected: @{bot_info.username}")
        
        # Test 2: Check if bot can receive commands (webhook status)
        print("2. Testing webhook/polling status...")
        webhook_info = await bot.get_webhook_info()
        print(f"   ✅ Webhook URL: {webhook_info.url or 'Not set (using polling)'}")
        
        # Test 3: Check commands are set
        print("3. Testing bot commands...")
        commands = await bot.get_my_commands()
        if commands:
            print(f"   ✅ Bot has {len(commands)} registered commands")
            for cmd in commands[:3]:  # Show first 3
                print(f"      /{cmd.command} - {cmd.description}")
        else:
            print("   ⚠️ No commands registered yet")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_bot_process():
    """Check if bot process is running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout
        
        if 'telegram_bot.py' in processes:
            print("✅ Bot process is running")
            return True
        else:
            print("❌ Bot process not found")
            return False
    except Exception as e:
        print(f"❌ Error checking process: {e}")
        return False

def check_config():
    """Check configuration"""
    load_dotenv()
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'DERIV_APP_ID', 
        'DERIV_API_TOKEN'
    ]
    
    print("📋 Configuration Check:")
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive info
            if 'TOKEN' in var:
                display_value = value[:10] + "..." + value[-5:] if len(value) > 15 else value
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: Missing")
            all_good = False
    
    return all_good

async def main():
    print("🤖 Deriv Telegram Bot - Comprehensive Test")
    print("=" * 60)
    
    # Check 1: Configuration
    print("\n📋 Step 1: Configuration Check")
    config_ok = check_config()
    
    # Check 2: Process status
    print("\n🔄 Step 2: Process Status Check")
    process_ok = check_bot_process()
    
    # Check 3: Bot functionality
    print("\n🔍 Step 3: Bot Functionality Test")
    bot_ok = await test_bot_commands()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Bot Process:   {'✅ RUNNING' if process_ok else '❌ NOT RUNNING'}")
    print(f"Bot API:       {'✅ WORKING' if bot_ok else '❌ FAILED'}")
    
    if all([config_ok, process_ok, bot_ok]):
        print("\n🎉 ALL TESTS PASSED!")
        print("🤖 Your bot is ready to receive commands!")
        print("📱 Try sending /start in Telegram")
        print(f"🔗 Bot username: @{(await Bot(os.getenv('TELEGRAM_BOT_TOKEN')).get_me()).username}")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("🔧 Please check the failed components above")

if __name__ == "__main__":
    asyncio.run(main())
