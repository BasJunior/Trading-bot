#!/usr/bin/env python3
"""
Deriv Telegram Bot
A Telegram bot for interacting with Deriv trading platform
"""

import os
import logging
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np
from collections import deque
import threading
import time
import pandas as pd
import talib as ta

import websockets
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from config import Config

# Debug print
import os
print(f"DEBUG: TELEGRAM_BOT_TOKEN = {os.getenv('TELEGRAM_BOT_TOKEN')}")
print(f"DEBUG: Config.TELEGRAM_BOT_TOKEN = {Config.TELEGRAM_BOT_TOKEN}")

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    exit(1)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DerivAPI:
    """Handler for Deriv API WebSocket connection"""
    
    def __init__(self, app_id: str, api_token: str = None):
        self.app_id = app_id
        self.api_token = api_token
        self.websocket = None
        self.is_connected = False
        self.request_id = 0
        
    async def connect(self):
        """Connect to Deriv WebSocket API"""
        try:
            uri = f"wss://ws.binaryws.com/websockets/v3?app_id={self.app_id}"
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            logger.info("Connected to Deriv API")
            
            # Authorize if token is provided
            if self.api_token:
                await self.authorize()
                
        except Exception as e:
            logger.error(f"Failed to connect to Deriv API: {e}")
            self.is_connected = False
            
    async def disconnect(self):
        """Disconnect from Deriv WebSocket API"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("Disconnected from Deriv API")
            
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to Deriv API and return response"""
        if not self.is_connected:
            await self.connect()
            
        self.request_id += 1
        request["req_id"] = self.request_id
        
        try:
            logger.debug(f"Sending request: {json.dumps(request, indent=2)}")
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            response_data = json.loads(response)
            logger.debug(f"Received response: {json.dumps(response_data, indent=2)}")
            return response_data
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"error": {"message": str(e)}}
            
    async def authorize(self):
        """Authorize with API token"""
        if not self.api_token:
            logger.warning("No API token provided for authorization")
            return False
            
        request = {
            "authorize": self.api_token
        }
        response = await self.send_request(request)
        if "error" in response:
            error_msg = response['error']['message'] if 'message' in response['error'] else str(response['error'])
            logger.error(f"Authorization failed: {error_msg}")
            return False
        logger.info("Successfully authorized")
        return True
        
    async def get_balance(self):
        """Get account balance"""
        request = {"balance": 1, "subscribe": 1}
        return await self.send_request(request)
        
    async def get_ticks(self, symbol: str):
        """Get live ticks for a symbol"""
        request = {
            "ticks": symbol,
            "subscribe": 1
        }
        return await self.send_request(request)
        
    async def get_active_symbols(self):
        """Get list of active trading symbols"""
        request = {
            "active_symbols": "brief",
            "product_type": "basic"
        }
        return await self.send_request(request)
        
    async def buy_contract(self, contract_type: str, symbol: str, amount: float, duration: int, duration_unit: str = "t"):
        """Buy a contract"""
        request = {
            "buy": 1,
            "price": amount,
            "parameters": {
                "contract_type": contract_type,
                "symbol": symbol,
                "duration": duration,
                "duration_unit": duration_unit,
                "amount": amount
            }
        }
        return await self.send_request(request)
    
    async def get_profit_table(self, symbol: str, contract_type: str = "CALL"):
        """Get profit table for a symbol"""
        request = {
            "profit_table": 1,
            "symbol": symbol,
            "contract_type": contract_type
        }
        return await self.send_request(request)
        
    async def get_proposal(self, contract_type: str, symbol: str, amount: float, duration: int, duration_unit: str = "t"):
        """Get proposal for a contract"""
        request = {
            "proposal": 1,
            "contract_type": contract_type,
            "symbol": symbol,
            "amount": amount,
            "duration": duration,
            "duration_unit": duration_unit
        }
        return await self.send_request(request)
        
    async def get_portfolio(self):
        """Get portfolio/open positions"""
        request = {"portfolio": 1}
        return await self.send_request(request)

class TechnicalIndicators:
    """Technical indicators for trading strategies"""
    
    @staticmethod
    def calculate_ema(prices, period=20):
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
        return ta.EMA(np.array(prices), timeperiod=period)
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Calculate Relative Strength Index"""
        if len(prices) < period:
            return None
        return ta.RSI(np.array(prices), timeperiod=period)
    
    @staticmethod
    def calculate_bollinger_bands(prices, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return None, None, None
        upper, middle, lower = ta.BBANDS(np.array(prices), timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)
        return upper, middle, lower
    
    @staticmethod
    def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
        """Calculate MACD"""
        if len(prices) < slow_period:
            return None, None, None
        macd, signal, histogram = ta.MACD(np.array(prices), fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)
        return macd, signal, histogram

class TradingStrategy:
    """Base trading strategy class"""
    
    def __init__(self, user_id: int, symbol: str, user_api: DerivAPI):
        self.user_id = user_id
        self.symbol = symbol
        self.user_api = user_api
        self.is_active = False
        self.price_history = deque(maxlen=100)
        self.indicators = TechnicalIndicators()
        self.trades_count = 0
        self.winning_trades = 0
        self.total_profit = 0
        
    async def add_price(self, price: float):
        """Add new price to history"""
        self.price_history.append(price)
        
    async def should_buy_call(self) -> bool:
        """Override in subclasses"""
        return False
        
    async def should_buy_put(self) -> bool:
        """Override in subclasses"""
        return False
        
    async def place_trade(self, contract_type: str, amount: float = 1.0, duration: int = 5):
        """Place a trade"""
        try:
            response = await self.user_api.buy_contract(contract_type, self.symbol, amount, duration, "t")
            if "buy" in response:
                self.trades_count += 1
                return True
            return False
        except Exception as e:
            logger.error(f"Trade placement error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get strategy statistics"""
        win_rate = (self.winning_trades / self.trades_count * 100) if self.trades_count > 0 else 0
        return {
            "trades_count": self.trades_count,
            "winning_trades": self.winning_trades,
            "win_rate": win_rate,
            "total_profit": self.total_profit
        }

class StepIndex100ScalpingStrategy(TradingStrategy):
    """Step Index 100 scalping strategy using EMA + RSI"""
    
    def __init__(self, user_id: int, user_api: DerivAPI):
        super().__init__(user_id, "STEP_100", user_api)
        self.ema_period = 20
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        
    async def should_buy_call(self) -> bool:
        """Buy CALL when price is above EMA and RSI is oversold (bounce expected)"""
        if len(self.price_history) < max(self.ema_period, self.rsi_period):
            return False
            
        prices = list(self.price_history)
        current_price = prices[-1]
        
        # Calculate EMA
        ema = self.indicators.calculate_ema(prices, self.ema_period)
        if ema is None:
            return False
        current_ema = ema[-1]
        
        # Calculate RSI
        rsi = self.indicators.calculate_rsi(prices, self.rsi_period)
        if rsi is None:
            return False
        current_rsi = rsi[-1]
        
        # Buy CALL if price is above EMA and RSI is oversold
        return current_price > current_ema and current_rsi < self.rsi_oversold
    
    async def should_buy_put(self) -> bool:
        """Buy PUT when price is below EMA and RSI is overbought (drop expected)"""
        if len(self.price_history) < max(self.ema_period, self.rsi_period):
            return False
            
        prices = list(self.price_history)
        current_price = prices[-1]
        
        # Calculate EMA
        ema = self.indicators.calculate_ema(prices, self.ema_period)
        if ema is None:
            return False
        current_ema = ema[-1]
        
        # Calculate RSI
        rsi = self.indicators.calculate_rsi(prices, self.rsi_period)
        if rsi is None:
            return False
        current_rsi = rsi[-1]
        
        # Buy PUT if price is below EMA and RSI is overbought
        return current_price < current_ema and current_rsi > self.rsi_overbought

class Volatility75SwingStrategy(TradingStrategy):
    """Volatility 75 swing strategy using Bollinger Bands + MACD"""
    
    def __init__(self, user_id: int, user_api: DerivAPI):
        super().__init__(user_id, "R_75", user_api)
        self.bb_period = 20
        self.bb_std_dev = 2
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        
    async def should_buy_call(self) -> bool:
        """Buy CALL when price hits lower BB and MACD shows bullish signal"""
        if len(self.price_history) < max(self.bb_period, self.macd_slow):
            return False
            
        prices = list(self.price_history)
        current_price = prices[-1]
        
        # Calculate Bollinger Bands
        upper, middle, lower = self.indicators.calculate_bollinger_bands(prices, self.bb_period, self.bb_std_dev)
        if lower is None:
            return False
        current_lower = lower[-1]
        
        # Calculate MACD
        macd, signal, histogram = self.indicators.calculate_macd(prices, self.macd_fast, self.macd_slow, self.macd_signal)
        if macd is None:
            return False
        current_macd = macd[-1]
        current_signal = signal[-1]
        
        # Buy CALL if price is near lower BB and MACD is bullish
        return current_price <= current_lower * 1.01 and current_macd > current_signal
    
    async def should_buy_put(self) -> bool:
        """Buy PUT when price hits upper BB and MACD shows bearish signal"""
        if len(self.price_history) < max(self.bb_period, self.macd_slow):
            return False
            
        prices = list(self.price_history)
        current_price = prices[-1]
        
        # Calculate Bollinger Bands
        upper, middle, lower = self.indicators.calculate_bollinger_bands(prices, self.bb_period, self.bb_std_dev)
        if upper is None:
            return False
        current_upper = upper[-1]
        
        # Calculate MACD
        macd, signal, histogram = self.indicators.calculate_macd(prices, self.macd_fast, self.macd_slow, self.macd_signal)
        if macd is None:
            return False
        current_macd = macd[-1]
        current_signal = signal[-1]
        
        # Buy PUT if price is near upper BB and MACD is bearish
        return current_price >= current_upper * 0.99 and current_macd < current_signal

class CustomScalpingStrategy(TradingStrategy):
    """Custom scalping strategy for any market using EMA + RSI"""
    
    def __init__(self, user_id: int, market: str, user_api: DerivAPI, lot_size: float):
        super().__init__(user_id, market, user_api)
        self.lot_size = lot_size
        self.ema_period = 20
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        
    async def should_buy_call(self) -> bool:
        """Buy CALL when price is above EMA and RSI is oversold"""
        if len(self.price_history) < max(self.ema_period, self.rsi_period):
            return False
            
        prices = list(self.price_history)
        current_price = prices[-1]
        
        # Calculate EMA
        ema = self.indicators.calculate_ema(prices, self.ema_period)
        if ema is None:
            return False
        current_ema = ema[-1]
        
        # Calculate RSI
        rsi = self.indicators.calculate_rsi(prices, self.rsi_period)
        if rsi is None:
            return False
        current_rsi = rsi[-1]
        
        # Buy CALL if price is above EMA and RSI is oversold
        return current_price > current_ema and current_rsi < self.rsi_oversold
    
    async def should_buy_put(self) -> bool:
        """Buy PUT when price is below EMA and RSI is overbought"""
        if len(self.price_history) < max(self.ema_period, self.rsi_period):
            return False
            
        prices = list(self.price_history)
        current_price = prices[-1]
        
        # Calculate EMA
        ema = self.indicators.calculate_ema(prices, self.ema_period)
        if ema is None:
            return False
        current_ema = ema[-1]
        
        # Calculate RSI
        rsi = self.indicators.calculate_rsi(prices, self.rsi_period)
        if rsi is None:
            return False
        current_rsi = rsi[-1]
        
        # Buy PUT if price is below EMA and RSI is overbought
        return current_price < current_ema and current_rsi > self.rsi_overbought
    
    async def place_trade(self, contract_type: str, amount: float = None, duration: int = 5):
        """Place a trade with custom lot size"""
        if amount is None:
            amount = self.lot_size
        return await super().place_trade(contract_type, amount, duration)

class CustomSwingStrategy(TradingStrategy):
    """Custom swing strategy for any market using Bollinger Bands + MACD"""
    
    def __init__(self, user_id: int, market: str, user_api: DerivAPI, lot_size: float):
        super().__init__(user_id, market, user_api)
        self.lot_size = lot_size
        self.bb_period = 20
        self.bb_std_dev = 2
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        
    async def should_buy_call(self) -> bool:
        """Buy CALL when price hits lower BB and MACD is bullish"""
        if len(self.price_history) < max(self.bb_period, self.macd_slow):
            return False
            
        prices = list(self.price_history)
        current_price = prices[-1]
        
        # Calculate Bollinger Bands
        upper, middle, lower = self.indicators.calculate_bollinger_bands(prices, self.bb_period, self.bb_std_dev)
        if lower is None:
            return False
        current_lower = lower[-1]
        
        # Calculate MACD
        macd, signal, histogram = self.indicators.calculate_macd(prices, self.macd_fast, self.macd_slow, self.macd_signal)
        if macd is None:
            return False
        current_macd = macd[-1]
        current_signal = signal[-1]
        
        # Buy CALL if price is near lower BB and MACD is bullish
        return current_price <= current_lower * 1.01 and current_macd > current_signal
    
    async def should_buy_put(self) -> bool:
        """Buy PUT when price hits upper BB and MACD is bearish"""
        if len(self.price_history) < max(self.bb_period, self.macd_slow):
            return False
            
        prices = list(self.price_history)
        current_price = prices[-1]
        
        # Calculate Bollinger Bands
        upper, middle, lower = self.indicators.calculate_bollinger_bands(prices, self.bb_period, self.bb_std_dev)
        if upper is None:
            return False
        current_upper = upper[-1]
        
        # Calculate MACD
        macd, signal, histogram = self.indicators.calculate_macd(prices, self.macd_fast, self.macd_slow, self.macd_signal)
        if macd is None:
            return False
        current_macd = macd[-1]
        current_signal = signal[-1]
        
        # Buy PUT if price is near upper BB and MACD is bearish
        return current_price >= current_upper * 0.99 and current_macd < current_signal

class StrategyManager:
    """Manages trading strategies for users"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.active_strategies = {}  # {user_id: {strategy_name: strategy_instance}}
        self.strategy_threads = {}  # {user_id: {strategy_name: thread}}
        
    async def start_strategy(self, user_id: int, strategy_name: str) -> bool:
        """Start a trading strategy for a user"""
        if user_id not in self.active_strategies:
            self.active_strategies[user_id] = {}
        
        if strategy_name in self.active_strategies[user_id]:
            return False  # Strategy already running
        
        user_api = self.bot.get_user_api(user_id)
        
        # Create strategy instance
        if strategy_name == "step_scalping":
            strategy = StepIndex100ScalpingStrategy(user_id, user_api)
        elif strategy_name == "v75_swing":
            strategy = Volatility75SwingStrategy(user_id, user_api)
        else:
            return False
        
        # Start the strategy
        self.active_strategies[user_id][strategy_name] = strategy
        strategy.is_active = True
        
        # Start monitoring thread
        thread = threading.Thread(target=self._run_strategy_monitoring, args=(user_id, strategy_name))
        thread.daemon = True
        thread.start()
        
        if user_id not in self.strategy_threads:
            self.strategy_threads[user_id] = {}
        self.strategy_threads[user_id][strategy_name] = thread
        
        return True
    
    def stop_strategy(self, user_id: int, strategy_name: str = None) -> bool:
        """Stop a trading strategy for a user"""
        if user_id not in self.active_strategies:
            return False
        
        if strategy_name is None:
            # Stop all strategies for user
            for strat_name in list(self.active_strategies[user_id].keys()):
                self.active_strategies[user_id][strat_name].is_active = False
            self.active_strategies[user_id] = {}
            if user_id in self.strategy_threads:
                self.strategy_threads[user_id] = {}
            return True
        else:
            # Stop specific strategy
            if strategy_name in self.active_strategies[user_id]:
                self.active_strategies[user_id][strategy_name].is_active = False
                del self.active_strategies[user_id][strategy_name]
                if user_id in self.strategy_threads and strategy_name in self.strategy_threads[user_id]:
                    del self.strategy_threads[user_id][strategy_name]
                return True
            return False
    
    def get_strategy_status(self, user_id: int) -> dict:
        """Get status of all strategies for a user"""
        if user_id not in self.active_strategies:
            return {}
        
        status = {}
        for strategy_name, strategy in self.active_strategies[user_id].items():
            status[strategy_name] = {
                "is_active": strategy.is_active,
                "symbol": strategy.symbol,
                "stats": strategy.get_stats()
            }
        return status
    
    def _run_strategy_monitoring(self, user_id: int, strategy_name: str):
        """Run strategy monitoring in background thread"""
        strategy = self.active_strategies[user_id][strategy_name]
        
        while strategy.is_active:
            try:
                # Create event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Get current price
                loop.run_until_complete(self._update_strategy_price(strategy))
                
                # Check for trading signals
                if len(strategy.price_history) >= 20:  # Minimum data points
                    call_signal = loop.run_until_complete(strategy.should_buy_call())
                    put_signal = loop.run_until_complete(strategy.should_buy_put())
                    
                    if call_signal:
                        loop.run_until_complete(strategy.place_trade("CALL"))
                    elif put_signal:
                        loop.run_until_complete(strategy.place_trade("PUT"))
                
                # Sleep for a bit before next check
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Strategy monitoring error: {e}")
                time.sleep(10)  # Wait longer on error
    
    async def _update_strategy_price(self, strategy: TradingStrategy):
        """Update price for a strategy"""
        try:
            response = await strategy.user_api.get_ticks(strategy.symbol)
            if "tick" in response:
                price = response["tick"]["quote"]
                await strategy.add_price(price)
        except Exception as e:
            logger.error(f"Price update error: {e}")

class DerivTelegramBot:
    """Main Telegram Bot class"""
    
    def __init__(self, telegram_token: str, deriv_app_id: str, deriv_api_token: str = None):
        self.telegram_token = telegram_token
        self.default_deriv_api = DerivAPI(deriv_app_id, deriv_api_token)
        self.application = None
        self.user_accounts = {}  # Store user-specific API connections
        self.user_sessions = {}  # Store user-specific data
        self.strategy_manager = StrategyManager(self)  # Add strategy manager
        self.price_history = {}  # Store price history for analysis
        
    def get_user_api(self, user_id: int) -> DerivAPI:
        """Get API connection for a specific user"""
        if user_id in self.user_accounts:
            return self.user_accounts[user_id]
        return self.default_deriv_api
        
    def add_user_account(self, user_id: int, api_token: str) -> bool:
        """Add a new user account"""
        try:
            # Use the same App ID but different API token
            user_api = DerivAPI(Config.DERIV_APP_ID, api_token)
            self.user_accounts[user_id] = user_api
            return True
        except Exception as e:
            logger.error(f"Failed to add user account: {e}")
            return False
            
    def remove_user_account(self, user_id: int):
        """Remove a user account"""
        if user_id in self.user_accounts:
            del self.user_accounts[user_id]
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Check if user has their own account connected
        has_personal_account = user_id in self.user_accounts
        
        welcome_message = f"""
🎯 Welcome to Deriv Trading Bot, {user.first_name}!

{'✅ Personal Account: Connected' if has_personal_account else '⚠️ Using Demo Account - Connect your own account with /connect'}

Quick access to all features:
        """
        
        keyboard = [
            [InlineKeyboardButton("🤖 Auto Trading", callback_data="auto_trading")],
            [InlineKeyboardButton("� Balance", callback_data="balance"), InlineKeyboardButton("📈 Live Prices", callback_data="live_prices")],
            [InlineKeyboardButton("🎲 Manual Trade", callback_data="manual_trade"), InlineKeyboardButton("📋 Portfolio", callback_data="portfolio")],
            [InlineKeyboardButton("🔗 Connect Account" if not has_personal_account else "👤 Account Info", callback_data="connect")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **Deriv Trading Bot Commands:**

**Account Management:**
• /connect [token] - Connect your personal Deriv account
• /disconnect - Disconnect your personal account
• /account - View account information

**Basic Commands:**
• /start - Start the bot
• /help - Show this help message
• /balance - Check account balance
• /symbols - Get active trading symbols
• /price [symbol] - Get current price for a symbol

**Trading Commands:**
• /buy [contract_type] [symbol] [amount] [duration] - Buy a contract
• /sell [contract_id] - Sell a contract
• /portfolio - View open positions
• /profit [symbol] - Get profit table for a symbol
• /history - View trading history

**Strategy Commands:**
• /strategy start step_scalping - Start Step Index 100 scalping
• /strategy start v75_swing - Start Volatility 75 swing trading
• /strategy stop - Stop all strategies
• /strategy status - Check strategy status

**Market Commands:**
• /analysis [symbol] - Get market analysis
• /trends - View market trends

**Examples:**
• /connect abc123def456ghi789 - Connect your account
• /price R_100 - Get price for Volatility 100 Index
• /buy CALL R_100 1 5 - Buy CALL contract for R_100, $1, 5 ticks

**Security:**
• Your API tokens are stored securely
• Only you can access your account data
• Use /disconnect to remove your account anytime
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        user_id = update.effective_user.id
        user_api = self.get_user_api(user_id)
        
        try:
            await update.message.reply_text("🔄 Fetching balance...")
            
            response = await user_api.get_balance()
            
            if "error" in response:
                await update.message.reply_text(f"❌ Error: {response['error']['message']}")
                return
                
            if "balance" in response:
                balance = response["balance"]
                currency = balance.get("currency", "USD")
                amount = balance.get("balance", 0)
                is_personal = user_id in self.user_accounts
                
                balance_text = f"""
💰 **Account Balance**
Account Type: {'Personal' if is_personal else 'Demo'}
Amount: {amount} {currency}
Login ID: {balance.get('loginid', 'N/A')}
                """
                await update.message.reply_text(balance_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Unable to fetch balance. Please check your API token.")
                
        except Exception as e:
            logger.error(f"Balance command error: {e}")
            await update.message.reply_text("❌ An error occurred while fetching balance.")
            
    async def symbols_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /symbols command"""
        user_id = update.effective_user.id
        user_api = self.get_user_api(user_id)
        
        try:
            await update.message.reply_text("🔄 Fetching active symbols...")
            
            response = await user_api.get_active_symbols()
            
            if "error" in response:
                await update.message.reply_text(f"❌ Error: {response['error']['message']}")
                return
                
            if "active_symbols" in response:
                symbols = response["active_symbols"][:10]  # Show first 10 symbols
                
                symbols_text = "📋 **Active Trading Symbols:**\n\n"
                for symbol in symbols:
                    symbols_text += f"• {symbol.get('symbol', 'N/A')} - {symbol.get('display_name', 'N/A')}\n"
                    
                symbols_text += f"\n📊 Showing {len(symbols)} of {len(response['active_symbols'])} symbols"
                
                await update.message.reply_text(symbols_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Unable to fetch symbols.")
                
        except Exception as e:
            logger.error(f"Symbols command error: {e}")
            await update.message.reply_text("❌ An error occurred while fetching symbols.")
            
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /price command"""
        user_id = update.effective_user.id
        user_api = self.get_user_api(user_id)
        
        if not context.args:
            await update.message.reply_text("❌ Please provide a symbol. Example: /price R_100")
            return
            
        symbol = context.args[0].upper()
        
        try:
            await update.message.reply_text(f"🔄 Fetching price for {symbol}...")
            
            response = await user_api.get_ticks(symbol)
            
            if "error" in response:
                await update.message.reply_text(f"❌ Error: {response['error']['message']}")
                return
                
            if "tick" in response:
                tick = response["tick"]
                price_text = f"""
📈 **{symbol} Price**
Current Price: {tick.get('quote', 'N/A')}
Time: {datetime.fromtimestamp(tick.get('epoch', 0)).strftime('%Y-%m-%d %H:%M:%S')}
                """
                await update.message.reply_text(price_text, parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Unable to fetch price for {symbol}.")
                
        except Exception as e:
            logger.error(f"Price command error: {e}")
            await update.message.reply_text("❌ An error occurred while fetching price.")
            
    async def connect_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /connect command"""
        user_id = update.effective_user.id
        
        if user_id in self.user_accounts:
            await update.message.reply_text("✅ You already have an account connected! Use /disconnect to remove it first.")
            return
            
        if not context.args:
            connect_message = """
🔗 **Connect Your Deriv Account**

To connect your personal Deriv account:

1. Go to https://app.deriv.com/account/api-token
2. Log in to your Deriv account
3. Create a new API token with required permissions
4. Send the command: `/connect YOUR_API_TOKEN`

**Example:**
`/connect abc123def456ghi789`

**Security Note:** Your API token will be stored securely and only used for your requests.
            """
            await update.message.reply_text(connect_message, parse_mode='Markdown')
            return
            
        api_token = context.args[0]
        
        # Validate token format (basic check)
        if len(api_token) < 10:
            await update.message.reply_text("❌ Invalid API token format. Please check your token.")
            return
            
        await update.message.reply_text("🔄 Connecting your account...")
        
        # Try to connect with the new token
        try:
            test_api = DerivAPI(Config.DERIV_APP_ID, api_token)
            await test_api.connect()
            
            # Test the connection by getting account info
            response = await test_api.get_balance()
            await test_api.disconnect()
            
            if "error" in response:
                await update.message.reply_text(f"❌ Connection failed: {response['error']['message']}")
                return
                
            # Store the user's API connection
            self.add_user_account(user_id, api_token)
            
            balance = response.get("balance", {})
            connect_success = f"""
✅ **Account Connected Successfully!**

Account Details:
• Balance: {balance.get('balance', 'N/A')} {balance.get('currency', 'USD')}
• Login ID: {balance.get('loginid', 'N/A')}

You can now use all bot features with your personal account!
            """
            await update.message.reply_text(connect_success, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Connect command error: {e}")
            await update.message.reply_text("❌ Failed to connect account. Please check your API token.")
            
    async def disconnect_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /disconnect command"""
        user_id = update.effective_user.id
        
        if user_id not in self.user_accounts:
            await update.message.reply_text("❌ No personal account connected.")
            return
            
        # Disconnect the user's API
        user_api = self.user_accounts[user_id]
        await user_api.disconnect()
        
        # Remove from storage
        self.remove_user_account(user_id)
        
        await update.message.reply_text("✅ Account disconnected successfully. You're now using the demo account.")
        
    async def account_info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /account command"""
        user_id = update.effective_user.id
        user_api = self.get_user_api(user_id)
        
        try:
            await update.message.reply_text("🔄 Fetching account information...")
            
            response = await user_api.get_balance()
            
            if "error" in response:
                await update.message.reply_text(f"❌ Error: {response['error']['message']}")
                return
                
            if "balance" in response:
                balance = response["balance"]
                is_personal = user_id in self.user_accounts
                
                account_info = f"""
👤 **Account Information**

Account Type: {'Personal Account' if is_personal else 'Demo Account'}
Balance: {balance.get('balance', 'N/A')} {balance.get('currency', 'USD')}
Login ID: {balance.get('loginid', 'N/A')}
Email: {balance.get('email', 'N/A')}

{'' if is_personal else '💡 Connect your personal account with /connect for full features'}
                """
                await update.message.reply_text(account_info, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Unable to fetch account information.")
                
        except Exception as e:
            logger.error(f"Account info command error: {e}")
            await update.message.reply_text("❌ An error occurred while fetching account information.")

    async def admin_users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /users command (admin only)"""
        user_id = update.effective_user.id
        
        # You can add your user ID here for admin access
        admin_user_ids = [update.effective_user.id]  # Add your telegram user ID
        
        if user_id not in admin_user_ids:
            await update.message.reply_text("❌ Admin access required.")
            return
        
        users_info = f"""
👥 **Connected Users Status**

📊 **Statistics:**
• Total Connected Users: {len(self.user_accounts)}
• Default Account: {Config.DERIV_API_TOKEN[:8]}...
• App ID: {Config.DERIV_APP_ID}

👤 **Connected Users:**
        """
        
        if self.user_accounts:
            for user_id, api in self.user_accounts.items():
                users_info += f"• User ID: {user_id}\n"
                users_info += f"  Token: {api.api_token[:8]}...\n"
                users_info += f"  Status: Connected\n\n"
        else:
            users_info += "• No users connected yet\n"
        
        users_info += """
💡 **How users connect:**
• Users send: /connect [token]
• Data stored in memory
• Cleared on bot restart
        """
        
        await update.message.reply_text(users_info, parse_mode='Markdown')

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        user_id = query.from_user.id
        await query.answer()
        
        if query.data == "balance":
            await self.balance_command(update, context)
        elif query.data == "live_prices":
            await self.show_price_menu(query)
        elif query.data == "symbols":
            await self.symbols_command(update, context)
        elif query.data == "connect":
            if user_id in self.user_accounts:
                await self.account_info_command(update, context)
            else:
                await self.show_connect_menu(query)
        elif query.data == "connect_account":
            await self.show_connect_menu(query)
        elif query.data == "help":
            await self.help_command(update, context)
        elif query.data == "auto_trading":
            await self.show_auto_trading_menu(query)
        elif query.data == "manual_trade":
            await self.show_manual_trade_menu(query)
        elif query.data == "portfolio":
            await self.portfolio_command(update, context)
        elif query.data == "all_positions":
            await self.show_all_positions(query)
        elif query.data.startswith("start_strategy_"):
            await self.handle_strategy_selection(query)
        elif query.data.startswith("market_"):
            await self.handle_market_selection(query)
        elif query.data.startswith("lot_"):
            await self.handle_lot_selection(query)
        elif query.data.startswith("price_"):
            await self.handle_price_request(query)
        elif query.data.startswith("trade_"):
            await self.handle_trade_category(query)
        elif query.data.startswith("symbol_"):
            await self.handle_symbol_selection(query)
        elif query.data.startswith("contract_"):
            await self.handle_contract_selection(query)
        elif query.data.startswith("amount_"):
            await self.handle_amount_selection(query)
        elif query.data.startswith("duration_"):
            await self.handle_duration_selection(query)
        elif query.data.startswith("place_trade_"):
            await self.handle_place_trade(query)
        elif query.data.startswith("close_position_"):
            await self.handle_close_position(query)
        elif query.data == "strategy_status":
            await self.show_strategy_status(query)
        elif query.data == "stop_all_strategies":
            await self.handle_stop_all_strategies(query)
        elif query.data == "back_to_main":
            await self.show_main_menu(query)
        elif query.data == "back_to_auto_trading":
            await self.show_auto_trading_menu(query)
            
    async def show_main_menu(self, query):
        """Show main menu"""
        user_id = query.from_user.id
        has_personal_account = user_id in self.user_accounts
        
        welcome_message = f"""
🎯 Deriv Trading Bot Main Menu

{'✅ Personal Account: Connected' if has_personal_account else '⚠️ Using Demo Account - Connect your own account'}

Quick access to all features:
        """
        
        keyboard = [
            [InlineKeyboardButton("🤖 Auto Trading", callback_data="auto_trading")],
            [InlineKeyboardButton("📊 Balance", callback_data="balance"), InlineKeyboardButton("📈 Live Prices", callback_data="live_prices")],
            [InlineKeyboardButton("🎲 Manual Trade", callback_data="manual_trade"), InlineKeyboardButton("📋 All Positions", callback_data="all_positions")],
            [InlineKeyboardButton("🔗 Connect Account" if not has_personal_account else "👤 Account Info", callback_data="connect")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_message, reply_markup=reply_markup)
        
    async def show_auto_trading_menu(self, query):
        """Show automated trading menu"""
        user_id = query.from_user.id
        
        if user_id not in self.user_accounts:
            await query.edit_message_text(
                "❌ Please connect your account first to use automated trading.\n\nUse the button below to connect:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Connect Account", callback_data="connect")],
                    [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
                ])
            )
            return
        
        strategies = self.strategy_manager.get_strategy_status(user_id)
        active_count = len(strategies)
        
        menu_text = f"""
🤖 **Automated Trading Menu**

📊 **Status:** {active_count} active strategies

**Available Strategies:**
• 🎯 Scalping Strategy (EMA + RSI)
• 📈 Swing Trading (Bollinger + MACD)

**Select a strategy to start:**
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Start Scalping", callback_data="start_strategy_scalping")],
            [InlineKeyboardButton("📈 Start Swing Trading", callback_data="start_strategy_swing")],
            [InlineKeyboardButton("📊 Strategy Status", callback_data="strategy_status")],
            [InlineKeyboardButton("🛑 Stop All Strategies", callback_data="stop_all_strategies")],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_strategy_selection(self, query):
        """Handle strategy selection"""
        strategy_type = query.data.split("_")[-1]  # scalping or swing
        
        if strategy_type == "scalping":
            menu_text = """
🎯 **Scalping Strategy Setup**

**Method:** EMA + RSI signals
**Best for:** Quick profits on volatility

**Select Market:**
            """
            keyboard = [
                [InlineKeyboardButton("📊 Volatility 75 (R_75)", callback_data="market_scalping_R_75")],
                [InlineKeyboardButton("📊 Volatility 100 (R_100)", callback_data="market_scalping_R_100")],
                [InlineKeyboardButton("📊 Volatility 50 (R_50)", callback_data="market_scalping_R_50")],
                [InlineKeyboardButton("💥 Boom 500", callback_data="market_scalping_BOOM500")],
                [InlineKeyboardButton("💥 Boom 1000", callback_data="market_scalping_BOOM1000")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_auto_trading")]
            ]
        else:  # swing
            menu_text = """
📈 **Swing Trading Setup**

**Method:** Bollinger Bands + MACD
**Best for:** Trend following

**Select Market:**
            """
            keyboard = [
                [InlineKeyboardButton("📊 Volatility 75 (R_75)", callback_data="market_swing_R_75")],
                [InlineKeyboardButton("📊 Volatility 100 (R_100)", callback_data="market_swing_R_100")],
                [InlineKeyboardButton("📊 Volatility 25 (R_25)", callback_data="market_swing_R_25")],
                [InlineKeyboardButton("💥 Crash 500", callback_data="market_swing_CRASH500")],
                [InlineKeyboardButton("💥 Crash 1000", callback_data="market_swing_CRASH1000")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_auto_trading")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_market_selection(self, query):
        """Handle market selection for strategies"""
        data_parts = query.data.split("_")
        strategy_type = data_parts[1]  # scalping or swing
        market = "_".join(data_parts[2:])  # R_75, BOOM500, etc.
        
        # Store selection in user session
        if query.from_user.id not in self.user_sessions:
            self.user_sessions[query.from_user.id] = {}
        self.user_sessions[query.from_user.id]['selected_strategy'] = strategy_type
        self.user_sessions[query.from_user.id]['selected_market'] = market
        
        market_info = {
            "R_75": "Volatility 75 Index",
            "R_100": "Volatility 100 Index", 
            "R_50": "Volatility 50 Index",
            "R_25": "Volatility 25 Index",
            "BOOM500": "Boom 500 Index",
            "BOOM1000": "Boom 1000 Index",
            "CRASH500": "Crash 500 Index",
            "CRASH1000": "Crash 1000 Index"
        }
        
        # Recommended lot sizes based on strategy and market
        if strategy_type == "scalping":
            recommended_lots = [0.1, 0.2, 0.5, 1.0, 2.0]
        else:  # swing
            recommended_lots = [0.001, 0.01, 0.1, 0.5, 1.0]
        
        menu_text = f"""
💰 **Lot Size Selection**

**Strategy:** {strategy_type.title()}
**Market:** {market_info.get(market, market)}

**Select lot size (amount per trade):**
        """
        
        keyboard = []
        for lot in recommended_lots:
            keyboard.append([InlineKeyboardButton(f"${lot}", callback_data=f"lot_{lot}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"start_strategy_{strategy_type}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_lot_selection(self, query):
        """Handle lot size selection and start strategy"""
        user_id = query.from_user.id
        lot_size = float(query.data.split("_")[1])
        
        # Get user selections
        user_session = self.user_sessions.get(user_id, {})
        strategy_type = user_session.get('selected_strategy')
        market = user_session.get('selected_market')
        
        if not strategy_type or not market:
            await query.edit_message_text("❌ Session expired. Please start again.", 
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_auto_trading")]
                                        ]))
            return
        
        await query.edit_message_text(f"🔄 Starting {strategy_type} strategy on {market} with ${lot_size} lot size...")
        
        # Create custom strategy with user parameters
        success = await self.start_custom_strategy(user_id, strategy_type, market, lot_size)
        
        if success:
            market_info = {
                "R_75": "Volatility 75", "R_100": "Volatility 100", "R_50": "Volatility 50", 
                "R_25": "Volatility 25", "BOOM500": "Boom 500", "BOOM1000": "Boom 1000",
                "CRASH500": "Crash 500", "CRASH1000": "Crash 1000"
            }
            
            success_message = f"""
✅ **Strategy Started Successfully!**

📊 **Strategy Details:**
• Type: {strategy_type.title()} Strategy
• Market: {market_info.get(market, market)}
• Lot Size: ${lot_size}
• Status: 🟢 Running

🎯 **What's Next:**
• Strategy will trade automatically
• Monitor with Strategy Status
• Check your balance regularly

⚠️ **Important:** Only risk what you can afford to lose!
            """
            
            keyboard = [
                [InlineKeyboardButton("📊 Strategy Status", callback_data="strategy_status")],
                [InlineKeyboardButton("🔙 Back to Auto Trading", callback_data="back_to_auto_trading")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(success_message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ Failed to start strategy. Please try again.", 
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_auto_trading")]
                                        ]))
    
    async def show_strategy_status(self, query):
        """Show strategy status with buttons"""
        user_id = query.from_user.id
        strategies = self.strategy_manager.get_strategy_status(user_id)
        
        if not strategies:
            await query.edit_message_text("📊 No active strategies found.", 
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Back to Auto Trading", callback_data="back_to_auto_trading")]
                                        ]))
            return
        
        status_text = "📊 **Active Strategies:**\n\n"
        
        for strategy_name, status in strategies.items():
            stats = status['stats']
            
            status_text += f"🤖 **{strategy_name.replace('_', ' ').title()}**\n"
            status_text += f"• Symbol: {status['symbol']}\n"
            status_text += f"• Status: {'🟢 Running' if status['is_active'] else '🔴 Stopped'}\n"
            status_text += f"• Trades: {stats['trades_count']}\n"
            status_text += f"• Wins: {stats['winning_trades']}\n"
            status_text += f"• Win Rate: {stats['win_rate']:.1f}%\n"
            status_text += f"• P&L: ${stats['total_profit']:.2f}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh Status", callback_data="strategy_status")],
            [InlineKeyboardButton("🛑 Stop All Strategies", callback_data="stop_all_strategies")],
            [InlineKeyboardButton("🔙 Back to Auto Trading", callback_data="back_to_auto_trading")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(status_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_stop_all_strategies(self, query):
        """Handle stopping all strategies"""
        user_id = query.from_user.id
        success = self.strategy_manager.stop_strategy(user_id)
        
        if success:
            await query.edit_message_text("✅ All strategies stopped successfully.", 
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Back to Auto Trading", callback_data="back_to_auto_trading")]
                                        ]))
        else:
            await query.edit_message_text("❌ No active strategies found.", 
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Back to Auto Trading", callback_data="back_to_auto_trading")]
                                        ]))
    
    async def show_price_menu(self, query):
        """Show price menu for quick access"""
        menu_text = """
📈 **Live Market Prices**

Select a market to get current price:
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Volatility 75", callback_data="price_R_75"), 
             InlineKeyboardButton("📊 Volatility 100", callback_data="price_R_100")],
            [InlineKeyboardButton("📊 Volatility 50", callback_data="price_R_50"), 
             InlineKeyboardButton("📊 Volatility 25", callback_data="price_R_25")],
            [InlineKeyboardButton("💥 Boom 500", callback_data="price_BOOM500"), 
             InlineKeyboardButton("💥 Boom 1000", callback_data="price_BOOM1000")],
            [InlineKeyboardButton("💥 Crash 500", callback_data="price_CRASH500"), 
             InlineKeyboardButton("💥 Crash 1000", callback_data="price_CRASH1000")],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_price_request(self, query):
        """Handle price request for specific symbol"""
        symbol = query.data.split("_", 1)[1]
        user_id = query.from_user.id
        user_api = self.get_user_api(user_id)
        
        try:
            await query.edit_message_text(f"🔄 Fetching price for {symbol}...")
            
            response = await user_api.get_ticks(symbol)
            
            if "error" in response:
                await query.edit_message_text(f"❌ Error: {response['error']['message']}", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                                            ]))
                return
            
            if "tick" in response:
                tick = response["tick"]
                market_names = {
                    "R_75": "Volatility 75 Index", "R_100": "Volatility 100 Index",
                    "R_50": "Volatility 50 Index", "R_25": "Volatility 25 Index",
                    "BOOM500": "Boom 500 Index", "BOOM1000": "Boom 1000 Index",
                    "CRASH500": "Crash 500 Index", "CRASH1000": "Crash 1000 Index"
                }
                
                price_text = f"""
📈 **{market_names.get(symbol, symbol)}**

� **Current Price:** {tick.get('quote', 'N/A')}
⏰ **Time:** {datetime.fromtimestamp(tick.get('epoch', 0)).strftime('%H:%M:%S')}
📊 **Symbol:** {symbol}
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Refresh Price", callback_data=f"price_{symbol}")],
                    [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(price_text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await query.edit_message_text(f"❌ Unable to fetch price for {symbol}.", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                                            ]))
        
        except Exception as e:
            logger.error(f"Price request error: {e}")
            await query.edit_message_text("❌ An error occurred while fetching price.", 
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                                        ]))
    
    async def show_manual_trade_menu(self, query):
        """Show manual trading menu"""
        user_id = query.from_user.id
        
        if user_id not in self.user_accounts:
            await query.edit_message_text(
                "❌ Please connect your account first to place trades.\n\nUse the button below to connect:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Connect Account", callback_data="connect")],
                    [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
                ])
            )
            return
        
        menu_text = """
🎲 **Manual Trading**

**Quick Trade Options:**
Choose market and trade type:
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Volatility Indices", callback_data="trade_volatility")],
            [InlineKeyboardButton("💥 Boom & Crash", callback_data="trade_boom_crash")],
            [InlineKeyboardButton("💱 Forex", callback_data="trade_forex")],
            [InlineKeyboardButton("📋 View All Positions", callback_data="all_positions")],
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        
        await query.edit_message_text(menu_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_connect_menu(self, query):
        """Show connection menu"""
        connect_message = """
🔗 **Connect Your Deriv Account**

**Steps to connect:**
1. Go to https://app.deriv.com/account/api-token
2. Log in to your Deriv account
3. Create a new API token
4. Copy the token
5. Use command: `/connect YOUR_TOKEN`

**Example:** `/connect abc123def456`

**Why connect?**
• Use your real balance
• Place actual trades
• Full bot features
• Your data stays secure
        """
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(connect_message, reply_markup=reply_markup, parse_mode='Markdown')
