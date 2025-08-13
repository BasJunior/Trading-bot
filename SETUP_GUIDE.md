# 🛠️ Setup Guide - Deriv Telegram Bot

This comprehensive guide will walk you through setting up the Deriv Telegram Bot from scratch.

## 📋 Prerequisites

### System Requirements
- **Python 3.8+**: Required for running the bot
- **Internet Connection**: For API connections
- **Telegram Account**: For bot interaction
- **Deriv Account**: For trading operations

### Account Setup
1. **Deriv Account**: Register at [app.deriv.com](https://app.deriv.com)
2. **Telegram Bot**: Create via [@BotFather](https://t.me/BotFather)
3. **API Tokens**: Generate from respective platforms

## 🚀 Installation Methods

### Method 1: Automated Setup (Recommended)
```bash
# Clone or download the project
cd deriv_telegram_bot

# Run the automated setup
./setup.sh
```

### Method 2: Manual Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (if needed)
# On macOS: brew install python3
# On Ubuntu: sudo apt-get install python3 python3-pip

# Configure environment
cp .env.example .env
# Edit .env with your tokens
```

## 🔧 Configuration

### Step 1: Environment Variables

Create a `.env` file in the project root:

```env
# Required Tokens
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DERIV_APP_ID=1089
DERIV_API_TOKEN=your_deriv_api_token_here

# Trading Configuration
DEFAULT_LOT_SIZE=0.1
MAX_TRADES_PER_HOUR=10
MAX_DAILY_LOSS=100.0
MAX_POSITION_SIZE=10.0

# System Configuration
LOG_LEVEL=INFO
```

### Step 2: Token Configuration

#### Interactive Setup (Recommended)
```bash
python3 setup_tokens.py
```

This wizard will guide you through:
- Telegram bot token setup
- Deriv API configuration
- Trading parameters
- Connection testing

#### Manual Configuration

**Telegram Bot Token:**
1. Message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose bot name and username
4. Copy the token provided
5. Add to `.env` as `TELEGRAM_BOT_TOKEN`

**Deriv API Token:**
1. Login to [app.deriv.com](https://app.deriv.com)
2. Go to Settings → API Token
3. Create new token with 'Trading' permission
4. Copy the token
5. Add to `.env` as `DERIV_API_TOKEN`

**Deriv App ID:**
1. Go to [developers.deriv.com](https://developers.deriv.com)
2. Register and create a new app
3. Copy the App ID
4. Add to `.env` as `DERIV_APP_ID`
5. Or use default: `1089`

## 🧪 Testing Configuration

### Step 1: Test Individual Components
```bash
# Test Deriv App ID
python3 test_app_id.py

# Test Deriv API Token
python3 test_token.py

# Test complete bot functionality
python3 test_bot.py
```

### Step 2: Verify Test Results
Each test should show:
- ✅ All tests passed
- Connection successful
- Valid tokens
- API responses working

### Step 3: Troubleshooting Tests
If tests fail:
1. Check internet connection
2. Verify tokens in `.env`
3. Ensure no typos in configuration
4. Check Deriv account status

## 🎮 Running the Bot

### Method 1: Using Startup Script
```bash
# Make executable (first time only)
chmod +x start_bot.sh

# Start the bot
./start_bot.sh
```

### Method 2: Direct Python Execution
```bash
python3 telegram_bot.py
```

### Method 3: Background Execution
```bash
# Run in background
nohup python3 telegram_bot.py &

# Check if running
ps aux | grep telegram_bot.py

# Stop background process
pkill -f telegram_bot.py
```

## 📊 Initial Bot Usage

### Step 1: Start Conversation
1. Open Telegram
2. Find your bot by username
3. Send `/start`
4. You should see the main menu

### Step 2: Configure Trading
1. Choose "⚙️ Settings"
2. Select trading strategy
3. Choose market and lot size
4. Enable/disable notifications

### Step 3: Start Trading
1. Choose "🚀 Start Trading"
2. Select strategy (Scalping or Swing)
3. Choose market (R_75, R_100, etc.)
4. Set lot size
5. Monitor trades in real-time

## 🛡️ Security Setup

### API Token Security
- Never share API tokens
- Use environment variables only
- Rotate tokens regularly
- Monitor account activity

### Bot Security
- Use unique bot username
- Don't share bot link publicly
- Monitor bot conversations
- Set up user restrictions if needed

### Account Security
- Enable 2FA on Deriv account
- Use strong passwords
- Monitor trading activity
- Set up account alerts

## 📈 Performance Optimization

### Resource Management
- Monitor memory usage
- Check CPU performance
- Optimize trade frequency
- Manage log file sizes

### Network Optimization
- Stable internet connection
- Low latency preferred
- Backup connection available
- Monitor API response times

## 📁 File Structure

```
deriv_telegram_bot/
├── telegram_bot.py          # Main bot application
├── config.py               # Configuration management
├── user_management.py      # User session handling
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── setup.sh               # Automated setup script
├── start_bot.sh           # Bot startup script
├── setup_tokens.py        # Token configuration wizard
├── test_bot.py            # Comprehensive tests
├── test_token.py          # Token validation
├── test_app_id.py         # App ID validation
├── verify_project.py      # Project verification
└── docs/
    ├── README.md
    ├── TRADING_STRATEGIES_GUIDE.md
    ├── SETUP_GUIDE.md
    ├── MULTI_ACCOUNT_GUIDE.md
    └── BOT_FIX_SUMMARY.md
```

## 🔧 Advanced Configuration

### Custom Trading Parameters
```env
# Risk Management
MAX_DAILY_LOSS=100.0
MAX_POSITION_SIZE=10.0
STOP_LOSS_PERCENTAGE=5.0
TAKE_PROFIT_PERCENTAGE=10.0

# Strategy Parameters
EMA_PERIOD=20
RSI_PERIOD=14
BOLLINGER_PERIOD=20
MACD_FAST=12
MACD_SLOW=26
MACD_SIGNAL=9

# Notification Settings
SEND_TRADE_NOTIFICATIONS=true
SEND_BALANCE_UPDATES=true
NOTIFICATION_INTERVAL=300
```

### Logging Configuration
```env
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
LOG_FILE=bot.log        # Log file path
LOG_MAX_SIZE=10485760   # 10MB
LOG_BACKUP_COUNT=5      # Keep 5 backup files
```

## 🐛 Troubleshooting

### Common Issues

**1. Bot Not Starting**
```bash
# Check Python version
python3 --version

# Check dependencies
pip list

# Check configuration
python3 -c "from config import Config; Config.validate()"
```

**2. API Connection Issues**
```bash
# Test connectivity
python3 test_app_id.py
python3 test_token.py

# Check network
ping ws.binaryws.com
```

**3. Trading Issues**
```bash
# Check account balance
python3 -c "import asyncio; from telegram_bot import check_balance; asyncio.run(check_balance())"

# Verify permissions
# Check Deriv account → API Token → Permissions
```

**4. Telegram Issues**
```bash
# Test bot token
curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Check bot status
python3 -c "import requests; print(requests.get('https://api.telegram.org/bot<YOUR_TOKEN>/getMe').json())"
```

### Error Messages

**"Configuration Error"**
- Check `.env` file exists
- Verify all required variables are set
- Ensure no extra spaces in values

**"WebSocket Connection Failed"**
- Check internet connection
- Verify Deriv App ID
- Test with different network

**"Unauthorized"**
- Check API token validity
- Verify token permissions
- Regenerate token if needed

## 📞 Support

### Self-Help Resources
1. Run diagnostic tests: `python3 test_bot.py`
2. Check log files: `tail -f bot.log`
3. Verify configuration: `python3 verify_project.py`
4. Review documentation: `cat README.md`

### Getting Help
1. Check error messages in logs
2. Run individual test scripts
3. Verify account status
4. Review recent changes

### Debug Mode
```bash
# Run with debug logging
LOG_LEVEL=DEBUG python3 telegram_bot.py

# Test with verbose output
python3 test_bot.py --verbose
```

## 📚 Next Steps

After successful setup:
1. **Read Strategy Guide**: `cat TRADING_STRATEGIES_GUIDE.md`
2. **Configure Multi-Account**: `cat MULTI_ACCOUNT_GUIDE.md`
3. **Start Paper Trading**: Test with small amounts
4. **Monitor Performance**: Check stats regularly
5. **Optimize Settings**: Adjust based on results

## 🎯 Best Practices

### Trading
- Start with small lot sizes
- Test strategies thoroughly
- Monitor risk metrics
- Keep trading journal

### Technical
- Regular backups
- Monitor system resources
- Update dependencies
- Test before production

### Security
- Secure token storage
- Regular security reviews
- Monitor account activity
- Use strong authentication

---

**Setup Complete! 🎉**

Your Deriv Telegram Bot is now ready for trading. Start with `/start` in Telegram and begin your automated trading journey!
