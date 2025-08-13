#!/usr/bin/env python3
"""
Test bot initialization to debug the user_accounts attribute issue
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import DerivTelegramBot

def test_bot_initialization():
    """Test if the bot can be initialized properly"""
    try:
        print("Testing bot initialization...")
        
        # Test step by step
        from config import Config
        print(f"✅ Config loaded: APP_ID={Config.DERIV_APP_ID}, TOKEN_SET={bool(Config.DERIV_API_TOKEN)}")
        
        from telegram_bot import DerivAPI
        print("✅ DerivAPI imported")
        
        # Test DerivAPI creation
        test_api = DerivAPI(Config.DERIV_APP_ID, Config.DERIV_API_TOKEN)
        print(f"✅ DerivAPI created: {test_api}")
        
        # Create bot instance
        print("Creating DerivTelegramBot...")
        bot = DerivTelegramBot()
        print("✅ DerivTelegramBot created")
        
        # Check method resolution order and __init__ method
        print(f"MRO: {DerivTelegramBot.__mro__}")
        print(f"__init__ method: {DerivTelegramBot.__init__}")
        print(f"Bot class: {bot.__class__}")
        print(f"Bot.__init__: {bot.__init__}")
        
        # Try to manually call __init__ 
        print("Trying to call __init__ manually...")
        bot.__init__()
        print("Manual __init__ called")
        
        # Check if required attributes exist
        required_attrs = [
            'user_accounts', 'user_sessions', 'strategy_manager', 
            'price_history', 'application', 'default_deriv_api'
        ]
        
        for attr in required_attrs:
            if hasattr(bot, attr):
                print(f"✅ {attr}: {type(getattr(bot, attr))}")
            else:
                print(f"❌ Missing attribute: {attr}")
        
        print("✅ Bot initialization successful!")
        return True
        
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_bot_initialization()
