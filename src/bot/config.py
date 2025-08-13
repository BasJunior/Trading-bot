"""
Deriv Telegram Bot - Configuration Management
Handles all configuration settings and environment variables
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class BotConfig:
    """Bot configuration settings"""
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    # Deriv API Configuration
    DERIV_APP_ID: str = os.getenv('DERIV_APP_ID', '1089')
    DERIV_API_TOKEN: Optional[str] = os.getenv('DERIV_API_TOKEN')
    DERIV_WS_URL: str = 'wss://ws.derivws.com/websockets/v3'
    
    # Bot Settings
    BOT_NAME: str = os.getenv('BOT_NAME', 'DerivTradingBot')
    BOT_VERSION: str = os.getenv('BOT_VERSION', '1.0.0')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'bot.log')
    
    # Feature Flags
    ENABLE_MT5: bool = os.getenv('ENABLE_MT5', 'true').lower() == 'true'
    ENABLE_AUTO_TRADING: bool = os.getenv('ENABLE_AUTO_TRADING', 'true').lower() == 'true'
    ENABLE_DEMO_MODE: bool = os.getenv('ENABLE_DEMO_MODE', 'true').lower() == 'true'
    
    # Security Settings
    MAX_USERS: int = int(os.getenv('MAX_USERS', '100'))
    RATE_LIMIT_REQUESTS: int = int(os.getenv('RATE_LIMIT_REQUESTS', '30'))
    RATE_LIMIT_WINDOW: int = int(os.getenv('RATE_LIMIT_WINDOW', '60'))
    
    # Trading Limits
    MAX_POSITION_SIZE: float = float(os.getenv('MAX_POSITION_SIZE', '1000'))
    MAX_DAILY_LOSS: float = float(os.getenv('MAX_DAILY_LOSS', '500'))
    MAX_OPEN_POSITIONS: int = int(os.getenv('MAX_OPEN_POSITIONS', '10'))
    
    # Timeouts and Intervals
    API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', '30'))
    HEARTBEAT_INTERVAL: int = int(os.getenv('HEARTBEAT_INTERVAL', '30'))
    RECONNECT_DELAY: int = int(os.getenv('RECONNECT_DELAY', '5'))
    
    # Strategy Settings
    DEFAULT_STRATEGY_AMOUNT: float = float(os.getenv('DEFAULT_STRATEGY_AMOUNT', '10'))
    STRATEGY_MAX_CONCURRENT: int = int(os.getenv('STRATEGY_MAX_CONCURRENT', '3'))
    STRATEGY_COOLDOWN: int = int(os.getenv('STRATEGY_COOLDOWN', '60'))
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        if not self.DERIV_APP_ID:
            raise ValueError("DERIV_APP_ID is required")
        
        if self.MAX_USERS <= 0:
            raise ValueError("MAX_USERS must be positive")
        
        if self.MAX_POSITION_SIZE <= 0:
            raise ValueError("MAX_POSITION_SIZE must be positive")
        
        return True

# Global configuration instance
Config = BotConfig()

# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("Please check your .env file and ensure all required variables are set.")
    exit(1)

# Export for backward compatibility
TELEGRAM_BOT_TOKEN = Config.TELEGRAM_BOT_TOKEN
DERIV_APP_ID = Config.DERIV_APP_ID
DERIV_API_TOKEN = Config.DERIV_API_TOKEN
