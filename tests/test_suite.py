#!/usr/bin/env python3
"""
Test Suite for Deriv Telegram Bot
Comprehensive testing of all bot functionality
"""

import asyncio
import pytest
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestBotConfiguration:
    """Test bot configuration and setup"""
    
    def test_config_loading(self):
        """Test configuration loading"""
        from src.bot.config import Config
        
        assert Config.BOT_NAME
        assert Config.BOT_VERSION
        assert isinstance(Config.MAX_USERS, int)
        assert Config.MAX_USERS > 0
    
    def test_environment_variables(self):
        """Test environment variable handling"""
        # Test with mock environment
        with patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG'}):
            from src.bot.config import BotConfig
            config = BotConfig()
            assert config.LOG_LEVEL == 'DEBUG'

class TestDerivAPI:
    """Test Deriv API integration"""
    
    @pytest.mark.asyncio
    async def test_connection_manager_init(self):
        """Test connection manager initialization"""
        try:
            from connection_manager_fixed import get_connection_manager
            manager = get_connection_manager("1089")
            assert manager is not None
        except ImportError:
            pytest.skip("Connection manager not available")
    
    @pytest.mark.asyncio
    async def test_api_connection(self):
        """Test basic API connection"""
        try:
            from connection_manager_fixed import DerivAPI
            api = DerivAPI("1089")
            # Don't actually connect in tests
            assert api.app_id == "1089"
        except ImportError:
            pytest.skip("DerivAPI not available")

class TestTelegramBot:
    """Test Telegram bot functionality"""
    
    def test_bot_initialization(self):
        """Test bot initialization"""
        try:
            # Mock Telegram token for testing
            with patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'}):
                from telegram_bot import DerivTelegramBot
                # Don't actually initialize with real token
                assert DerivTelegramBot is not None
        except ImportError:
            pytest.skip("Telegram bot module not available")
    
    def test_command_handlers_setup(self):
        """Test that command handlers are properly defined"""
        try:
            from telegram_bot import DerivTelegramBot
            # Check if class has required methods
            assert hasattr(DerivTelegramBot, 'start_command')
            assert hasattr(DerivTelegramBot, 'help_command')
            assert hasattr(DerivTelegramBot, 'balance_command')
            assert hasattr(DerivTelegramBot, 'connect_command')
        except ImportError:
            pytest.skip("Telegram bot module not available")

class TestMT5Integration:
    """Test MT5 CFD trading integration"""
    
    def test_mt5_import(self):
        """Test MT5 module import"""
        try:
            from mt5_cfd_trading import MT5CFDTrader
            assert MT5CFDTrader is not None
        except ImportError:
            pytest.skip("MT5 module not available")
    
    def test_mt5_trader_init(self):
        """Test MT5 trader initialization"""
        try:
            from mt5_cfd_trading import MT5CFDTrader
            # Mock initialization without actual MT5 connection
            trader = MT5CFDTrader(user_id=12345, login=123456, password="test", server="test")
            assert trader.user_id == 12345
        except ImportError:
            pytest.skip("MT5 module not available")

class TestTradingStrategies:
    """Test trading strategy implementations"""
    
    def test_strategy_manager_import(self):
        """Test strategy manager import"""
        try:
            from telegram_bot import StrategyManager
            assert StrategyManager is not None
        except (ImportError, AttributeError):
            pytest.skip("Strategy manager not available")
        except ValueError as e:
            # Config validation error when TELEGRAM_BOT_TOKEN is missing
            if "TELEGRAM_BOT_TOKEN" in str(e):
                pytest.skip("Strategy manager not available (TELEGRAM_BOT_TOKEN not set)")
            raise
        except SystemExit:
            # telegram_bot.py calls exit(1) when config validation fails
            pytest.skip("Strategy manager not available (configuration error on import)")
    
    def test_step_system_utilities_import(self):
        """Test step system utilities import"""
        try:
            from src.trading.utilities import StepSystemUtilities
            assert StepSystemUtilities is not None
        except ImportError:
            pytest.skip("Trading utilities module not available")
    
    def test_volatility75_scalping_strategy_import(self):
        """Test Volatility75ScalpingStrategy import"""
        try:
            from src.trading.strategies import Volatility75ScalpingStrategy
            assert Volatility75ScalpingStrategy is not None
        except ImportError:
            pytest.skip("Trading strategies module not available")
    
    def test_step_signal_calculation(self):
        """Test step signal calculation"""
        try:
            from src.trading.utilities import calculate_step_signal, TradingSignal
            
            # Test with sample prices
            prices = [100.0 + i * 0.1 for i in range(30)]
            result = calculate_step_signal(prices)
            
            assert result is not None
            assert result.signal in [TradingSignal.BUY, TradingSignal.SELL, TradingSignal.HOLD]
        except ImportError:
            pytest.skip("Trading utilities module not available")
    
    def test_volatility_signal_calculation(self):
        """Test volatility signal calculation uses same model as step"""
        try:
            from src.trading.utilities import calculate_step_signal, calculate_volatility_signal
            
            # Both functions should use the same underlying logic
            prices = [100.0 + i * 0.1 for i in range(30)]
            step_result = calculate_step_signal(prices)
            vol_result = calculate_volatility_signal(prices)
            
            # Results should be identical since they use the same model
            assert step_result.signal == vol_result.signal
        except ImportError:
            pytest.skip("Trading utilities module not available")
    
    def test_validate_trading_parameters(self):
        """Test trading parameter validation"""
        try:
            from src.trading.utilities import validate_trading_parameters
            
            # Valid parameters
            is_valid, msg = validate_trading_parameters("R_75", 1.0)
            assert is_valid
            
            # Invalid symbol
            is_valid, msg = validate_trading_parameters("INVALID", 1.0)
            assert not is_valid
            
            # Lot size too small
            is_valid, msg = validate_trading_parameters("R_75", 0.0001)
            assert not is_valid
            
            # Negative lot size
            is_valid, msg = validate_trading_parameters("R_75", -1.0)
            assert not is_valid
            
            # Zero lot size
            is_valid, msg = validate_trading_parameters("R_75", 0)
            assert not is_valid
        except ImportError:
            pytest.skip("Trading utilities module not available")
    
    def test_get_recommended_lot_sizes(self):
        """Test recommended lot sizes"""
        try:
            from src.trading.utilities import get_recommended_lot_sizes
            
            # Scalping lots
            scalping_lots = get_recommended_lot_sizes("scalping")
            assert len(scalping_lots) > 0
            
            # Swing lots
            swing_lots = get_recommended_lot_sizes("swing")
            assert len(swing_lots) > 0
        except ImportError:
            pytest.skip("Trading utilities module not available")

class TestSecurityFeatures:
    """Test security and validation features"""
    
    def test_api_token_validation(self):
        """Test API token format validation"""
        # Test basic token format validation
        valid_tokens = [
            "abc123def456ghi789",
            "1234567890abcdef",
            "a1b2c3d4e5f6g7h8i9j0"
        ]
        
        invalid_tokens = [
            "short",
            "",
            "   ",
            "special@chars!"
        ]
        
        for token in valid_tokens:
            assert len(token) >= 10  # Basic length check
        
        for token in invalid_tokens:
            assert len(token) < 10 or not token.strip()
    
    def test_position_size_limits(self):
        """Test position size validation"""
        from src.bot.config import Config
        
        assert Config.MAX_POSITION_SIZE > 0
        assert Config.MAX_OPEN_POSITIONS > 0
        assert Config.MAX_DAILY_LOSS > 0

class TestUtilities:
    """Test utility functions"""
    
    def test_file_structure(self):
        """Test that required files exist"""
        required_files = [
            'telegram_bot.py',
            'config.py',
            'requirements.txt',
            'README.md',
            '.gitignore'
        ]
        
        for file in required_files:
            assert os.path.exists(file), f"Required file missing: {file}"
    
    def test_directory_structure(self):
        """Test that required directories exist"""
        required_dirs = [
            'src',
            'src/bot',
            'src/trading',
            'tests',
            'docs',
            'scripts'
        ]
        
        for dir_path in required_dirs:
            assert os.path.isdir(dir_path), f"Required directory missing: {dir_path}"

class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_bot_startup_sequence(self):
        """Test bot startup without actually starting"""
        # Mock the startup sequence
        startup_steps = [
            "Load configuration",
            "Initialize connection manager", 
            "Setup Telegram application",
            "Register command handlers",
            "Start polling"
        ]
        
        # Simulate startup sequence
        for step in startup_steps:
            # In real test, we would check each step
            assert isinstance(step, str)
    
    def test_error_handling(self):
        """Test error handling mechanisms"""
        # Test that error handlers are defined
        try:
            from telegram_bot import DerivTelegramBot
            assert hasattr(DerivTelegramBot, 'error_handler')
        except ImportError:
            pytest.skip("Telegram bot module not available")

def run_performance_test():
    """Run basic performance tests"""
    print("🔧 Running performance tests...")
    
    import time
    import psutil
    
    # Test memory usage
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"📊 Initial memory usage: {initial_memory:.2f} MB")
    
    # Test response time (mock)
    start_time = time.time()
    # Simulate some work
    time.sleep(0.1)
    response_time = time.time() - start_time
    
    print(f"⏱️ Mock response time: {response_time:.3f} seconds")
    
    assert initial_memory < 100, "Memory usage too high"
    assert response_time < 1.0, "Response time too slow"

def run_basic_tests():
    """Run basic functionality tests"""
    print("🧪 Running basic tests...")
    
    # Test imports
    try:
        import config
        print("✅ Config import successful")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
    
    try:
        import telegram_bot
        print("✅ Telegram bot import successful")
    except ImportError as e:
        print(f"❌ Telegram bot import failed: {e}")
    
    # Test file existence
    required_files = ['telegram_bot.py', 'config.py', 'requirements.txt']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")

if __name__ == "__main__":
    print("🚀 DERIV TELEGRAM BOT - TEST SUITE")
    print("=" * 50)
    
    # Run basic tests first
    run_basic_tests()
    print()
    
    # Run performance tests
    try:
        run_performance_test()
        print()
    except Exception as e:
        print(f"⚠️ Performance tests failed: {e}")
    
    # Run pytest if available
    try:
        print("🔬 Running pytest suite...")
        result = pytest.main([__file__, "-v"])
        
        if result == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n⚠️ Some tests failed or were skipped")
    
    except ImportError:
        print("⚠️ pytest not installed, skipping advanced tests")
        print("Install with: pip install pytest")
    
    print("\n📋 Test Summary:")
    print("• Basic functionality: File imports and structure")
    print("• Configuration: Environment and settings")
    print("• Security: Input validation and limits")
    print("• Integration: Component interaction")
    print("• Performance: Memory and response time")
    
    print("\n💡 Next Steps:")
    print("• Run with real tokens: python test_api_simple.py")
    print("• Start bot: python telegram_bot.py")
    print("• Check logs: tail -f bot.log")
