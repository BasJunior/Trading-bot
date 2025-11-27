#!/usr/bin/env python3
"""
Step System Utilities for Deriv Telegram Bot
Provides utility functions for step-based trading strategies
including Step Index and Volatility Index trading
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TradingSignal(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class SignalResult:
    """Result of a trading signal calculation"""
    signal: TradingSignal
    confidence: float  # 0-1 scale
    indicator_values: Dict[str, Any]
    reason: str


class StepSystemUtilities:
    """
    Utilities for step-based trading systems.
    Provides common calculations for Step Index and Volatility Index strategies.
    """
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int = 20) -> Optional[np.ndarray]:
        """
        Calculate Exponential Moving Average
        
        Args:
            prices: List of price values
            period: EMA period (default 20)
            
        Returns:
            numpy array of EMA values or None if insufficient data
        """
        if len(prices) < period:
            return None
        
        try:
            import talib as ta
            return ta.EMA(np.array(prices, dtype=float), timeperiod=period)
        except ImportError:
            # Fallback calculation without TA-Lib
            prices_arr = np.array(prices, dtype=float)
            ema = np.zeros(len(prices_arr))
            multiplier = 2 / (period + 1)
            
            # Initial SMA
            ema[:period] = np.nan
            ema[period - 1] = np.mean(prices_arr[:period])
            
            # Calculate EMA
            for i in range(period, len(prices_arr)):
                ema[i] = (prices_arr[i] - ema[i - 1]) * multiplier + ema[i - 1]
            
            return ema
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[np.ndarray]:
        """
        Calculate Relative Strength Index
        
        Args:
            prices: List of price values
            period: RSI period (default 14)
            
        Returns:
            numpy array of RSI values or None if insufficient data
        """
        if len(prices) < period + 1:
            return None
        
        try:
            import talib as ta
            return ta.RSI(np.array(prices, dtype=float), timeperiod=period)
        except ImportError:
            # Fallback calculation without TA-Lib
            prices_arr = np.array(prices, dtype=float)
            deltas = np.diff(prices_arr)
            
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.zeros(len(prices_arr))
            avg_loss = np.zeros(len(prices_arr))
            
            # Initial averages
            avg_gain[period] = np.mean(gains[:period])
            avg_loss[period] = np.mean(losses[:period])
            
            # Calculate subsequent averages
            for i in range(period + 1, len(prices_arr)):
                avg_gain[i] = (avg_gain[i - 1] * (period - 1) + gains[i - 1]) / period
                avg_loss[i] = (avg_loss[i - 1] * (period - 1) + losses[i - 1]) / period
            
            # Calculate RSI
            rs = np.divide(avg_gain, avg_loss, out=np.zeros_like(avg_gain), where=avg_loss != 0)
            rsi = 100 - (100 / (1 + rs))
            rsi[:period] = np.nan
            
            return rsi
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Calculate Bollinger Bands
        
        Args:
            prices: List of price values
            period: Period for moving average (default 20)
            std_dev: Standard deviation multiplier (default 2.0)
            
        Returns:
            Tuple of (upper, middle, lower) bands or (None, None, None) if insufficient data
        """
        if len(prices) < period:
            return None, None, None
        
        try:
            import talib as ta
            return ta.BBANDS(np.array(prices, dtype=float), timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)
        except ImportError:
            # Fallback calculation without TA-Lib
            prices_arr = np.array(prices, dtype=float)
            
            middle = np.full(len(prices_arr), np.nan)
            upper = np.full(len(prices_arr), np.nan)
            lower = np.full(len(prices_arr), np.nan)
            
            for i in range(period - 1, len(prices_arr)):
                window = prices_arr[i - period + 1:i + 1]
                middle[i] = np.mean(window)
                std = np.std(window)
                upper[i] = middle[i] + std_dev * std
                lower[i] = middle[i] - std_dev * std
            
            return upper, middle, lower
    
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: List of price values
            fast_period: Fast EMA period (default 12)
            slow_period: Slow EMA period (default 26)
            signal_period: Signal line period (default 9)
            
        Returns:
            Tuple of (macd, signal, histogram) or (None, None, None) if insufficient data
        """
        if len(prices) < slow_period:
            return None, None, None
        
        try:
            import talib as ta
            return ta.MACD(np.array(prices, dtype=float), fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)
        except ImportError:
            # Fallback calculation without TA-Lib
            fast_ema = StepSystemUtilities.calculate_ema(prices, fast_period)
            slow_ema = StepSystemUtilities.calculate_ema(prices, slow_period)
            
            if fast_ema is None or slow_ema is None:
                return None, None, None
            
            macd_line = fast_ema - slow_ema
            
            # Calculate signal line as EMA of MACD line
            signal_line = StepSystemUtilities.calculate_ema(macd_line.tolist(), signal_period)
            
            if signal_line is None:
                return None, None, None
            
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram


def calculate_step_signal(prices: List[float], ema_period: int = 20, rsi_period: int = 14,
                         rsi_oversold: float = 30, rsi_overbought: float = 70) -> SignalResult:
    """
    Calculate trading signal for Step Index strategy using EMA + RSI
    
    This is the standard step-based scalping signal calculation used for:
    - Step Index 100
    - Step Index 200
    - Step Index 500
    
    Args:
        prices: List of historical prices
        ema_period: Period for EMA calculation
        rsi_period: Period for RSI calculation
        rsi_oversold: RSI oversold threshold
        rsi_overbought: RSI overbought threshold
        
    Returns:
        SignalResult with trading signal and details
    """
    utils = StepSystemUtilities()
    
    # Check for sufficient data
    min_required = max(ema_period, rsi_period)
    if len(prices) < min_required:
        return SignalResult(
            signal=TradingSignal.HOLD,
            confidence=0.0,
            indicator_values={},
            reason=f"Insufficient data: need {min_required} prices, have {len(prices)}"
        )
    
    # Calculate indicators
    ema = utils.calculate_ema(prices, ema_period)
    rsi = utils.calculate_rsi(prices, rsi_period)
    
    if ema is None or rsi is None:
        return SignalResult(
            signal=TradingSignal.HOLD,
            confidence=0.0,
            indicator_values={},
            reason="Failed to calculate indicators"
        )
    
    current_price = prices[-1]
    current_ema = ema[-1]
    current_rsi = rsi[-1]
    
    indicator_values = {
        "price": current_price,
        "ema": current_ema,
        "rsi": current_rsi,
        "ema_period": ema_period,
        "rsi_period": rsi_period
    }
    
    # BUY signal: Price above EMA and RSI oversold (bounce expected)
    if current_price > current_ema and current_rsi < rsi_oversold:
        confidence = min((rsi_oversold - current_rsi) / rsi_oversold, 1.0)
        return SignalResult(
            signal=TradingSignal.BUY,
            confidence=confidence,
            indicator_values=indicator_values,
            reason=f"Price above EMA ({current_price:.4f} > {current_ema:.4f}) and RSI oversold ({current_rsi:.1f} < {rsi_oversold})"
        )
    
    # SELL signal: Price below EMA and RSI overbought (drop expected)
    if current_price < current_ema and current_rsi > rsi_overbought:
        confidence = min((current_rsi - rsi_overbought) / (100 - rsi_overbought), 1.0)
        return SignalResult(
            signal=TradingSignal.SELL,
            confidence=confidence,
            indicator_values=indicator_values,
            reason=f"Price below EMA ({current_price:.4f} < {current_ema:.4f}) and RSI overbought ({current_rsi:.1f} > {rsi_overbought})"
        )
    
    # HOLD signal
    return SignalResult(
        signal=TradingSignal.HOLD,
        confidence=0.0,
        indicator_values=indicator_values,
        reason=f"No clear signal: Price vs EMA: {current_price:.4f}/{current_ema:.4f}, RSI: {current_rsi:.1f}"
    )


def calculate_volatility_signal(prices: List[float], ema_period: int = 20, rsi_period: int = 14,
                                rsi_oversold: float = 30, rsi_overbought: float = 70) -> SignalResult:
    """
    Calculate trading signal for Volatility Index strategy using EMA + RSI
    
    This uses the same model as the Step Index strategy, suitable for:
    - Volatility 75 Index (R_75)
    - Volatility 100 Index (R_100)
    - Volatility 50 Index (R_50)
    - Volatility 25 Index (R_25)
    - Volatility 10 Index (R_10)
    
    Args:
        prices: List of historical prices
        ema_period: Period for EMA calculation
        rsi_period: Period for RSI calculation
        rsi_oversold: RSI oversold threshold
        rsi_overbought: RSI overbought threshold
        
    Returns:
        SignalResult with trading signal and details
    """
    # Use the same logic as step signal - this creates consistency
    # across both Step Index and Volatility Index scalping strategies
    return calculate_step_signal(prices, ema_period, rsi_period, rsi_oversold, rsi_overbought)


def validate_trading_parameters(symbol: str, lot_size: float, max_lot_size: float = 100.0,
                                 min_lot_size: float = 0.001) -> Tuple[bool, str]:
    """
    Validate trading parameters before placing a trade
    
    Args:
        symbol: Trading symbol
        lot_size: Requested lot size
        max_lot_size: Maximum allowed lot size
        min_lot_size: Minimum allowed lot size
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate symbol
    valid_prefixes = ["R_", "STEP_", "BOOM", "CRASH", "1HZ", "JD"]
    if not any(symbol.startswith(prefix) for prefix in valid_prefixes):
        return False, f"Invalid symbol: {symbol}. Must start with one of {valid_prefixes}"
    
    # Validate lot size
    if lot_size < min_lot_size:
        return False, f"Lot size too small: {lot_size}. Minimum is {min_lot_size}"
    
    if lot_size > max_lot_size:
        return False, f"Lot size too large: {lot_size}. Maximum is {max_lot_size}"
    
    return True, "Parameters valid"


def get_recommended_lot_sizes(strategy_type: str, account_balance: float = None) -> List[float]:
    """
    Get recommended lot sizes for a strategy type
    
    Args:
        strategy_type: Type of strategy ("scalping" or "swing")
        account_balance: Optional account balance for personalized recommendations
        
    Returns:
        List of recommended lot sizes
    """
    if strategy_type.lower() == "scalping":
        # Scalping: Smaller, more frequent trades
        base_lots = [0.1, 0.2, 0.5, 1.0, 2.0]
    else:
        # Swing: Larger trades held longer
        base_lots = [0.001, 0.01, 0.1, 0.5, 1.0]
    
    # Adjust based on account balance if provided
    if account_balance is not None and account_balance > 0:
        # Never risk more than 2% per trade
        max_risk = account_balance * 0.02
        base_lots = [lot for lot in base_lots if lot <= max_risk]
        if not base_lots:
            base_lots = [min(0.01, max_risk)]
    
    return base_lots
