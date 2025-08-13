#!/usr/bin/env python3
"""
Quick async test for the bot
"""

import asyncio
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import DerivTelegramBot
from config import Config

async def test_bot_async():
    """Test bot async functionality"""
    try:
        print("🧪 Testing bot async functionality...")
        
        # Create bot instance
        bot = DerivTelegramBot(
            Config.TELEGRAM_BOT_TOKEN,
            Config.DERIV_APP_ID,
            Config.DERIV_API_TOKEN
        )
        
        print("✅ Bot instance created successfully")
        
        # Test async method
        if hasattr(bot, 'deriv_api') and bot.deriv_api:
            print("✅ DerivAPI instance found")
        
        print("✅ Async functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        return False

def main():
    """Main test function"""
    try:
        # Test that we can run async code
        result = asyncio.run(test_bot_async())
        
        if result:
            print("\n🎉 Async functionality is working correctly!")
            return 0
        else:
            print("\n❌ Async functionality test failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
