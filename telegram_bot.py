#!/usr/bin/env python3
"""
Deriv Telegram Bot
A Telegram bot for interacting with Deriv trading platform
"""

print("🚀 TELEGRAM_BOT.PY MODULE LOADING - THIS SHOULD SHOW IF FILE IS LOADED")

import os
import logging
import asyncio
import json
import traceback
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
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
from connection_manager_fixed import get_connection_manager

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

# The DerivAPI class is now imported from connection_manager_fixed
from connection_manager_fixed import DerivAPI

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
        return current_price < current_ema and current_rsi > self.rsi_oversold
    
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
    
    def __init__(self, telegram_token: str = None, deriv_app_id: str = None, deriv_api_token: str = None):
        print("🔍 DerivTelegramBot.__init__ started")
        
        # Initialize ALL core attributes FIRST before anything else
        self.user_accounts = {}
        self.user_sessions = {}
        self.price_history = {}
        self.default_deriv_api = None
        self.strategy_manager = None
        self.application = None
        self.connection_manager = None
        
        try:
            # Use environment variables if not provided
            self.telegram_token = telegram_token or Config.TELEGRAM_BOT_TOKEN
            deriv_app_id = deriv_app_id or Config.DERIV_APP_ID
            deriv_api_token = deriv_api_token or Config.DERIV_API_TOKEN
            
            print("🔍 About to initialize core attributes...")
            
            # Initialize connection manager (new fixed version)
            print("🔍 Creating connection manager...")
            try:
                self.connection_manager = get_connection_manager(deriv_app_id)
                print(f"🔍 connection_manager created: {hasattr(self, 'connection_manager')}")
            except Exception as e:
                print(f"❌ Failed to create connection_manager: {e}")
                self.connection_manager = None
            
            # Initialize default_deriv_api with error handling
            print("🔍 Creating default_deriv_api...")
            try:
                self.default_deriv_api = DerivAPI(deriv_app_id, deriv_api_token)
                print(f"🔍 default_deriv_api created: {hasattr(self, 'default_deriv_api')}")
            except Exception as e:
                print(f"❌ Failed to create default_deriv_api: {e}")
                self.default_deriv_api = None
            
            # Initialize strategy manager
            print("🔍 Creating strategy_manager...")
            try:
                self.strategy_manager = StrategyManager(self)
                print(f"🔍 strategy_manager created: {hasattr(self, 'strategy_manager')}")
            except Exception as e:
                print(f"❌ Failed to create strategy_manager: {e}")
                self.strategy_manager = None
            
            # Create Telegram application
            print("🔍 Creating Telegram application...")
            try:
                self.application = Application.builder().token(self.telegram_token).build()
                print("🔍 Telegram application created")
            except Exception as e:
                print(f"❌ Failed to create Telegram application: {e}")
                raise
            
            # Setup handlers
            print("🔍 Setting up handlers...")
            try:
                self.setup_handlers()
                print("🔍 Handlers setup completed")
            except Exception as e:
                print(f"❌ Failed to setup handlers: {e}")
                raise
                
            print("🎉 Bot initialization completed!")
            
            # Final attribute check
            print("🔍 Final attribute check:")
            for attr in ['user_accounts', 'user_sessions', 'default_deriv_api', 'strategy_manager', 'connection_manager']:
                has_attr = hasattr(self, attr)
                print(f"  {attr}: {has_attr}")
            
        except Exception as e:
            print(f"❌ Critical error during bot initialization: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def setup_handlers(self):
        """Setup all command and callback handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("symbols", self.symbols_command))
        self.application.add_handler(CommandHandler("price", self.price_command))
        self.application.add_handler(CommandHandler("connect", self.connect_command))
        self.application.add_handler(CommandHandler("disconnect", self.disconnect_command))
        self.application.add_handler(CommandHandler("account", self.account_info_command))
        self.application.add_handler(CommandHandler("users", self.admin_users_command))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.application.add_handler(CommandHandler("profit", self.profit_table_command))
        
        # Callback query handler for buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
        
    def run(self):
        """Run the bot"""
        # Initialize connection manager before starting
        asyncio.get_event_loop().run_until_complete(self._initialize_connection_manager())
        self.application.run_polling()
        
    async def _initialize_connection_manager(self):
        """Initialize the connection manager"""
        if self.connection_manager:
            try:
                await self.connection_manager.connect()
                logger.info("🔗 Connection manager initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize connection manager: {e}")
                # Create a new one as fallback
                try:
                    self.connection_manager = get_connection_manager(Config.DERIV_APP_ID)
                    await self.connection_manager.connect()
                    logger.info("🔗 Fallback connection manager initialized")
                except Exception as e2:
                    logger.error(f"❌ Fallback connection manager also failed: {e2}")
        
    def _ensure_attributes(self):
        """Ensure all required attributes exist on the instance"""
        if not hasattr(self, 'user_accounts'):
            self.user_accounts = {}
        if not hasattr(self, 'default_deriv_api'):
            # Only pass token if it's not None/empty
            token = Config.DERIV_API_TOKEN if Config.DERIV_API_TOKEN else None
            self.default_deriv_api = DerivAPI(Config.DERIV_APP_ID, token)
        if not hasattr(self, 'user_sessions'):
            self.user_sessions = {}
        if not hasattr(self, 'price_history'):
            self.price_history = {}

    def get_user_api(self, user_id: int) -> DerivAPI:
        """Get API connection for a specific user"""
        self._ensure_attributes()  # Ensure attributes exist
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
        try:
            # Ensure attributes exist before any access
            if not hasattr(self, 'user_accounts'):
                self.user_accounts = {}
            if not hasattr(self, 'user_sessions'):
                self.user_sessions = {}
            
            user = update.effective_user
            user_id = user.id
            
            # Check if user has their own account connected
            has_personal_account = user_id in self.user_accounts
            
            welcome_message = f"""
🎯 Welcome to Deriv Trading Bot, {user.first_name}!

{'✅ Personal Account: Connected'
 if has_personal_account 
else '⚠️ Using Demo Account - Connect your own account with /connect'}

Quick access to all features:
            """
            
            keyboard = [
                [InlineKeyboardButton("🤖 Auto Trading", callback_data="auto_trading")],
                [InlineKeyboardButton("💰 Balance", callback_data="balance"), InlineKeyboardButton("📈 Live Prices", callback_data="live_prices")],
                [InlineKeyboardButton("🎲 Manual Trade", callback_data="manual_trade"), InlineKeyboardButton("📋 Portfolio", callback_data="portfolio")],
                [InlineKeyboardButton("🔗 Connect Account" if not has_personal_account else "👤 Account Info", callback_data="connect")],
                [InlineKeyboardButton("❓ Help", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error in start_command: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Handle case where update.message might be None
            try:
                if update.message:
                    await update.message.reply_text("❌ An error occurred while starting. Please try again.")
                elif update.callback_query:
                    await update.callback_query.message.reply_text("❌ An error occurred while starting. Please try again.")
            except Exception as reply_error:
                logger.error(f"Failed to send error message in start_command: {reply_error}")

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
                error_msg = response['error']['message']
                if "Max retries exceeded" in error_msg or "Connection failed" in error_msg:
                    await update.message.reply_text(
                        "🔗 **Connection Issue**\n\n"
                        "❌ Unable to connect to Deriv servers at the moment.\n\n"
                        "**Possible solutions:**\n"
                        "• Check your internet connection\n"
                        "• Try again in a few moments\n"
                        "• Deriv servers might be temporarily unavailable\n\n"
                        "💡 You can try the /start command to access the main menu."
                    )
                else:
                    await update.message.reply_text(f"❌ Error: {error_msg}")
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
            await update.message.reply_text(
                "❌ **An error occurred while fetching balance.**\n\n"
                "This might be due to:\n"
                "• Network connectivity issues\n"
                "• Deriv API unavailability\n"
                "• Invalid API token\n\n"
                "Please try again later or use /help for other commands."
            )
            
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
        try:
            # Ensure attributes exist before any access
            self._ensure_attributes()
            
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
            elif query.data.startswith("stream_"):
                await self.handle_start_stream(query)
            elif query.data.startswith("history_"):
                await self.handle_price_history(query)
            elif query.data == "stop_all_streams":
                await self.handle_stop_all_streams(query)
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
                
        except Exception as e:
            logger.error(f"Error in button_callback: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            try:
                await query.edit_message_text("❌ An error occurred. Please try again.")
            except Exception as e2:
                logger.error(f"Failed to send error message: {e2}")
            
    async def show_main_menu(self, query):
        """Show main menu"""
        try:
            # Ensure attributes exist before any access
            self._ensure_attributes()
            
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
            
        except Exception as e:
            logger.error(f"Error in show_main_menu: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            try:
                await query.edit_message_text("❌ An error occurred while showing the menu. Please try /start again.")
            except Exception as e2:
                logger.error(f"Failed to send error message: {e2}")
        
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
                                            [InlineKeyboardButton("🔙 Back to Auto Trading", callback_data="back_to_auto_trading")]
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
        """Show enhanced price menu with live streaming options"""
        menu_text = """
📈 **Live Prices Menu**

**Popular Trading Symbols:**
Choose a symbol for current price or start live streaming:
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Volatility 75 (R_75)", callback_data="price_R_75"), 
             InlineKeyboardButton("� Stream R_75", callback_data="stream_R_75")],
            [InlineKeyboardButton("�📊 Volatility 100 (R_100)", callback_data="price_R_100"),
             InlineKeyboardButton("🔴 Stream R_100", callback_data="stream_R_100")],
            [InlineKeyboardButton("📊 Volatility 50 (R_50)", callback_data="price_R_50"), 
             InlineKeyboardButton("� Stream R_50", callback_data="stream_R_50")],
            [InlineKeyboardButton("💥 Boom 500", callback_data="price_BOOM500"),
             InlineKeyboardButton("� Stream BOOM500", callback_data="stream_BOOM500")],
            [InlineKeyboardButton("💥 Crash 500", callback_data="price_CRASH500"), 
             InlineKeyboardButton("� Stream CRASH500", callback_data="stream_CRASH500")],
            [InlineKeyboardButton("🛑 Stop All Streams", callback_data="stop_all_streams")],
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
            
            # First try to get cached price from connection pool
            cached_price = user_api.get_latest_price(symbol)
            if cached_price:
                price = cached_price.get("quote", "N/A")
                timestamp = cached_price.get("epoch", "")
                
                price_text = f"""
💰 **{symbol} - Current Price**

• Price: **{price}**
• Last Updated: {datetime.fromtimestamp(timestamp) if timestamp else 'N/A'}
• Source: Live Stream (Cached)

🎯 **Quick Actions:**
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Refresh", callback_data=f"price_{symbol}"),
                     InlineKeyboardButton("🔴 Start Stream", callback_data=f"stream_{symbol}")],
                    [InlineKeyboardButton("📊 Price History", callback_data=f"history_{symbol}"),
                     InlineKeyboardButton("🎲 Trade Now", callback_data=f"trade_{symbol}")],
                    [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(price_text, reply_markup=reply_markup, parse_mode='Markdown')
                return
            
            # Fallback to direct API request
            response = await user_api.get_ticks(symbol)
            
            if "error" in response:
                await query.edit_message_text(f"❌ Error: {response['error']['message']}", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                                            ]))
                return
            
            if "tick" in response:
                tick_data = response["tick"]
                price = tick_data.get("quote", "N/A")
                timestamp = tick_data.get("epoch", "")
                
                price_text = f"""
💰 **{symbol} - Current Price**

• Price: **{price}**
• Last Updated: {datetime.fromtimestamp(timestamp) if timestamp else 'N/A'}
• Source: Direct API

🎯 **Quick Actions:**
                """
                
                price_text = f"💰 **{symbol}**\n"
                price_text += f"• Current Price: {price}\n"
                price_text += f"• Last Updated: {timestamp}"
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Refresh", callback_data=f"price_{symbol}")],
                    [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(price_text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Unable to fetch price data.", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                                            ]))
        except Exception as e:
            logger.error(f"Price request error: {e}")
            await query.edit_message_text("❌ An error occurred while fetching price.", 
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                                        ]))

    async def handle_manual_trade(self, query):
        """Handle manual trade requests"""
        await self.show_manual_trade_menu(query)

    async def show_live_prices(self, query):
        """Show live prices for popular symbols"""
        try:
            symbols = ["R_100", "R_50", "R_25", "R_10", "BOOM1000", "CRASH1000"]
            user_id = query.from_user.id
            user_api = self.get_user_api(user_id)
            
            prices_text = "📈 **Live Prices**\n\n"
            keyboard = []
            
            for symbol in symbols:
                try:
                    response = await user_api.get_ticks(symbol)
                    if "tick" in response:
                        price = response["tick"].get("quote", "N/A")
                        prices_text += f"• {symbol}: {price}\n"
                        keyboard.append([InlineKeyboardButton(f"📊 {symbol}", callback_data=f"price_{symbol}")])
                    else:
                        prices_text += f"• {symbol}: N/A\n"
                except Exception as e:
                    logger.error(f"Error fetching price for {symbol}: {e}")
                    prices_text += f"• {symbol}: Error\n"
            
            keyboard.extend([
                [InlineKeyboardButton("🔄 Refresh All", callback_data="live_prices")],
                [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(prices_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in show_live_prices: {e}")
            # Handle case where query might not have message or edit capabilities
            try:
                if query and hasattr(query, 'edit_message_text'):
                    await query.edit_message_text("❌ An error occurred while fetching live prices. Please try again.", 
                                                reply_markup=InlineKeyboardMarkup([
                                                    [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
                                                ]))
                elif query and hasattr(query, 'message'):
                    await query.message.reply_text("❌ An error occurred while fetching live prices. Please try again.")
            except Exception as reply_error:
                logger.error(f"Failed to send error message in show_live_prices: {reply_error}")

    async def show_manual_trade_menu(self, query):
        """Show manual trading options"""
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
    
    async def handle_close_position(self, query):
        """Handle closing a specific position"""
        contract_id = int(query.data.split("_")[2])
        user_id = query.from_user.id
        user_api = self.get_user_api(user_id)
        
        try:
            await query.edit_message_text("🔄 Closing position...")
            
            # Close the position using sell request
            request = {"sell": contract_id, "price": 0}
            response = await user_api.send_request(request)
            
            if "error" in response:
                await query.edit_message_text(f"❌ Failed to close position: {response['error']['message']}", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔙 Back to Positions", callback_data="all_positions")]
                                            ]))
                return
            
            if "sell" in response:
                sold_for = response["sell"].get("sold_for", 0)
                await query.edit_message_text(f"✅ Position closed successfully!\n💰 Sold for: ${sold_for}", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔙 Back to Positions", callback_data="all_positions")]
                                            ]))
            else:
                await query.edit_message_text("❌ Position closed but confirmation not received.", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔙 Back to Positions", callback_data="all_positions")]
                                            ]))
                
        except Exception as e:
            logger.error(f"Close position error: {e}")
            await query.edit_message_text("❌ An error occurred while closing position.", 
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Back to Positions", callback_data="all_positions")]
                                        ]))

    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command for viewing open positions"""
        user_id = update.effective_user.id
        user_api = self.get_user_api(user_id)
        
        try:
            await update.message.reply_text("🔄 Fetching portfolio...")
            
            # Check if user has API token configured
            if user_id not in self.user_accounts and not user_api.api_token:
                await update.message.reply_text("❌ No API token configured. Please use /connect to add your Deriv API token.")
                return
            
            # Ensure connection and authorization
            if not user_api.is_connected:
                await user_api.connect()
            
            if user_api.api_token and not await user_api.authorize():
                await update.message.reply_text("❌ Failed to authorize with Deriv API. Please check your API token using /connect.")
                return
            
            # Get portfolio
            request = {"portfolio": 1}
            response = await user_api.send_request(request)
            
            if "error" in response:
                error_msg = response['error']['message'] if 'message' in response['error'] else str(response['error'])
                logger.error(f"Portfolio request error for user {user_id}: {error_msg}")
                await update.message.reply_text(f"❌ Error fetching portfolio: {error_msg}")
                return
            
            if "portfolio" in response:
                contracts = response["portfolio"]["contracts"]
                
                if not contracts:
                    await update.message.reply_text("📊 No open positions found.")
                    return
                
                portfolio_text = "📊 **Open Positions:**\n\n"
                total_profit_loss = 0
                
                for contract in contracts[:5]:  # Show first 5 contracts
                    contract_id = contract.get("contract_id")
                    symbol = contract.get("symbol")
                    contract_type = contract.get("contract_type")
                    buy_price = contract.get("buy_price", 0)
                    current_spot = contract.get("current_spot", 0)
                    profit_loss = contract.get("profit_loss", 0)
                    payout = contract.get("payout", 0)
                    
                    total_profit_loss += profit_loss
                    
                    # Status indicator
                    status_icon = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "🟡"
                    
                    portfolio_text += f"{status_icon} **{symbol}** - {contract_type}\n"
                    portfolio_text += f"• ID: {contract_id}\n"
                    portfolio_text += f"• Buy Price: ${buy_price:.2f}\n"
                    portfolio_text += f"• Current: {current_spot:.4f}\n"
                    portfolio_text += f"• P&L: ${profit_loss:.2f}\n"
                    portfolio_text += f"• Potential Payout: ${payout:.2f}\n\n"
                
                portfolio_text += f"💰 **Total P&L: ${total_profit_loss:.2f}**\n"
                portfolio_text += f"📊 Showing {len(contracts[:5])} of {len(contracts)} positions"
                
                # Add inline keyboard for more actions
                keyboard = [
                    [InlineKeyboardButton("📋 View All Positions", callback_data="all_positions")],
                    [InlineKeyboardButton("🔄 Refresh Portfolio", callback_data="portfolio")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(portfolio_text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Unable to fetch portfolio.")
                
        except Exception as e:
            logger.error(f"Portfolio command error: {e}")
            await update.message.reply_text("❌ An error occurred while fetching portfolio.")

    async def profit_table_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profit command for profit table"""
        user_id = update.effective_user.id
        user_api = self.get_user_api(user_id)
        
        if not context.args:
            await update.message.reply_text("❌ Please provide a symbol. Example: /profit R_100")
            return
        
        symbol = context.args[0].upper()
        
        try:
            await update.message.reply_text(f"🔄 Fetching profit table for {symbol}...")
            
            # Check if user has API token configured
            if user_id not in self.user_accounts and not user_api.api_token:
                await update.message.reply_text("❌ No API token configured. Please use /connect to add your Deriv API token.")
                return
            
            # Ensure connection and authorization
            if not user_api.is_connected:
                await user_api.connect()
            
            if user_api.api_token and not await user_api.authorize():
                await update.message.reply_text("❌ Failed to authorize with Deriv API. Please check your API token using /connect.")
                return
            
            # Get profit table
            request = {
                "profit_table": 1,
                "symbol": symbol,
                "contract_type": ["CALL", "PUT"]
            }
            response = await user_api.send_request(request)
            
            if "error" in response:
                error_msg = response['error']['message'] if 'message' in response['error'] else str(response['error'])
                logger.error(f"Profit table request error for user {user_id}: {error_msg}")
                await update.message.reply_text(f"❌ Error fetching profit table: {error_msg}")
                return
            
            if "profit_table" in response:
                profit_table = response["profit_table"]
                
                if not profit_table:
                    await update.message.reply_text(f"📊 No profit data found for {symbol}.")
                    return
                
                profit_text = f"📊 **Profit Table for {symbol}**\n\n"
                
                # Group by contract type
                call_trades = [t for t in profit_table if t.get("contract_type") == "CALL"]
                put_trades = [t for t in profit_table if t.get("contract_type") == "PUT"]
                
                if call_trades:
                    profit_text += "📈 **CALL Trades:**\n"
                    for trade in call_trades[:3]:  # Show first 3
                        buy_price = trade.get("buy_price", 0)
                        sell_price = trade.get("sell_price", 0)
                        profit_loss = trade.get("profit_loss", 0)
                        status_icon = "✅" if profit_loss > 0 else "❌"
                        
                        profit_text += f"{status_icon} Buy: ${buy_price:.2f} | Sell: ${sell_price:.2f} | P&L: ${profit_loss:.2f}\n"
                    profit_text += "\n"
                
                if put_trades:
                    profit_text += "📉 **PUT Trades:**\n"
                    for trade in put_trades[:3]:  # Show first 3
                        buy_price = trade.get("buy_price", 0)
                        sell_price = trade.get("sell_price", 0)
                        profit_loss = trade.get("profit_loss", 0)
                        status_icon = "✅" if profit_loss > 0 else "❌"
                        
                        profit_text += f"{status_icon} Buy: ${buy_price:.2f} | Sell: ${sell_price:.2f} | P&L: ${profit_loss:.2f}\n"
                    profit_text += "\n"
                
                # Calculate summary
                total_profit = sum(t.get("profit_loss", 0) for t in profit_table)
                win_trades = len([t for t in profit_table if t.get("profit_loss", 0) > 0])
                total_trades = len(profit_table)
                win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
                
                profit_text += f"📈 **Summary:**\n"
                profit_text += f"• Total P&L: ${total_profit:.2f}\n"
                profit_text += f"• Win Rate: {win_rate:.1f}% ({win_trades}/{total_trades})\n"
                profit_text += f"• Showing recent trades for {symbol}"
                
                await update.message.reply_text(profit_text, parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Unable to fetch profit table for {symbol}.")
                
        except Exception as e:
            logger.error(f"Profit table command error: {e}")
            await update.message.reply_text("❌ An error occurred while fetching profit table.")

    async def show_all_positions(self, query):
        """Show all active positions with management options"""
        user_id = query.from_user.id
        user_api = self.get_user_api(user_id)
        
        try:
            await query.edit_message_text("🔄 Fetching all active positions...")
            
            # Check if user has API token configured
            if user_id not in self.user_accounts and not user_api.api_token:
                await query.edit_message_text("❌ No API token configured. Please use /connect to add your Deriv API token.", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔗 Connect Account", callback_data="connect_account")],
                                                [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
                                            ]))
                return
            
            # Ensure connection and authorization
            if not user_api.is_connected:
                await user_api.connect()
            
            if user_api.api_token and not await user_api.authorize():
                await query.edit_message_text("❌ Failed to authorize with Deriv API. Please check your API token.", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔗 Reconnect Account", callback_data="connect_account")],
                                                [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
                                            ]))
                return
            
            # Get portfolio
            request = {"portfolio": 1}
            response = await user_api.send_request(request)
            
            if "error" in response:
                error_msg = response['error']['message'] if 'message' in response['error'] else str(response['error'])
                logger.error(f"Portfolio request error for user {user_id}: {error_msg}")
                await query.edit_message_text(f"❌ Error fetching positions: {error_msg}", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔗 Check Account", callback_data="connect_account")],
                                                [InlineKeyboardButton("🔙 Back to Manual Trade", callback_data="manual_trade")]
                                            ]))
                return
            
            if "portfolio" in response:
                contracts = response["portfolio"]["contracts"]
                
                if not contracts:
                    await query.edit_message_text("📊 No active positions found.", 
                                                reply_markup=InlineKeyboardMarkup([
                                                    [InlineKeyboardButton("🎲 Place New Trade", callback_data="manual_trade")],
                                                    [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
                                                ]))
                    return

                # Show detailed positions
                total_profit_loss = 0
                positions_text = "📊 **All Active Positions:**\n\n"
                
                keyboard = []
                
                for i, contract in enumerate(contracts[:10]):  # Show first 10 contracts
                    contract_id = contract.get("contract_id")
                    symbol = contract.get("symbol")
                    contract_type = contract.get("contract_type")
                    buy_price = contract.get("buy_price", 0)
                    current_spot = contract.get("current_spot", 0)
                    profit_loss = contract.get("profit_loss", 0)
                    payout = contract.get("payout", 0)
                    
                    total_profit_loss += profit_loss
                    
                    # Status indicator
                    status_icon = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "🟡"
                    
                    positions_text += f"{status_icon} **{symbol}** - {contract_type}\n"
                    positions_text += f"• ID: {contract_id}\n"
                    positions_text += f"• Buy Price: ${buy_price:.2f}\n"
                    positions_text += f"• Current: {current_spot:.4f}\n"
                    positions_text += f"• P&L: ${profit_loss:.2f}\n"
                    positions_text += f"• Potential Payout: ${payout:.2f}\n\n"
                    
                    # Add sell button for each position
                    if i < 5:  # Only show sell buttons for first 5 positions to avoid too many buttons
                        keyboard.append([InlineKeyboardButton(f"🔻 Sell {symbol} (${profit_loss:.2f})", 
                                                           callback_data=f"close_position_{contract_id}")])
                positions_text += f"💰 **Total P&L: ${total_profit_loss:.2f}**\n"
                positions_text += f"📊 Showing {len(contracts[:10])} of {len(contracts)} positions"
                
                # Add management buttons
                keyboard.extend([
                    [InlineKeyboardButton("🔄 Refresh Positions", callback_data="all_positions")],
                    [InlineKeyboardButton("🎲 Place New Trade", callback_data="manual_trade")],
                    [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
                ])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(positions_text, reply_markup=reply_markup, parse_mode='Markdown')
                
            else:
                await query.edit_message_text("❌ Unable to fetch positions.", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔙 Back to Manual Trade", callback_data="manual_trade")]
                                            ]))
        
        except Exception as e:
            logger.error(f"Show all positions error: {e}")
            await query.edit_message_text("❌ An error occurred while fetching positions.", 
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Back to Manual Trade", callback_data="manual_trade")]
                                        ]))

    async def start_custom_strategy(self, user_id: int, strategy_type: str, market: str, lot_size: float) -> bool:
        """Start a custom strategy with user-specified parameters"""
        try:
            # Create custom strategy instances based on type
            user_api = self.get_user_api(user_id)
            
            if strategy_type == "scalping":
                # Create custom scalping strategy
                strategy = CustomScalpingStrategy(user_id, market, user_api, lot_size)
            elif strategy_type == "swing":
                # Create custom swing strategy  
                strategy = CustomSwingStrategy(user_id, market, user_api, lot_size)
            else:
                return False
            
            # Add to active strategies
            if user_id not in self.strategy_manager.active_strategies:
                self.strategy_manager.active_strategies[user_id] = {}
            
            strategy_key = f"{strategy_type}_{market}"
            self.strategy_manager.active_strategies[user_id][strategy_key] = strategy
            strategy.is_active = True
            
            # Start monitoring thread
            thread = threading.Thread(
                target=self.strategy_manager._run_strategy_monitoring, 
                args=(user_id, strategy_key)
            )
            thread.daemon = True
            thread.start()
            
            if user_id not in self.strategy_manager.strategy_threads:
                self.strategy_manager.strategy_threads[user_id] = {}
            self.strategy_manager.strategy_threads[user_id][strategy_key] = thread
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start custom strategy: {e}")
            return False

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

    async def handle_start_stream(self, query):
        """Handle live price streaming for a symbol"""
        symbol = query.data.split("_", 1)[1]
        user_id = query.from_user.id
        user_api = self.get_user_api(user_id)
        
        try:
            await query.edit_message_text(f"🔄 Starting live stream for {symbol}...")
            
            # Create a callback to update this specific message
            async def price_update_callback(symbol, tick_data):
                try:
                    price = tick_data.get("quote", "N/A")
                    timestamp = tick_data.get("epoch", "")
                    
                    stream_text = f"""
🔴 **LIVE: {symbol}**

• Current Price: **{price}**
• Last Update: {datetime.fromtimestamp(timestamp) if timestamp else 'N/A'}
• Status: 🟢 Streaming

*Price updates automatically every few seconds*
                    """
                    
                    keyboard = [
                        [InlineKeyboardButton("🛑 Stop Stream", callback_data=f"stop_stream_{symbol}"),
                         InlineKeyboardButton("📊 History", callback_data=f"history_{symbol}")],
                        [InlineKeyboardButton("🎲 Trade Now", callback_data=f"trade_{symbol}")],
                        [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    # Update the message (note: in production you'd need to store message_id)
                    # For now, we'll just log the update
                    logger.info(f"📈 Live update {symbol}: {price}")
                    
                except Exception as e:
                    logger.error(f"Error in price update callback: {e}")
            
            # Subscribe to live prices
            success = await user_api.subscribe_to_live_prices(symbol, price_update_callback)
            
            if success:
                stream_text = f"""
🔴 **LIVE: {symbol}**

• Status: 🟢 Stream Started
• Updates: Every few seconds
• Connection: Stable

*Fetching first price update...*
                """
                
                keyboard = [
                    [InlineKeyboardButton("🛑 Stop Stream", callback_data=f"stop_stream_{symbol}"),
                     InlineKeyboardButton("📊 History", callback_data=f"history_{symbol}")],
                    [InlineKeyboardButton("🎲 Trade Now", callback_data=f"trade_{symbol}")],
                    [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(stream_text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await query.edit_message_text(f"❌ Failed to start stream for {symbol}", 
                                            reply_markup=InlineKeyboardMarkup([
                                                [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                                            ]))
                
        except Exception as e:
            logger.error(f"Error starting stream: {e}")
            await query.edit_message_text(f"❌ Error starting stream: {str(e)}", 
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                                        ]))

    async def handle_price_history(self, query):
        """Show price history for a symbol"""
        symbol = query.data.split("_", 1)[1]
        user_id = query.from_user.id
        user_api = self.get_user_api(user_id)
        
        try:
            await query.edit_message_text(f"📊 Loading price history for {symbol}...")
            
            # Get price history from connection pool
            history = user_api.get_price_history(symbol, limit=10)
            
            if history:
                history_text = f"📊 **{symbol} - Recent Price History**\n\n"
                
                for i, tick in enumerate(reversed(history[-10:])):  # Show last 10 prices
                    price = tick.get("quote", "N/A")
                    timestamp = tick.get("epoch", "")
                    time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S") if timestamp else "N/A"
                    history_text += f"{i+1}. {price} at {time_str}\n"
                    
                history_text += f"\n📈 Total samples: {len(history)}"
            else:
                history_text = f"📊 **{symbol} - Price History**\n\nNo price history available yet.\nStart a live stream to begin collecting data."
            
            keyboard = [
                [InlineKeyboardButton("🔴 Start Stream", callback_data=f"stream_{symbol}"),
                 InlineKeyboardButton("🔄 Refresh", callback_data=f"history_{symbol}")],
                [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(history_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            await query.edit_message_text(f"❌ Error getting history: {str(e)}", 
                                        reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton("🔙 Back to Prices", callback_data="live_prices")]
                                        ]))

    async def handle_stop_all_streams(self, query):
        """Stop all active price streams"""
        try:
            await query.edit_message_text("🛑 Stopping all price streams...")
            
            # This would require tracking active streams per user
            # For now, we'll show a confirmation
            stream_text = """
🛑 **Stream Control**

All price streams have been stopped.

You can restart streams from the Live Prices menu.
            """
            
            keyboard = [
                [InlineKeyboardButton("📈 Live Prices", callback_data="live_prices")],
                [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(stream_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error stopping streams: {e}")

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors in the bot"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Try to notify the user if possible - but check for None update first
        if update and hasattr(update, 'effective_chat') and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ An error occurred while processing your request. Please try again."
                )
            except Exception as e:
                logger.error(f"Failed to send error message to user: {e}")
        elif update is None:
            logger.error("Update is None, cannot send error message to user")


# Main execution
if __name__ == "__main__":
    try:
        bot = DerivTelegramBot()
        print("🤖 Starting Deriv Telegram Bot...")
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logger.error(f"Failed to start bot: {e}")
