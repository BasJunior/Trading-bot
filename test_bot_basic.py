#!/usr/bin/env python3
"""
Test basic bot functionality after restart
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import DerivTelegramBot
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bot_basic_functionality():
    """Test basic bot functionality"""
    
    print("🔍 Testing bot basic functionality...")
    
    try:
        # Create bot instance
        bot = DerivTelegramBot()
        print("✅ Bot instance created successfully")
        
        # Check if all attributes exist
        required_attrs = ['user_accounts', 'user_sessions', 'default_deriv_api', 'connection_manager']
        
        for attr in required_attrs:
            if hasattr(bot, attr):
                print(f"✅ {attr}: exists")
            else:
                print(f"❌ {attr}: missing")
        
        # Test _ensure_attributes method
        try:
            bot._ensure_attributes()
            print("✅ _ensure_attributes() works")
        except Exception as e:
            print(f"❌ _ensure_attributes() failed: {e}")
        
        # Test connection manager
        try:
            if bot.connection_manager and bot.connection_manager.is_connected:
                print("✅ Connection manager is connected")
            else:
                print("⚠️  Connection manager not connected")
        except Exception as e:
            print(f"❌ Connection manager error: {e}")
        
        # Test default API
        try:
            if bot.default_deriv_api:
                print("✅ Default Deriv API exists")
            else:
                print("❌ Default Deriv API missing")
        except Exception as e:
            print(f"❌ Default Deriv API error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing bot after restart...")
    asyncio.run(test_bot_basic_functionality())
