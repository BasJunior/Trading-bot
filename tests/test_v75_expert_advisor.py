#!/usr/bin/env python3
"""
Tests for V75 Expert Advisor Module
"""

import asyncio
import pytest
import pytest_asyncio
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

# Import the V75 EA module
from v75_expert_advisor import (
    V75Config,
    V75ExpertAdvisor,
    V75EAManager,
    TradeDirection,
    MarketCondition,
    TradeSignal,
    TradeStatistics,
    TechnicalAnalysis,
    create_v75_ea,
    start_v75_ea,
    stop_v75_ea,
    get_v75_ea,
    get_v75_ea_stats
)


class TestV75Config:
    """Tests for V75Config class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = V75Config()
        
        assert config.lot_size == 1.0
        assert config.stop_loss_pips == 50.0
        assert config.take_profit_pips == 100.0
        assert config.risk_per_trade_percent == 2.0
        assert config.max_daily_loss_percent == 5.0
        assert config.max_open_trades == 3
        assert config.ema_fast_period == 9
        assert config.ema_slow_period == 21
        assert config.rsi_period == 14
    
    def test_config_validation_valid(self):
        """Test config validation with valid values"""
        config = V75Config(
            lot_size=1.0,
            stop_loss_pips=50.0,
            take_profit_pips=100.0
        )
        assert config.validate() is True
    
    def test_config_validation_lot_size_too_small(self):
        """Test config validation with lot size below minimum"""
        config = V75Config(lot_size=0.1)
        with pytest.raises(ValueError, match="below minimum"):
            config.validate()
    
    def test_config_validation_lot_size_too_large(self):
        """Test config validation with lot size above maximum"""
        config = V75Config(lot_size=15.0)
        with pytest.raises(ValueError, match="exceeds maximum"):
            config.validate()
    
    def test_config_validation_invalid_risk(self):
        """Test config validation with invalid risk percentage"""
        config = V75Config(risk_per_trade_percent=15.0)
        with pytest.raises(ValueError, match="Risk per trade"):
            config.validate()
    
    def test_config_validation_negative_stop_loss(self):
        """Test config validation with negative stop loss"""
        config = V75Config(stop_loss_pips=-10.0)
        with pytest.raises(ValueError, match="Stop loss must be positive"):
            config.validate()


class TestTradeStatistics:
    """Tests for TradeStatistics class"""
    
    def test_win_rate_calculation(self):
        """Test win rate calculation"""
        stats = TradeStatistics(
            total_trades=10,
            winning_trades=7,
            losing_trades=3
        )
        assert stats.win_rate == 70.0
    
    def test_win_rate_zero_trades(self):
        """Test win rate with zero trades"""
        stats = TradeStatistics()
        assert stats.win_rate == 0.0
    
    def test_profit_factor_calculation(self):
        """Test profit factor calculation"""
        stats = TradeStatistics(
            total_profit=100.0,
            total_loss=50.0
        )
        assert stats.profit_factor == 2.0
    
    def test_profit_factor_zero_loss(self):
        """Test profit factor with zero loss"""
        stats = TradeStatistics(
            total_profit=100.0,
            total_loss=0.0
        )
        assert stats.profit_factor == float('inf')
    
    def test_net_profit_calculation(self):
        """Test net profit calculation"""
        stats = TradeStatistics(
            total_profit=150.0,
            total_loss=50.0
        )
        assert stats.net_profit == 100.0
    
    def test_daily_net_calculation(self):
        """Test daily net calculation"""
        stats = TradeStatistics(
            daily_profit=75.0,
            daily_loss=25.0
        )
        assert stats.daily_net == 50.0


class TestTechnicalAnalysis:
    """Tests for TechnicalAnalysis class"""
    
    def test_ema_calculation(self):
        """Test EMA calculation"""
        prices = np.array([100, 102, 104, 103, 105, 107, 106, 108, 110, 109] * 3)
        ema = TechnicalAnalysis.calculate_ema(prices, period=10)
        
        assert ema is not None
        assert len(ema) == len(prices)
        # EMA should be close to the mean for this data
        assert abs(ema[-1] - np.mean(prices[-10:])) < 5
    
    def test_ema_insufficient_data(self):
        """Test EMA with insufficient data"""
        prices = np.array([100, 102, 104])
        ema = TechnicalAnalysis.calculate_ema(prices, period=10)
        assert ema is None
    
    def test_rsi_calculation(self):
        """Test RSI calculation"""
        # Create price data with upward trend
        prices = np.array(list(range(100, 130)) + list(range(130, 100, -1)))
        rsi = TechnicalAnalysis.calculate_rsi(prices, period=14)
        
        assert rsi is not None
        assert len(rsi) == len(prices)
        # RSI should be bounded 0-100
        valid_rsi = rsi[~np.isnan(rsi)]
        if len(valid_rsi) > 0:
            assert all(0 <= r <= 100 for r in valid_rsi)
    
    def test_rsi_insufficient_data(self):
        """Test RSI with insufficient data"""
        prices = np.array([100, 102, 104, 106, 108])
        rsi = TechnicalAnalysis.calculate_rsi(prices, period=14)
        assert rsi is None
    
    def test_bollinger_bands_calculation(self):
        """Test Bollinger Bands calculation"""
        np.random.seed(42)
        prices = np.cumsum(np.random.randn(50)) + 100
        
        upper, middle, lower = TechnicalAnalysis.calculate_bollinger_bands(
            prices, period=20, std_dev=2.0
        )
        
        assert upper is not None
        assert middle is not None
        assert lower is not None
        # Upper should be above middle, lower should be below
        valid_idx = ~np.isnan(upper)
        if np.any(valid_idx):
            assert np.all(upper[valid_idx] >= middle[valid_idx])
            assert np.all(lower[valid_idx] <= middle[valid_idx])
    
    def test_bollinger_bands_insufficient_data(self):
        """Test Bollinger Bands with insufficient data"""
        prices = np.array([100, 102, 104])
        upper, middle, lower = TechnicalAnalysis.calculate_bollinger_bands(
            prices, period=20
        )
        assert upper is None
    
    def test_macd_calculation(self):
        """Test MACD calculation"""
        np.random.seed(42)
        prices = np.cumsum(np.random.randn(50)) + 100
        
        macd_line, signal_line, histogram = TechnicalAnalysis.calculate_macd(
            prices, fast=12, slow=26, signal=9
        )
        
        assert macd_line is not None
        assert signal_line is not None
        assert histogram is not None
    
    def test_macd_insufficient_data(self):
        """Test MACD with insufficient data"""
        prices = np.array([100, 102, 104, 106])
        macd_line, signal_line, histogram = TechnicalAnalysis.calculate_macd(
            prices, fast=12, slow=26, signal=9
        )
        assert macd_line is None
    
    def test_momentum_calculation(self):
        """Test momentum calculation"""
        prices = np.array([100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150])
        momentum = TechnicalAnalysis.calculate_momentum(prices, period=5)
        
        assert momentum is not None
        assert len(momentum) == len(prices)
        # Momentum should be positive for uptrend
        assert momentum[-1] > 0


class TestV75ExpertAdvisor:
    """Tests for V75ExpertAdvisor class"""
    
    @pytest.fixture
    def mock_api(self):
        """Create a mock API for testing"""
        api = Mock()
        api.buy_contract = AsyncMock(return_value={
            "buy": {
                "contract_id": 12345,
                "start_time": 1234567890
            }
        })
        api.get_ticks = AsyncMock(return_value={
            "tick": {"quote": 5000.0, "epoch": 1234567890}
        })
        return api
    
    @pytest.fixture
    def ea(self, mock_api):
        """Create a V75 EA instance for testing"""
        config = V75Config()
        return V75ExpertAdvisor(user_id=12345, user_api=mock_api, config=config)
    
    def test_ea_initialization(self, ea):
        """Test EA initialization"""
        assert ea.user_id == 12345
        assert ea.SYMBOL == "R_75"
        assert ea.is_active is False
        assert len(ea.price_history) == 0
    
    @pytest.mark.asyncio
    async def test_add_price(self, ea):
        """Test adding price data"""
        await ea.add_price(5000.0)
        await ea.add_price(5010.0)
        await ea.add_price(5005.0)
        
        assert len(ea.price_history) == 3
        assert list(ea.price_history) == [5000.0, 5010.0, 5005.0]
    
    @pytest.mark.asyncio
    async def test_add_price_with_high_low(self, ea):
        """Test adding price data with high/low"""
        await ea.add_price(5000.0, high=5020.0, low=4980.0)
        
        assert len(ea.price_history) == 1
        assert len(ea.high_history) == 1
        assert len(ea.low_history) == 1
        assert ea.high_history[-1] == 5020.0
        assert ea.low_history[-1] == 4980.0
    
    def test_rate_limit_check(self, ea):
        """Test rate limit checking"""
        assert ea._check_rate_limit() is True
        
        # Simulate max trades reached
        ea.trades_this_hour = ea.config.max_trades_per_hour
        assert ea._check_rate_limit() is False
    
    def test_risk_limit_check(self, ea):
        """Test risk limit checking"""
        ea.stats.start_balance = 1000.0
        ea.stats.daily_loss = 0.0
        ea.stats.max_drawdown = 0.0
        
        assert ea._check_risk_limits() is True
        
        # Simulate max daily loss reached
        ea.stats.daily_loss = 60.0  # 6% of balance
        assert ea._check_risk_limits() is False
    
    def test_max_open_trades_check(self, ea):
        """Test max open trades limit"""
        ea.stats.start_balance = 1000.0
        
        assert ea._check_risk_limits() is True
        
        # Add max open trades
        for i in range(ea.config.max_open_trades):
            ea.open_trades.append({"id": i})
        
        assert ea._check_risk_limits() is False
    
    @pytest.mark.asyncio
    async def test_analyze_ema_crossover_insufficient_data(self, ea):
        """Test EMA crossover analysis with insufficient data"""
        # Add fewer prices than needed
        for i in range(10):
            await ea.add_price(5000.0 + i)
        
        signal = await ea.analyze_ema_crossover()
        assert signal is None
    
    @pytest.mark.asyncio
    async def test_analyze_rsi_reversal_insufficient_data(self, ea):
        """Test RSI reversal analysis with insufficient data"""
        for i in range(10):
            await ea.add_price(5000.0 + i)
        
        signal = await ea.analyze_rsi_reversal()
        assert signal is None
    
    @pytest.mark.asyncio
    async def test_place_trade_success(self, ea, mock_api):
        """Test successful trade placement"""
        ea.is_trading_allowed = True
        ea.stats.start_balance = 1000.0
        
        result = await ea.place_trade("CALL", amount=1.0, duration=5)
        
        assert result is True
        assert ea.stats.total_trades == 1
        assert ea.trades_this_hour == 1
        assert len(ea.open_trades) == 1
        mock_api.buy_contract.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_place_trade_failure(self, ea, mock_api):
        """Test failed trade placement"""
        mock_api.buy_contract = AsyncMock(return_value={
            "error": {"message": "Insufficient funds"}
        })
        
        result = await ea.place_trade("CALL")
        
        assert result is False
    
    def test_record_winning_trade(self, ea):
        """Test recording a winning trade"""
        ea.stats.start_balance = 1000.0
        ea.stats.current_balance = 1050.0
        
        ea.record_trade_result(profit=50.0, is_win=True)
        
        assert ea.stats.winning_trades == 1
        assert ea.stats.total_profit == 50.0
        assert ea.stats.consecutive_wins == 1
        assert ea.stats.consecutive_losses == 0
    
    def test_record_losing_trade(self, ea):
        """Test recording a losing trade"""
        ea.stats.start_balance = 1000.0
        ea.stats.current_balance = 950.0
        
        ea.record_trade_result(profit=-50.0, is_win=False)
        
        assert ea.stats.losing_trades == 1
        assert ea.stats.total_loss == 50.0
        assert ea.stats.consecutive_losses == 1
        assert ea.stats.consecutive_wins == 0
        assert ea.last_loss_time is not None
    
    def test_get_stats(self, ea):
        """Test getting EA statistics"""
        ea.stats.total_trades = 10
        ea.stats.winning_trades = 7
        
        stats = ea.get_stats()
        
        assert stats["total_trades"] == 10
        assert stats["winning_trades"] == 7
        assert stats["win_rate"] == 70.0
        assert "market_condition" in stats
        assert "open_trades" in stats
    
    def test_get_config_summary(self, ea):
        """Test getting config summary"""
        summary = ea.get_config_summary()
        
        assert "V75 Expert Advisor Configuration" in summary
        assert "Lot Size:" in summary
        assert "Stop Loss:" in summary
        assert "Take Profit:" in summary
        assert "Risk Management:" in summary
    
    def test_reset_daily_stats(self, ea):
        """Test resetting daily statistics"""
        ea.stats.daily_profit = 100.0
        ea.stats.daily_loss = 50.0
        
        ea.reset_daily_stats()
        
        assert ea.stats.daily_profit == 0.0
        assert ea.stats.daily_loss == 0.0


class TestV75EAManager:
    """Tests for V75EAManager class"""
    
    @pytest.fixture
    def manager(self):
        """Create an EA manager for testing"""
        return V75EAManager()
    
    @pytest.fixture
    def mock_api(self):
        """Create a mock API"""
        api = Mock()
        api.buy_contract = AsyncMock()
        api.get_ticks = AsyncMock()
        return api
    
    def test_create_ea(self, manager, mock_api):
        """Test creating an EA"""
        ea = manager.create_ea(user_id=12345, user_api=mock_api)
        
        assert ea is not None
        assert ea.user_id == 12345
        assert 12345 in manager.active_eas
    
    def test_get_ea(self, manager, mock_api):
        """Test getting an EA"""
        manager.create_ea(user_id=12345, user_api=mock_api)
        
        ea = manager.get_ea(12345)
        assert ea is not None
        assert ea.user_id == 12345
        
        missing_ea = manager.get_ea(99999)
        assert missing_ea is None
    
    def test_start_ea(self, manager, mock_api):
        """Test starting an EA"""
        manager.create_ea(user_id=12345, user_api=mock_api)
        
        result = manager.start_ea(12345, start_balance=1000.0)
        
        assert result is True
        ea = manager.get_ea(12345)
        assert ea.is_active is True
        assert ea.stats.start_balance == 1000.0
    
    def test_start_ea_not_found(self, manager):
        """Test starting non-existent EA"""
        result = manager.start_ea(99999)
        assert result is False
    
    def test_stop_ea(self, manager, mock_api):
        """Test stopping an EA"""
        manager.create_ea(user_id=12345, user_api=mock_api)
        manager.start_ea(12345)
        
        result = manager.stop_ea(12345)
        
        assert result is True
        assert 12345 not in manager.active_eas
    
    def test_stop_ea_not_found(self, manager):
        """Test stopping non-existent EA"""
        result = manager.stop_ea(99999)
        assert result is False
    
    def test_get_all_stats(self, manager, mock_api):
        """Test getting stats for all EAs"""
        manager.create_ea(user_id=12345, user_api=mock_api)
        manager.create_ea(user_id=67890, user_api=mock_api)
        
        stats = manager.get_all_stats()
        
        assert 12345 in stats
        assert 67890 in stats


class TestConvenienceFunctions:
    """Tests for module-level convenience functions"""
    
    @pytest.fixture
    def mock_api(self):
        """Create a mock API"""
        api = Mock()
        api.buy_contract = AsyncMock()
        api.get_ticks = AsyncMock()
        return api
    
    def test_create_v75_ea_function(self, mock_api):
        """Test create_v75_ea convenience function"""
        ea = create_v75_ea(user_id=11111, user_api=mock_api)
        
        assert ea is not None
        assert ea.user_id == 11111
    
    def test_start_stop_v75_ea_functions(self, mock_api):
        """Test start and stop convenience functions"""
        create_v75_ea(user_id=22222, user_api=mock_api)
        
        result = start_v75_ea(22222, start_balance=500.0)
        assert result is True
        
        ea = get_v75_ea(22222)
        assert ea.is_active is True
        
        result = stop_v75_ea(22222)
        assert result is True
    
    def test_get_v75_ea_stats_function(self, mock_api):
        """Test get_v75_ea_stats convenience function"""
        create_v75_ea(user_id=33333, user_api=mock_api)
        
        stats = get_v75_ea_stats(33333)
        
        assert stats is not None
        assert "total_trades" in stats
        assert "win_rate" in stats


class TestTradeSignal:
    """Tests for TradeSignal dataclass"""
    
    def test_trade_signal_creation(self):
        """Test creating a trade signal"""
        signal = TradeSignal(
            direction=TradeDirection.CALL,
            strength=0.8,
            reason="Test signal",
            entry_price=5000.0,
            stop_loss=4950.0,
            take_profit=5100.0
        )
        
        assert signal.direction == TradeDirection.CALL
        assert signal.strength == 0.8
        assert signal.entry_price == 5000.0
        assert signal.stop_loss == 4950.0
        assert signal.take_profit == 5100.0
    
    def test_trade_signal_default_values(self):
        """Test trade signal default values"""
        signal = TradeSignal(
            direction=TradeDirection.PUT,
            strength=0.5,
            reason="Test",
            entry_price=5000.0,
            stop_loss=5050.0,
            take_profit=4900.0
        )
        
        assert signal.market_condition == MarketCondition.RANGING
        assert signal.timestamp is not None


class TestMarketConditionEnum:
    """Tests for MarketCondition enumeration"""
    
    def test_market_conditions(self):
        """Test all market condition values"""
        assert MarketCondition.TRENDING_UP.value == "trending_up"
        assert MarketCondition.TRENDING_DOWN.value == "trending_down"
        assert MarketCondition.RANGING.value == "ranging"
        assert MarketCondition.HIGH_VOLATILITY.value == "high_volatility"
        assert MarketCondition.LOW_VOLATILITY.value == "low_volatility"
        assert MarketCondition.BREAKOUT.value == "breakout"


class TestTradeDirectionEnum:
    """Tests for TradeDirection enumeration"""
    
    def test_trade_directions(self):
        """Test all trade direction values"""
        assert TradeDirection.CALL.value == "CALL"
        assert TradeDirection.PUT.value == "PUT"
        assert TradeDirection.NONE.value == "NONE"


if __name__ == "__main__":
    print("🧪 Running V75 Expert Advisor Tests")
    print("=" * 50)
    
    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])
