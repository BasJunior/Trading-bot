#!/usr/bin/env python3
"""
Configuration file for Deriv Telegram Bot
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the bot"""
    
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Deriv API Configuration
    DERIV_APP_ID = os.getenv('DERIV_APP_ID', '1089')  # Default app ID
    DERIV_API_TOKEN = os.getenv('DERIV_API_TOKEN')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Trading Configuration
    DEFAULT_LOT_SIZE = float(os.getenv('DEFAULT_LOT_SIZE', '0.1'))
    MAX_TRADES_PER_HOUR = int(os.getenv('MAX_TRADES_PER_HOUR', '10'))
    
    # Risk Management
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '100.0'))
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '10.0'))
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        required_vars = {
            'TELEGRAM_BOT_TOKEN': cls.TELEGRAM_BOT_TOKEN,
            'DERIV_APP_ID': cls.DERIV_APP_ID,
        }
        
        missing_vars = []
        for var_name, var_value in required_vars.items():
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_deriv_websocket_url(cls):
        """Get the Deriv WebSocket URL"""
        return "wss://ws.derivws.com/websockets/v3"
    
    @classmethod
    def get_supported_symbols(cls):
        """Get list of supported trading symbols"""
        return [
            'R_75', 'R_100', 'R_50', 'R_25', 'R_10',
            'BOOM500', 'BOOM1000', 'CRASH500', 'CRASH1000',
            'frxEURUSD', 'frxGBPUSD', 'frxUSDJPY', 'frxAUDUSD',
            'frxEURGBP', 'frxEURJPY', 'frxGBPJPY'
        ]
    
    @classmethod
    def get_strategy_defaults(cls):
        """Get default strategy configurations"""
        return {
            'scalping': {
                'lot_size': 0.1,
                'duration': 5,
                'ema_period': 20,
                'rsi_period': 14,
                'rsi_overbought': 70,
                'rsi_oversold': 30
            },
            'swing': {
                'lot_size': 0.001,
                'duration': 10,
                'bb_period': 20,
                'bb_std_dev': 2,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9
            }
        }
