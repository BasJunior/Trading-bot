#!/usr/bin/env python3
"""
Debug version of bot initialization
"""

import logging
from telegram_bot import DerivAPI, StrategyManager
from config import Config
from telegram.ext import Application

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebugDerivTelegramBot:
    """Debug version of main Telegram Bot class"""
    
    def __init__(self, telegram_token: str = None, deriv_app_id: str = None, deriv_api_token: str = None):
        print("🔍 Starting bot initialization...")
        
        try:
            # Use environment variables if not provided
            print("📝 Setting telegram_token...")
            self.telegram_token = telegram_token or Config.TELEGRAM_BOT_TOKEN
            print(f"✅ telegram_token set: {bool(self.telegram_token)}")
            
            print("📝 Setting deriv_app_id...")
            deriv_app_id = deriv_app_id or Config.DERIV_APP_ID
            print(f"✅ deriv_app_id: {deriv_app_id}")
            
            print("📝 Setting deriv_api_token...")
            deriv_api_token = deriv_api_token or Config.DERIV_API_TOKEN
            print(f"✅ deriv_api_token length: {len(deriv_api_token) if deriv_api_token else 0}")
            
            # Initialize core attributes one by one
            print("📝 Creating default_deriv_api...")
            self.default_deriv_api = DerivAPI(deriv_app_id, deriv_api_token)
            print("✅ default_deriv_api created")
            
            print("📝 Creating user_accounts...")
            self.user_accounts = {}  # Store user-specific API connections
            print("✅ user_accounts created")
            
            print("📝 Creating user_sessions...")
            self.user_sessions = {}  # Store user-specific data
            print("✅ user_sessions created")
            
            print("📝 Creating strategy_manager...")
            self.strategy_manager = StrategyManager(self)  # Add strategy manager
            print("✅ strategy_manager created")
            
            print("📝 Creating price_history...")
            self.price_history = {}  # Store price history for analysis
            print("✅ price_history created")
            
            print("📝 Creating Telegram application...")
            self.application = Application.builder().token(self.telegram_token).build()
            print("✅ Telegram application created")
            
            print("🎉 Bot initialization completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during initialization: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    try:
        bot = DebugDerivTelegramBot()
        print("\n📊 Final attribute check:")
        for attr in ['telegram_token', 'user_accounts', 'user_sessions', 'default_deriv_api', 'strategy_manager', 'price_history']:
            has_attr = hasattr(bot, attr)
            print(f"  {attr}: {has_attr}")
            
    except Exception as e:
        print(f"❌ Failed to create bot: {e}")
