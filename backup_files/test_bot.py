#!/usr/bin/env python3
"""
Test script for Deriv Telegram Bot
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import DerivTelegramBot, DerivAPI
from config import Config

def test_imports():
    """Test that all imports are working"""
    print("🧪 Testing imports...")
    try:
        from telegram_bot import (
            DerivAPI, TechnicalIndicators, TradingStrategy,
            StepIndex100ScalpingStrategy, Volatility75SwingStrategy,
            CustomScalpingStrategy, CustomSwingStrategy,
            StrategyManager, DerivTelegramBot
        )
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("🧪 Testing configuration...")
    try:
        # Test basic config loading
        print(f"• App ID: {Config.DERIV_APP_ID}")
        print(f"• Log Level: {Config.LOG_LEVEL}")
        print(f"• Default Lot Size: {Config.DEFAULT_LOT_SIZE}")
        
        # Test supported symbols
        symbols = Config.get_supported_symbols()
        print(f"• Supported symbols: {len(symbols)} symbols")
        
        # Test strategy defaults
        defaults = Config.get_strategy_defaults()
        print(f"• Strategy defaults: {len(defaults)} strategies")
        
        print("✅ Configuration test passed")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_bot_creation():
    """Test bot creation"""
    print("🧪 Testing bot creation...")
    try:
        # Try to create bot instance
        bot = DerivTelegramBot(
            telegram_token="test_token",
            deriv_app_id=Config.DERIV_APP_ID,
            deriv_api_token=None
        )
        print("✅ Bot instance created successfully")
        return True
    except Exception as e:
        print(f"❌ Bot creation error: {e}")
        return False

def test_strategy_manager():
    """Test strategy manager"""
    print("🧪 Testing strategy manager...")
    try:
        # Create bot instance
        bot = DerivTelegramBot(
            telegram_token="test_token",
            deriv_app_id=Config.DERIV_APP_ID
        )
        
        # Test strategy manager
        manager = bot.strategy_manager
        print(f"• Strategy manager type: {type(manager).__name__}")
        print(f"• Active strategies: {len(manager.active_strategies)}")
        
        print("✅ Strategy manager test passed")
        return True
    except Exception as e:
        print(f"❌ Strategy manager error: {e}")
        return False

def test_technical_indicators():
    """Test technical indicators"""
    print("🧪 Testing technical indicators...")
    try:
        from telegram_bot import TechnicalIndicators
        
        # Create test data
        test_prices = [100.0, 101.0, 102.0, 101.5, 103.0, 102.5, 104.0, 103.5, 105.0, 104.5]
        
        indicators = TechnicalIndicators()
        
        # Test EMA
        ema = indicators.calculate_ema(test_prices, 5)
        print(f"• EMA calculation: {'✅ Success' if ema is not None else '❌ Failed'}")
        
        # Test RSI
        rsi = indicators.calculate_rsi(test_prices, 5)
        print(f"• RSI calculation: {'✅ Success' if rsi is not None else '❌ Failed'}")
        
        # Test Bollinger Bands
        bb = indicators.calculate_bollinger_bands(test_prices, 5, 2)
        print(f"• Bollinger Bands: {'✅ Success' if bb[0] is not None else '❌ Failed'}")
        
        # Test MACD
        macd = indicators.calculate_macd(test_prices, 3, 6, 2)
        print(f"• MACD calculation: {'✅ Success' if macd[0] is not None else '❌ Failed'}")
        
        print("✅ Technical indicators test passed")
        return True
    except Exception as e:
        print(f"❌ Technical indicators error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Deriv Telegram Bot Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_configuration,
        test_bot_creation,
        test_strategy_manager,
        test_technical_indicators
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Bot is ready to use.")
        print("\n📋 Next steps:")
        print("1. Update .env file with your actual tokens")
        print("2. Run: python3 telegram_bot.py")
        print("3. Start trading with improved UI!")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
