# 🚀 Deriv Telegram Trading Bot

An advanced automated trading bot for Deriv platform with sophisticated trading strategies, user-friendly Telegram interface, and comprehensive risk management.

## 📋 Features

### 🎯 Trading Strategies
- **Scalping Strategy**: EMA + RSI for quick profits on volatility
- **Swing Trading**: Bollinger Bands + MACD for trend following
- **Real-time Analysis**: Advanced technical indicators
- **Risk Management**: Configurable stop-loss and position sizing

### 🤖 Telegram Interface
- **Button-based UI**: Easy strategy selection and configuration
- **Real-time Updates**: Live trade notifications and results
- **Multi-account Support**: Manage multiple trading accounts
- **Session Management**: Persistent user sessions and preferences
- **Async Architecture**: Fixed event loop issues for stable operation

### 🔧 Technical Features
- **Async Architecture**: Non-blocking operations for better performance
- **Event Loop Management**: Proper async/await handling for stability
- **Error Handling**: Comprehensive error recovery and logging
- **Configuration Management**: Environment-based configuration
- **Testing Suite**: Complete test coverage for all components

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Run the automated setup
./setup.sh

# Or manual setup
pip install -r requirements.txt
```

### 2. Configure Tokens
```bash
# Interactive setup wizard
python3 setup_tokens.py

# Or manual configuration
cp .env.example .env
# Edit .env with your tokens
```

### 3. Test Configuration
```bash
# Test Deriv App ID
python3 test_app_id.py

# Test Deriv API Token
python3 test_token.py

# Test Telegram Bot
python3 test_bot.py
```

### 4. Start Trading
```bash
# Start the bot
./start_bot.sh

# Or run directly
python3 telegram_bot.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DERIV_APP_ID=1089
DERIV_API_TOKEN=your_deriv_api_token_here

# Optional Trading Settings
DEFAULT_LOT_SIZE=0.1
MAX_TRADES_PER_HOUR=10
MAX_DAILY_LOSS=100.0
MAX_POSITION_SIZE=10.0
LOG_LEVEL=INFO
```

### Getting Tokens

#### Telegram Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the token provided by BotFather

#### Deriv API Token
1. Go to [Deriv App](https://app.deriv.com/)
2. Login to your account
3. Go to Settings → API Token
4. Create a new token with 'Trading' permission
5. Copy the token

#### Deriv App ID
1. Go to [Deriv Developers](https://developers.deriv.com/)
2. Register and create a new app
3. Copy the App ID
4. Or use the default: `1089`

## 📊 Trading Strategies

### Scalping Strategy (EMA + RSI)
- **Best for**: Quick profits on volatility
- **Indicators**: 20-period EMA + 14-period RSI
- **Markets**: R_75, R_100, R_50, BOOM500, BOOM1000
- **Duration**: 5 ticks
- **Risk**: Medium

### Swing Trading (Bollinger Bands + MACD)
- **Best for**: Trend following
- **Indicators**: Bollinger Bands (20, 2) + MACD (12, 26, 9)
- **Markets**: R_75, R_100, R_25, CRASH500, CRASH1000
- **Duration**: 10 ticks
- **Risk**: Low to Medium

## 🛠️ Available Scripts

### Setup Scripts
- `setup.sh` - Complete environment setup
- `setup_tokens.py` - Interactive token configuration wizard
- `start_bot.sh` - Quick bot startup

### Test Scripts
- `test_app_id.py` - Validate Deriv App ID and basic connectivity
- `test_token.py` - Validate Deriv API token and permissions
- `test_bot.py` - Comprehensive bot functionality tests
- `check_bot_status.py` - Quick bot status and connectivity check

### Core Files
- `telegram_bot.py` - Main bot application
- `config.py` - Configuration management
- `user_management.py` - User session and data management

## 🔍 Testing

### Run All Tests
```bash
# Complete test suite
python3 test_bot.py

# Individual component tests
python3 test_app_id.py
python3 test_token.py
```

### Test Output Example
```
🧪 Starting Deriv App ID Tests
==================================================

📋 Running Basic Connection...
✅ WebSocket connection established

📋 Running Ping/Pong...
✅ Ping/pong successful - API is responsive

📋 Running Server Time...
✅ Server time retrieved: 1752695621

📋 Running App ID Validation...
✅ App ID is valid - Website status: up

📋 Running Active Symbols...
✅ Active symbols retrieved: 38 symbols available

🎉 All tests passed! Your Deriv App ID configuration is working correctly.
```

## 🎮 Using the Bot

### Start Trading
1. Send `/start` to your bot on Telegram
2. Choose your trading strategy
3. Select market and lot size
4. Bot will analyze and execute trades automatically

### Bot Commands
- `/start` - Start the bot and show main menu
- `/help` - Show help information
- `/stats` - View trading statistics
- `/stop` - Stop active trading sessions

### Trading Interface
The bot provides an intuitive button-based interface:
- **Strategy Selection**: Choose between Scalping and Swing trading
- **Market Selection**: Pick from available markets (R_75, R_100, etc.)
- **Lot Size**: Configure position size
- **Real-time Updates**: Live trade notifications

## 📈 Performance & Monitoring

### Trading Statistics
- Win/Loss ratios
- Daily/Weekly performance
- Risk metrics
- Account balance tracking

### Risk Management
- Maximum daily loss limits
- Position size controls
- Trade frequency limits
- Stop-loss mechanisms

## 🔒 Security

### Best Practices
- Keep API tokens secure
- Use environment variables
- Regular token rotation
- Monitor account activity

### Permissions
- Bot only needs 'Trading' permission
- No withdrawal permissions required
- Read-only access to account data

## 📚 Documentation

### Additional Guides
- [Trading Strategies Guide](TRADING_STRATEGIES_GUIDE.md) - Detailed strategy documentation
- [Multi-Account Guide](MULTI_ACCOUNT_GUIDE.md) - Managing multiple accounts
- [Setup Guide](SETUP_GUIDE.md) - Detailed setup instructions
- [Bot Fix Summary](BOT_FIX_SUMMARY.md) - Recent fixes and improvements

### Troubleshooting
- Check `.env` file configuration
- Verify internet connection
- Test API tokens individually
- Review log files for errors
- For async issues, ensure proper event loop handling

### Common Issues
- **Bot Not Responsive**: Check if bot is running with `ps aux | grep telegram_bot.py`
- **AsyncIO Event Loop Errors**: Fixed in latest version with proper async/await handling
- **WebSocket Connection Issues**: Check network connectivity and API tokens
- **Bot Not Responding**: Verify Telegram bot token and permissions
- **Trading Errors**: Check Deriv account balance and API token permissions

### Quick Bot Troubleshooting
```bash
# 1. Quick status check
python3 check_bot_status.py

# 2. Check if bot is running
ps aux | grep telegram_bot.py

# 3. If not running, start it
python3 telegram_bot.py

# 4. Test bot connection
python3 -c "
import requests
from config import Config
response = requests.get(f'https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getMe')
print('Bot status:', 'OK' if response.json().get('ok') else 'ERROR')
"

# 5. Check logs for errors
tail -f bot.log  # if logging to file
```

## 🤝 Contributing

### Development Setup
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python3 test_bot.py`
4. Make changes and test

### Code Structure
- `telegram_bot.py` - Main application logic
- `config.py` - Configuration management
- `user_management.py` - User data handling
- `test_*.py` - Test suites

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This bot is for educational purposes. Trading involves risk. Always:
- Test with demo accounts first
- Use proper risk management
- Monitor your trades
- Never risk more than you can afford to lose

## 📞 Support

For issues and questions:
1. Check the documentation
2. Run diagnostic tests
3. Review log files
4. Open an issue if needed

---

**Happy Trading! 🚀**
