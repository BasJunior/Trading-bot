#!/usr/bin/env python3
"""
Trading Strategies for Deriv Telegram Bot
Contains strategy implementations for Step Index and Volatility Index trading
"""

import logging
from typing import Optional
from collections import deque

from .utilities import (
    StepSystemUtilities,
    calculate_volatility_signal,
    TradingSignal,
)

logger = logging.getLogger(__name__)


class Volatility75ScalpingStrategy:
    """
    Volatility 75 Index scalping strategy using EMA + RSI
    
    This follows the same model as StepIndex100ScalpingStrategy,
    providing consistent scalping approach across both Step Index
    and Volatility Index markets.
    
    The strategy:
    - Uses EMA to determine trend direction
    - Uses RSI to identify overbought/oversold conditions
    - Buys CALL when price is above EMA and RSI is oversold (bounce expected)
    - Buys PUT when price is below EMA and RSI is overbought (drop expected)
    """
    
    def __init__(self, user_id: int, user_api, symbol: str = "R_75"):
        """
        Initialize Volatility 75 Scalping Strategy
        
        Args:
            user_id: Telegram user ID
            user_api: DerivAPI instance for this user
            symbol: Trading symbol (default "R_75")
        """
        self.user_id = user_id
        self.user_api = user_api
        self.symbol = symbol
        self.is_active = False
        
        # Price history for indicator calculations
        self.price_history = deque(maxlen=100)
        
        # Strategy parameters (same as Step Index 100)
        self.ema_period = 20
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        
        # Performance tracking
        self.trades_count = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        
        # Utilities for calculations
        self.indicators = StepSystemUtilities()
        
        logger.info(f"Volatility75ScalpingStrategy initialized for user {user_id} on {symbol}")
    
    async def add_price(self, price: float):
        """Add new price to history"""
        self.price_history.append(price)
    
    async def should_buy_call(self) -> bool:
        """
        Check if conditions are met for a CALL trade
        
        Returns True when:
        - Price is above EMA (uptrend)
        - RSI is oversold (bounce expected)
        """
        if len(self.price_history) < max(self.ema_period, self.rsi_period):
            return False
        
        prices = list(self.price_history)
        signal_result = calculate_volatility_signal(
            prices,
            ema_period=self.ema_period,
            rsi_period=self.rsi_period,
            rsi_oversold=self.rsi_oversold,
            rsi_overbought=self.rsi_overbought
        )
        
        return signal_result.signal == TradingSignal.BUY
    
    async def should_buy_put(self) -> bool:
        """
        Check if conditions are met for a PUT trade
        
        Returns True when:
        - Price is below EMA (downtrend)
        - RSI is overbought (drop expected)
        """
        if len(self.price_history) < max(self.ema_period, self.rsi_period):
            return False
        
        prices = list(self.price_history)
        signal_result = calculate_volatility_signal(
            prices,
            ema_period=self.ema_period,
            rsi_period=self.rsi_period,
            rsi_oversold=self.rsi_oversold,
            rsi_overbought=self.rsi_overbought
        )
        
        return signal_result.signal == TradingSignal.SELL
    
    async def place_trade(self, contract_type: str, amount: float = 1.0, duration: int = 5):
        """
        Place a trade using the Deriv API
        
        Note: This method is implemented here for modularity, allowing this strategy
        to be used independently of the telegram_bot module's TradingStrategy class.
        
        Args:
            contract_type: "CALL" or "PUT"
            amount: Trade amount in account currency
            duration: Contract duration in ticks
            
        Returns:
            True if trade was successful, False otherwise
        """
        try:
            response = await self.user_api.buy_contract(
                contract_type, 
                self.symbol, 
                amount, 
                duration, 
                "t"  # duration unit: ticks
            )
            
            if "buy" in response:
                self.trades_count += 1
                logger.info(f"Trade placed: {contract_type} on {self.symbol} for ${amount}")
                return True
            
            logger.warning(f"Trade failed: {response}")
            return False
            
        except Exception as e:
            logger.error(f"Trade placement error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        Get strategy performance statistics
        
        Returns:
            Dictionary with trades_count, winning_trades, win_rate, total_profit
        """
        win_rate = (self.winning_trades / self.trades_count * 100) if self.trades_count > 0 else 0
        return {
            "trades_count": self.trades_count,
            "winning_trades": self.winning_trades,
            "win_rate": win_rate,
            "total_profit": self.total_profit
        }
    
    def get_current_indicators(self) -> dict:
        """
        Get current indicator values for display
        
        Returns:
            Dictionary with current EMA, RSI values
        """
        if len(self.price_history) < max(self.ema_period, self.rsi_period):
            return {
                "ema": None,
                "rsi": None,
                "price": self.price_history[-1] if self.price_history else None
            }
        
        prices = list(self.price_history)
        
        ema = self.indicators.calculate_ema(prices, self.ema_period)
        rsi = self.indicators.calculate_rsi(prices, self.rsi_period)
        
        return {
            "ema": ema[-1] if ema is not None else None,
            "rsi": rsi[-1] if rsi is not None else None,
            "price": prices[-1]
        }
    
    def update_trade_result(self, profit: float):
        """
        Update strategy statistics with trade result
        
        Args:
            profit: Profit/loss from the trade
        """
        self.total_profit += profit
        if profit > 0:
            self.winning_trades += 1
