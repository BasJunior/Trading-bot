#!/usr/bin/env python3
"""
MT5 CFD Trading Integration Guide
How to add CFD and Multiplier trading to your Deriv Telegram Bot
"""

# 📊 MT5 CFD TRADING INTEGRATION GUIDE

"""
===============================================================================
🚀 ADDING CFD TRADING TO YOUR DERIV TELEGRAM BOT
===============================================================================

Your current bot supports Digital Options only. This guide shows how to add
CFD and Multiplier trading capabilities using MetaTrader 5 (MT5).

===============================================================================
📋 WHAT YOU'LL GET
===============================================================================

✅ CFD Trading:
- Forex pairs (EUR/USD, GBP/USD, etc.)
- Stock indices (US30, NAS100, GER40, etc.)
- Commodities (Gold, Silver, Oil, etc.)
- Cryptocurrency CFDs (BTC/USD, ETH/USD, etc.)

✅ Advanced Features:
- Variable lot sizes
- Stop Loss and Take Profit
- Leverage trading
- Real-time P&L
- Position management
- Account analytics

✅ Risk Management:
- Margin calculations
- Maximum drawdown limits
- Position sizing controls
- Real-time risk monitoring

===============================================================================
🛠️ INSTALLATION STEPS
===============================================================================

Step 1: Install MT5 Platform
1. Download MetaTrader 5 from MetaQuotes
2. Install on your system (Windows/Mac/Linux)
3. Create a demo account or use existing account

Step 2: Install Python Package
```bash
pip install MetaTrader5
pip install -r requirements_mt5.txt
```

Step 3: Test MT5 Connection
```python
import MetaTrader5 as mt5

# Test connection
if mt5.initialize():
    print("✅ MT5 initialized successfully")
    print(f"MT5 version: {mt5.version()}")
    mt5.shutdown()
else:
    print("❌ MT5 initialization failed")
```

===============================================================================
🔗 TELEGRAM BOT INTEGRATION
===============================================================================

The mt5_cfd_trading.py module provides these new commands:

Bot Commands (New):
/mt5_connect - Connect MT5 account
/cfd_trade - Place CFD trade
/cfd_positions - View open CFD positions  
/cfd_close - Close CFD position
/mt5_balance - Check MT5 account balance

Example Usage:
1. User: /mt5_connect
   Bot: "Please provide your MT5 login credentials"
   
2. User: /cfd_trade EURUSD BUY 0.1
   Bot: "✅ CFD trade placed: EUR/USD BUY 0.1 lots"
   
3. User: /cfd_positions
   Bot: Shows all open CFD positions with real-time P&L

===============================================================================
💻 CODE INTEGRATION EXAMPLE
===============================================================================

Add to your telegram_bot.py:

```python
# Import the MT5 module
from mt5_cfd_trading import (
    setup_user_mt5_account, 
    place_cfd_trade, 
    close_cfd_trade,
    get_cfd_positions,
    get_mt5_account_info
)

# Add new command handlers
async def mt5_connect_command(update, context):
    '''Connect user's MT5 account'''
    # Implementation here
    pass

async def cfd_trade_command(update, context):
    '''Place CFD trade'''
    # Implementation here  
    pass

# Add to your bot setup
def setup_handlers(self):
    # ...existing handlers...
    
    # New MT5 handlers
    self.application.add_handler(CommandHandler("mt5_connect", self.mt5_connect_command))
    self.application.add_handler(CommandHandler("cfd_trade", self.cfd_trade_command))
    self.application.add_handler(CommandHandler("cfd_positions", self.cfd_positions_command))
```

===============================================================================
🎯 ENHANCED MAIN MENU
===============================================================================

Update your main menu to include CFD options:

```python
keyboard = [
    [InlineKeyboardButton("💰 Balance", callback_data="balance")],
    [InlineKeyboardButton("🎲 Digital Options", callback_data="manual_trade")],
    [InlineKeyboardButton("📊 CFD Trading", callback_data="cfd_menu")],  # NEW
    [InlineKeyboardButton("📋 All Positions", callback_data="all_positions")],
    [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
]
```

CFD Trading Submenu:
- 📈 Open CFD Position
- 📉 Close CFD Position  
- 📊 CFD Portfolio
- 💱 Forex CFDs
- 🏛️ Index CFDs
- 🥇 Commodity CFDs
- 🪙 Crypto CFDs

===============================================================================
⚙️ CONFIGURATION
===============================================================================

Add to your config.py:

```python
class Config:
    # ...existing config...
    
    # MT5 Configuration
    MT5_ENABLED = os.getenv('MT5_ENABLED', 'False').lower() == 'true'
    MT5_DEFAULT_SERVER = os.getenv('MT5_DEFAULT_SERVER', 'Deriv-Demo')
    
    # CFD Trading Limits
    CFD_MAX_LOT_SIZE = float(os.getenv('CFD_MAX_LOT_SIZE', '10.0'))
    CFD_MIN_LOT_SIZE = float(os.getenv('CFD_MIN_LOT_SIZE', '0.01'))
    CFD_MAX_POSITIONS = int(os.getenv('CFD_MAX_POSITIONS', '20'))
```

Add to your .env file:

```env
# MT5 CFD Trading
MT5_ENABLED=true
MT5_DEFAULT_SERVER=Deriv-Demo
CFD_MAX_LOT_SIZE=10.0
CFD_MIN_LOT_SIZE=0.01
CFD_MAX_POSITIONS=20
```

===============================================================================
🛡️ RISK MANAGEMENT FEATURES
===============================================================================

Built-in Safety Features:

1. Position Size Limits:
   - Maximum lot size per trade
   - Maximum number of open positions
   - Account equity checks

2. Stop Loss Protection:
   - Automatic SL calculation
   - Maximum risk per trade (% of equity)
   - Forced SL on all trades

3. Margin Monitoring:
   - Real-time margin level tracking
   - Margin call alerts
   - Position auto-closure at low margin

4. Account Protection:
   - Daily loss limits
   - Maximum drawdown alerts
   - Emergency position closure

===============================================================================
📊 EXAMPLE CFD TRADING FLOW
===============================================================================

User Trading Session:

1. Connect MT5 Account:
   User: /mt5_connect
   Bot: "Please enter your MT5 credentials"
   User: Provides login, password, server
   Bot: "✅ MT5 account connected successfully"

2. Check Account:
   User: /mt5_balance  
   Bot: "💰 MT5 Account: $10,000 | Free Margin: $9,500"

3. Place CFD Trade:
   User: /cfd_trade EURUSD BUY 0.1
   Bot: "📊 CFD Trade Proposal:
         Symbol: EUR/USD
         Direction: BUY
         Volume: 0.1 lots
         Current Price: 1.0850
         Estimated Margin: $108
         
         ✅ Confirm | ❌ Cancel"

4. Monitor Positions:
   User: /cfd_positions
   Bot: "📊 Open CFD Positions:
         🟢 EUR/USD BUY 0.1 | P&L: +$25.50
         🔴 GBP/USD SELL 0.05 | P&L: -$12.30
         
         Total P&L: +$13.20"

===============================================================================
🔧 TROUBLESHOOTING
===============================================================================

Common Issues:

1. "MT5 initialization failed":
   - Ensure MT5 platform is installed
   - Check MT5 is running
   - Verify MetaTrader5 package installed

2. "Login failed":
   - Check credentials are correct
   - Verify server name
   - Ensure account allows API trading

3. "Symbol not found":
   - Check symbol name spelling
   - Verify symbol is available on broker
   - Try alternative symbol names

4. "Insufficient margin":
   - Check account balance
   - Reduce position size
   - Close other positions

===============================================================================
📚 LEARNING RESOURCES
===============================================================================

CFD Trading Basics:
- Understand leverage and margin
- Learn about spread costs
- Practice with demo account first
- Study risk management principles

MT5 Platform:
- Explore MT5 interface
- Learn about different order types
- Understand market depth
- Practice manual trading first

Bot Integration:
- Test with small positions
- Monitor system performance
- Keep logs of all trades
- Regular system health checks

===============================================================================
✅ DEPLOYMENT CHECKLIST
===============================================================================

Before Going Live:

□ MT5 platform installed and tested
□ MetaTrader5 Python package installed
□ Demo account testing completed
□ Risk management rules configured
□ User authentication system ready
□ Error handling implemented
□ Logging system active
□ Backup procedures in place

Production Deployment:

□ Real account credentials secured
□ Position size limits set
□ Daily loss limits configured
□ User permission system active
□ Monitoring dashboards ready
□ Alert systems functional
□ Emergency stop procedures tested

===============================================================================

🚨 IMPORTANT DISCLAIMERS:

- CFD trading involves significant risk
- Leverage can amplify both profits and losses  
- Always use proper risk management
- Test thoroughly with demo accounts first
- Users should understand CFD risks before trading
- Consider regulatory requirements in your jurisdiction

Happy CFD Trading! 📈
"""

if __name__ == "__main__":
    print("📖 MT5 CFD Trading Integration Guide")
    print("This guide explains how to add CFD trading to your Deriv Telegram Bot.")
    print("Please read the complete guide above for detailed instructions.")
