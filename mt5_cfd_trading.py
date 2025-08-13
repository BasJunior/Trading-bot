#!/usr/bin/env python3
"""
MT5 CFD Trading Module for Deriv Telegram Bot
Adds CFD and Multiplier trading capabilities through MetaTrader 5
"""

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    print("✅ Real MetaTrader5 module loaded")
except ImportError:
    try:
        import mock_mt5 as mt5
        MT5_AVAILABLE = True
        print("🔧 Using Mock MT5 for development/testing")
    except ImportError:
        MT5_AVAILABLE = False
        print("❌ No MT5 module available")

import pandas as pd
import numpy as np
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import threading
import time
from enum import Enum

logger = logging.getLogger(__name__)

class OrderType(Enum):
    """Order types for MT5"""
    BUY = mt5.ORDER_TYPE_BUY
    SELL = mt5.ORDER_TYPE_SELL
    BUY_STOP = mt5.ORDER_TYPE_BUY_STOP
    SELL_STOP = mt5.ORDER_TYPE_SELL_STOP
    BUY_LIMIT = mt5.ORDER_TYPE_BUY_LIMIT
    SELL_LIMIT = mt5.ORDER_TYPE_SELL_LIMIT

class TimeFrame(Enum):
    """Time frames for MT5"""
    M1 = mt5.TIMEFRAME_M1
    M5 = mt5.TIMEFRAME_M5
    M15 = mt5.TIMEFRAME_M15
    M30 = mt5.TIMEFRAME_M30
    H1 = mt5.TIMEFRAME_H1
    H4 = mt5.TIMEFRAME_H4
    D1 = mt5.TIMEFRAME_D1

@dataclass
class TradeResult:
    """Result of a trade operation"""
    success: bool
    ticket: Optional[int] = None
    price: Optional[float] = None
    volume: Optional[float] = None
    comment: Optional[str] = None
    error_code: Optional[int] = None
    error_description: Optional[str] = None

@dataclass
class Position:
    """MT5 Position information"""
    ticket: int
    symbol: str
    type: int
    volume: float
    price_open: float
    price_current: float
    profit: float
    swap: float
    comment: str
    time: datetime

@dataclass
class MarketInfo:
    """Market information for a symbol"""
    symbol: str
    bid: float
    ask: float
    spread: float
    digits: int
    point: float
    min_lot: float
    max_lot: float
    lot_step: float
    margin_required: float

class MT5CFDTrader:
    """MT5 CFD Trading interface for Deriv"""
    
    def __init__(self, login: int, password: str, server: str):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False
        self.account_info = None
        
    def connect(self) -> bool:
        """Connect to MT5 terminal"""
        try:
            # Initialize MT5
            if not mt5.initialize():
                logger.error(f"MT5 initialize() failed, error code = {mt5.last_error()}")
                return False
            
            # Connect to account
            if not mt5.login(self.login, password=self.password, server=self.server):
                logger.error(f"Failed to connect to MT5 account {self.login}, error code = {mt5.last_error()}")
                mt5.shutdown()
                return False
            
            self.connected = True
            self.account_info = mt5.account_info()
            logger.info(f"✅ Connected to MT5 account {self.login}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to MT5: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("🔌 Disconnected from MT5")
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.connected:
            return {}
        
        info = mt5.account_info()
        if info is None:
            return {}
        
        return {
            "login": info.login,
            "balance": info.balance,
            "equity": info.equity,
            "profit": info.profit,
            "margin": info.margin,
            "margin_free": info.margin_free,
            "margin_level": info.margin_level,
            "currency": info.currency,
            "company": info.company,
            "server": info.server
        }
    
    def get_symbol_info(self, symbol: str) -> Optional[MarketInfo]:
        """Get symbol information"""
        if not self.connected:
            return None
        
        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Symbol {symbol} not found")
            return None
        
        # Get current tick
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            logger.error(f"Failed to get tick for {symbol}")
            return None
        
        return MarketInfo(
            symbol=symbol,
            bid=tick.bid,
            ask=tick.ask,
            spread=tick.ask - tick.bid,
            digits=symbol_info.digits,
            point=symbol_info.point,
            min_lot=symbol_info.volume_min,
            max_lot=symbol_info.volume_max,
            lot_step=symbol_info.volume_step,
            margin_required=symbol_info.margin_initial
        )
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available trading symbols"""
        if not self.connected:
            return []
        
        symbols = mt5.symbols_get()
        if symbols is None:
            return []
        
        # Filter for common CFD symbols
        cfd_symbols = []
        for symbol in symbols:
            symbol_name = symbol.name
            # Include major forex, indices, commodities, and crypto CFDs
            if any(market in symbol_name for market in [
                'EUR', 'USD', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD',  # Forex
                'US30', 'US500', 'NAS100', 'GER40', 'UK100', 'FRA40', 'JPN225',  # Indices
                'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL',  # Commodities
                'BTCUSD', 'ETHUSD', 'LTCUSD'  # Crypto
            ]):
                cfd_symbols.append(symbol_name)
        
        return sorted(cfd_symbols[:50])  # Return top 50
    
    def open_position(self, symbol: str, order_type: OrderType, volume: float, 
                     sl: float = 0, tp: float = 0, comment: str = "") -> TradeResult:
        """Open a new position"""
        if not self.connected:
            return TradeResult(success=False, error_description="Not connected to MT5")
        
        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return TradeResult(success=False, error_description=f"Symbol {symbol} not found")
        
        # Check if symbol is available for trading
        if not symbol_info.visible:
            # Try to enable symbol
            if not mt5.symbol_select(symbol, True):
                return TradeResult(success=False, error_description=f"Failed to select symbol {symbol}")
        
        # Get current price
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return TradeResult(success=False, error_description=f"Failed to get price for {symbol}")
        
        # Determine price based on order type
        if order_type == OrderType.BUY:
            price = tick.ask
        else:
            price = tick.bid
        
        # Prepare trade request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type.value,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send trade request
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return TradeResult(
                success=False,
                error_code=result.retcode,
                error_description=f"Trade failed: {result.comment}"
            )
        
        return TradeResult(
            success=True,
            ticket=result.order,
            price=result.price,
            volume=result.volume,
            comment=f"Position opened: {symbol} {order_type.name} {volume} lots"
        )
    
    def close_position(self, ticket: int) -> TradeResult:
        """Close an existing position"""
        if not self.connected:
            return TradeResult(success=False, error_description="Not connected to MT5")
        
        # Get position info
        position = mt5.positions_get(ticket=ticket)
        if position is None or len(position) == 0:
            return TradeResult(success=False, error_description=f"Position {ticket} not found")
        
        position = position[0]
        
        # Determine close order type
        if position.type == mt5.POSITION_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(position.symbol).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(position.symbol).ask
        
        # Prepare close request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": f"Close position {ticket}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send close request
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return TradeResult(
                success=False,
                error_code=result.retcode,
                error_description=f"Close failed: {result.comment}"
            )
        
        return TradeResult(
            success=True,
            ticket=result.order,
            price=result.price,
            volume=result.volume,
            comment=f"Position closed: {position.symbol}"
        )
    
    def get_positions(self) -> List[Position]:
        """Get all open positions"""
        if not self.connected:
            return []
        
        positions = mt5.positions_get()
        if positions is None:
            return []
        
        result = []
        for pos in positions:
            result.append(Position(
                ticket=pos.ticket,
                symbol=pos.symbol,
                type=pos.type,
                volume=pos.volume,
                price_open=pos.price_open,
                price_current=pos.price_current,
                profit=pos.profit,
                swap=pos.swap,
                comment=pos.comment,
                time=datetime.fromtimestamp(pos.time)
            ))
        
        return result
    
    def get_history(self, symbol: str, timeframe: TimeFrame, count: int = 100) -> pd.DataFrame:
        """Get historical price data"""
        if not self.connected:
            return pd.DataFrame()
        
        # Get rates
        rates = mt5.copy_rates_from_pos(symbol, timeframe.value, 0, count)
        if rates is None:
            logger.error(f"Failed to get rates for {symbol}")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        return df

class DerivMT5Integration:
    """Integration class to add MT5 CFD trading to Deriv Telegram Bot"""
    
    def __init__(self, mt5_login: int = None, mt5_password: str = None, mt5_server: str = None):
        self.mt5_trader = None
        self.mt5_login = mt5_login
        self.mt5_password = mt5_password
        self.mt5_server = mt5_server
        self.user_mt5_accounts = {}  # user_id -> MT5CFDTrader
        
    def setup_user_mt5(self, user_id: int, login: int, password: str, server: str) -> bool:
        """Setup MT5 connection for a user"""
        try:
            trader = MT5CFDTrader(login, password, server)
            if trader.connect():
                self.user_mt5_accounts[user_id] = trader
                logger.info(f"✅ MT5 setup successful for user {user_id}")
                return True
            else:
                logger.error(f"❌ MT5 setup failed for user {user_id}")
                return False
        except Exception as e:
            logger.error(f"Error setting up MT5 for user {user_id}: {e}")
            return False
    
    def get_user_mt5(self, user_id: int) -> Optional[MT5CFDTrader]:
        """Get MT5 trader for a user"""
        return self.user_mt5_accounts.get(user_id)
    
    def remove_user_mt5(self, user_id: int):
        """Remove MT5 connection for a user"""
        if user_id in self.user_mt5_accounts:
            self.user_mt5_accounts[user_id].disconnect()
            del self.user_mt5_accounts[user_id]
            logger.info(f"🔌 MT5 connection removed for user {user_id}")
    
    async def place_cfd_trade(self, user_id: int, symbol: str, direction: str, 
                             volume: float, sl: float = 0, tp: float = 0) -> TradeResult:
        """Place a CFD trade for a user"""
        trader = self.get_user_mt5(user_id)
        if not trader:
            return TradeResult(success=False, error_description="MT5 not configured for this user")
        
        # Determine order type
        order_type = OrderType.BUY if direction.upper() == "BUY" else OrderType.SELL
        
        # Place trade
        result = trader.open_position(symbol, order_type, volume, sl, tp, f"Telegram Bot Trade")
        
        return result
    
    async def close_cfd_trade(self, user_id: int, ticket: int) -> TradeResult:
        """Close a CFD trade for a user"""
        trader = self.get_user_mt5(user_id)
        if not trader:
            return TradeResult(success=False, error_description="MT5 not configured for this user")
        
        return trader.close_position(ticket)
    
    def get_user_cfd_positions(self, user_id: int) -> List[Position]:
        """Get CFD positions for a user"""
        trader = self.get_user_mt5(user_id)
        if not trader:
            return []
        
        return trader.get_positions()
    
    def get_user_account_info(self, user_id: int) -> Dict:
        """Get MT5 account info for a user"""
        trader = self.get_user_mt5(user_id)
        if not trader:
            return {}
        
        return trader.get_account_info()

# Global MT5 integration instance
mt5_integration = DerivMT5Integration()

# Convenience functions for the Telegram bot
async def setup_user_mt5_account(user_id: int, login: int, password: str, server: str) -> bool:
    """Setup MT5 account for a user"""
    return mt5_integration.setup_user_mt5(user_id, login, password, server)

async def place_cfd_trade(user_id: int, symbol: str, direction: str, volume: float, 
                         sl: float = 0, tp: float = 0) -> TradeResult:
    """Place CFD trade"""
    return await mt5_integration.place_cfd_trade(user_id, symbol, direction, volume, sl, tp)

async def close_cfd_trade(user_id: int, ticket: int) -> TradeResult:
    """Close CFD trade"""
    return await mt5_integration.close_cfd_trade(user_id, ticket)

def get_cfd_positions(user_id: int) -> List[Position]:
    """Get CFD positions"""
    return mt5_integration.get_user_cfd_positions(user_id)

def get_mt5_account_info(user_id: int) -> Dict:
    """Get MT5 account info"""
    return mt5_integration.get_user_account_info(user_id)

if __name__ == "__main__":
    # Test the MT5 CFD trading module
    print("🧪 Testing MT5 CFD Trading Module...")
    
    # This would require actual MT5 credentials
    # trader = MT5CFDTrader(login=12345, password="password", server="server")
    # if trader.connect():
    #     print("✅ MT5 connection successful")
    #     print(f"Account info: {trader.get_account_info()}")
    #     print(f"Available symbols: {trader.get_available_symbols()[:10]}")
    #     trader.disconnect()
    # else:
    #     print("❌ MT5 connection failed")
    
    print("📖 MT5 CFD Trading module ready for integration")
    print("🔗 To use: Import this module in your telegram_bot.py")
    print("💡 Requires MetaTrader 5 installation and valid account credentials")