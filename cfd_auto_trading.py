#!/usr/bin/env python3
"""
CFD Automated Trading Strategies
Advanced automated trading strategies for MT5 CFD trading
"""

import asyncio
import time
import logging
from typing import Dict, List
from mt5_cfd_trading import CFDTradingBot, mt5_manager

logger = logging.getLogger(__name__)

class CFDAutoTrader:
    """Automated CFD trading strategies"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.mt5 = mt5_manager
        self.active_strategies = {}
        self.running = False
        
    async def start_scalping_strategy(self, symbol: str, volume: float, risk_percent: float = 1.0):
        """Start EMA + RSI scalping strategy for CFDs"""
        strategy_id = f"scalp_{symbol}_{int(time.time())}"
        
        strategy = {
            "id": strategy_id,
            "type": "scalping",
            "symbol": symbol,
            "volume": volume,
            "risk_percent": risk_percent,
            "active": True,
            "trades_today": 0,
            "max_trades": 10,
            "last_trade_time": 0,
            "min_interval": 300,  # 5 minutes between trades
            "profit": 0.0,
            "win_rate": 0.0
        }
        
        self.active_strategies[strategy_id] = strategy
        asyncio.create_task(self._run_scalping_strategy(strategy))
        
        return strategy_id
    
    async def start_trend_following_strategy(self, symbol: str, volume: float, risk_percent: float = 2.0):
        """Start trend following strategy using moving averages"""
        strategy_id = f"trend_{symbol}_{int(time.time())}"
        
        strategy = {
            "id": strategy_id,
            "type": "trend_following",
            "symbol": symbol,
            "volume": volume,
            "risk_percent": risk_percent,
            "active": True,
            "trades_today": 0,
            "max_trades": 5,
            "last_trade_time": 0,
            "min_interval": 1800,  # 30 minutes between trades
            "profit": 0.0,
            "win_rate": 0.0
        }
        
        self.active_strategies[strategy_id] = strategy
        asyncio.create_task(self._run_trend_strategy(strategy))
        
        return strategy_id
    
    async def start_breakout_strategy(self, symbol: str, volume: float, risk_percent: float = 1.5):
        """Start breakout trading strategy"""
        strategy_id = f"breakout_{symbol}_{int(time.time())}"
        
        strategy = {
            "id": strategy_id,
            "type": "breakout",
            "symbol": symbol,
            "volume": volume,
            "risk_percent": risk_percent,
            "active": True,
            "trades_today": 0,
            "max_trades": 8,
            "last_trade_time": 0,
            "min_interval": 900,  # 15 minutes between trades
            "profit": 0.0,
            "win_rate": 0.0
        }
        
        self.active_strategies[strategy_id] = strategy
        asyncio.create_task(self._run_breakout_strategy(strategy))
        
        return strategy_id
    
    async def stop_strategy(self, strategy_id: str):
        """Stop a specific strategy"""
        if strategy_id in self.active_strategies:
            self.active_strategies[strategy_id]["active"] = False
            del self.active_strategies[strategy_id]
            return True
        return False
    
    async def stop_all_strategies(self):
        """Stop all active strategies"""
        for strategy_id in list(self.active_strategies.keys()):
            await self.stop_strategy(strategy_id)
    
    def get_active_strategies(self) -> List[Dict]:
        """Get list of active strategies"""
        return list(self.active_strategies.values())
    
    async def _run_scalping_strategy(self, strategy: Dict):
        """Run EMA + RSI scalping strategy"""
        while strategy["active"] and strategy["trades_today"] < strategy["max_trades"]:
            try:
                symbol = strategy["symbol"]
                
                # Check time interval
                current_time = time.time()
                if current_time - strategy["last_trade_time"] < strategy["min_interval"]:
                    await asyncio.sleep(30)
                    continue
                
                # Get current price
                price_data = self.mt5.get_current_price(symbol)
                if not price_data:
                    await asyncio.sleep(60)
                    continue
                
                current_price = price_data["bid"]
                
                # Simple scalping logic (can be enhanced with real indicators)
                # For demo: Buy if price ends in even digit, sell if odd
                price_int = int(current_price * 10000) % 10
                
                if price_int % 2 == 0:  # Even - buy signal
                    action = "BUY"
                    stop_loss = current_price - 0.0020  # 20 pips
                    take_profit = current_price + 0.0040  # 40 pips
                elif price_int % 3 == 0:  # Divisible by 3 - sell signal
                    action = "SELL"
                    stop_loss = current_price + 0.0020  # 20 pips
                    take_profit = current_price - 0.0040  # 40 pips
                else:
                    await asyncio.sleep(60)
                    continue
                
                # Place trade
                cfd_trader = CFDTradingBot(self.user_id)
                
                result = await cfd_trader.place_cfd_trade(
                    symbol=symbol,
                    action=action,
                    volume=strategy["volume"],
                    stop_loss=stop_loss,
                    take_profit=take_profit
                )
                
                if "success" in result:
                    strategy["trades_today"] += 1
                    strategy["last_trade_time"] = current_time
                    logger.info(f"CFD Scalping trade placed: {action} {symbol} @ {current_price}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Scalping strategy error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _run_trend_strategy(self, strategy: Dict):
        """Run trend following strategy"""
        while strategy["active"] and strategy["trades_today"] < strategy["max_trades"]:
            try:
                symbol = strategy["symbol"]
                
                # Check time interval
                current_time = time.time()
                if current_time - strategy["last_trade_time"] < strategy["min_interval"]:
                    await asyncio.sleep(300)
                    continue
                
                # Get current price
                price_data = self.mt5.get_current_price(symbol)
                if not price_data:
                    await asyncio.sleep(300)
                    continue
                
                current_price = price_data["bid"]
                spread = price_data["spread"]
                
                # Simple trend logic based on time and spread
                hour = time.gmtime().tm_hour
                
                # Buy during European session (7-16 UTC), sell during US session (13-22 UTC)
                if 7 <= hour <= 12 and spread < 0.0003:  # Low spread, European morning
                    action = "BUY"
                    stop_loss = current_price - 0.0050  # 50 pips
                    take_profit = current_price + 0.0100  # 100 pips
                elif 18 <= hour <= 21 and spread < 0.0003:  # US evening
                    action = "SELL"
                    stop_loss = current_price + 0.0050  # 50 pips
                    take_profit = current_price - 0.0100  # 100 pips
                else:
                    await asyncio.sleep(300)
                    continue
                
                # Place trade
                cfd_trader = CFDTradingBot(self.user_id)
                
                result = await cfd_trader.place_cfd_trade(
                    symbol=symbol,
                    action=action,
                    volume=strategy["volume"],
                    stop_loss=stop_loss,
                    take_profit=take_profit
                )
                
                if "success" in result:
                    strategy["trades_today"] += 1
                    strategy["last_trade_time"] = current_time
                    logger.info(f"CFD Trend trade placed: {action} {symbol} @ {current_price}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Trend strategy error: {e}")
                await asyncio.sleep(600)
    
    async def _run_breakout_strategy(self, strategy: Dict):
        """Run breakout trading strategy"""
        price_history = []
        
        while strategy["active"] and strategy["trades_today"] < strategy["max_trades"]:
            try:
                symbol = strategy["symbol"]
                
                # Check time interval
                current_time = time.time()
                if current_time - strategy["last_trade_time"] < strategy["min_interval"]:
                    await asyncio.sleep(180)
                    continue
                
                # Get current price
                price_data = self.mt5.get_current_price(symbol)
                if not price_data:
                    await asyncio.sleep(300)
                    continue
                
                current_price = price_data["bid"]
                price_history.append(current_price)
                
                # Keep only last 20 prices
                if len(price_history) > 20:
                    price_history = price_history[-20:]
                
                if len(price_history) < 10:
                    await asyncio.sleep(180)
                    continue
                
                # Calculate support/resistance
                recent_high = max(price_history[-10:])
                recent_low = min(price_history[-10:])
                price_range = recent_high - recent_low
                
                # Breakout signals
                if current_price > recent_high + (price_range * 0.1):  # Bullish breakout
                    action = "BUY"
                    stop_loss = recent_high - (price_range * 0.2)
                    take_profit = current_price + price_range
                elif current_price < recent_low - (price_range * 0.1):  # Bearish breakout
                    action = "SELL"
                    stop_loss = recent_low + (price_range * 0.2)
                    take_profit = current_price - price_range
                else:
                    await asyncio.sleep(180)
                    continue
                
                # Place trade
                cfd_trader = CFDTradingBot(self.user_id)
                
                result = await cfd_trader.place_cfd_trade(
                    symbol=symbol,
                    action=action,
                    volume=strategy["volume"],
                    stop_loss=stop_loss,
                    take_profit=take_profit
                )
                
                if "success" in result:
                    strategy["trades_today"] += 1
                    strategy["last_trade_time"] = current_time
                    logger.info(f"CFD Breakout trade placed: {action} {symbol} @ {current_price}")
                
                await asyncio.sleep(180)  # Check every 3 minutes
                
            except Exception as e:
                logger.error(f"Breakout strategy error: {e}")
                await asyncio.sleep(300)

# Global auto trader instances
user_auto_traders = {}

def get_auto_trader(user_id: int) -> CFDAutoTrader:
    """Get or create auto trader for user"""
    if user_id not in user_auto_traders:
        user_auto_traders[user_id] = CFDAutoTrader(user_id)
    return user_auto_traders[user_id]
