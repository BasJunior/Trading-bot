# Deriv Telegram Bot Repository

A comprehensive trading bot for Telegram that integrates with Deriv's API for automated and manual trading of digital options and CFDs.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/deriv-telegram-bot.git
cd deriv-telegram-bot

# Run automated setup
python scripts/deploy.py

# Start the bot
./start_bot.sh
```

## 📁 Repository Structure

```
deriv-telegram-bot/
├── 📁 src/                     # Source code modules
│   ├── 📁 bot/                 # Bot core functionality
│   ├── 📁 trading/             # Trading logic and APIs
│   └── 📁 strategies/          # Automated trading strategies
├── 📁 tests/                   # Test suite and validation
├── 📁 docs/                    # Documentation and guides
├── 📁 scripts/                 # Deployment and utility scripts
├── 📁 config/                  # Configuration templates
├── 📁 backup_files/            # Development backups
├── 📄 telegram_bot.py          # Main bot application
├── 📄 config.py               # Configuration management
├── 📄 requirements.txt        # Python dependencies
├── 📄 requirements_mt5.txt    # MT5 CFD trading dependencies
├── 📄 .env.example           # Environment configuration template
├── 📄 README.md              # This file
├── 📄 LICENSE                # MIT License
└── 📄 .gitignore             # Git ignore rules
```

## 🛠️ Features

### Core Trading Features
- **Digital Options**: Real-time trading with Deriv API
- **MT5 CFD Trading**: Forex, indices, and commodities
- **Automated Strategies**: Scalping and swing trading algorithms
- **Portfolio Management**: Position tracking and P&L analysis
- **Real-time Data**: Live price streaming and market analysis

### Bot Capabilities
- **Multi-user Support**: Each user connects their own account
- **Interactive Commands**: Full command-line interface
- **Inline Keyboards**: User-friendly button navigation
- **Error Handling**: Comprehensive error management
- **Security**: Secure API token handling and validation

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection
- Telegram Bot Token (from @BotFather)
- Deriv API Token (from app.deriv.com)
- Optional: MT5 account for CFD trading

## 🔧 Installation Methods

### Method 1: Automated Setup (Recommended)
```bash
python scripts/deploy.py
```

### Method 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Optional: Install MT5 support
pip install -r requirements_mt5.txt

# Configure environment
cp .env.example .env
# Edit .env with your tokens

# Start bot
python telegram_bot.py
```

### Method 3: Production Deployment
```bash
# For Linux servers
sudo ./scripts/deploy_production.sh

# With MT5 support
sudo ./scripts/deploy_production.sh --with-mt5
```

## ⚙️ Configuration

### Environment Variables
Edit `.env` file with your credentials:

```env
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
DERIV_APP_ID=your_deriv_app_id

# Optional
DERIV_API_TOKEN=default_api_token
ENABLE_MT5=true
MAX_USERS=100
```

### Interactive Setup
```bash
python setup_tokens.py
```

## 🚀 Usage

### Basic Commands
```
/start          - Start the bot and show main menu
/help           - Show all available commands
/connect TOKEN  - Connect your Deriv account
/balance        - Check account balance
/portfolio      - View open positions
```

### Trading Commands
```
/price SYMBOL   - Get live price for symbol
/manual_trade   - Interactive trading interface
/auto_trading   - Setup automated strategies
```

### MT5 CFD Commands
```
/mt5_setup LOGIN PASSWORD SERVER  - Connect MT5 account
/cfd_trade SYMBOL BUY 0.1         - Place CFD trade
/cfd_positions                     - View CFD positions
/cfd_close TICKET                  - Close CFD position
```

## 🧪 Testing

### Run Test Suite
```bash
# Basic tests
python tests/test_suite.py

# API connectivity test
python test_api_simple.py

# Comprehensive tests
python comprehensive_test_suite.py
```

### Manual Testing
```bash
# Test bot startup
python telegram_bot.py

# Test with demo account
# Send /start in Telegram
# Use /connect with demo token
```

## 📊 Monitoring

### Service Status
```bash
# Check if bot is running
ps aux | grep telegram_bot

# View logs
tail -f bot.log

# For production deployment
systemctl status deriv-telegram-bot
journalctl -u deriv-telegram-bot -f
```

### Performance Monitoring
- Memory usage tracking
- API response times
- Error rate monitoring
- User activity analytics

## 🔐 Security

### Best Practices
- Never commit `.env` files
- Use environment variables for sensitive data
- Implement rate limiting
- Validate all user inputs
- Monitor for unusual activity

### Trading Safety
- Position size limits
- Daily loss thresholds
- Account balance checks
- Emergency stop mechanisms

## 🤝 Contributing

### Development Setup
```bash
# Fork and clone repository
git clone https://github.com/yourusername/deriv-telegram-bot.git
cd deriv-telegram-bot

# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
python tests/test_suite.py

# Commit and push
git commit -m "Add your feature"
git push origin feature/your-feature
```

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include error handling
- Write tests for new features
- Update documentation

### Pull Request Process
1. Ensure all tests pass
2. Update documentation
3. Add changelog entry
4. Request review
5. Address feedback

## 📖 Documentation

- [User Guide](docs/USER_GUIDE.md) - Complete user manual
- [API Documentation](docs/API.md) - Technical API reference
- [Trading Strategies](docs/STRATEGIES.md) - Strategy documentation
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues

## 🆘 Support

### Getting Help
- 📚 Check documentation in `docs/` folder
- 🐛 Report issues on GitHub Issues
- 💬 Join community discussions
- 📧 Contact maintainers

### Common Issues
- **Bot not starting**: Check Python version and dependencies
- **Connection errors**: Verify API tokens and network
- **Trading failures**: Check account balance and permissions

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python telegram_bot.py
```

## 🔄 Updates

### Updating the Bot
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart bot
./start_bot.sh
```

### Version Information
- Current Version: 1.0.0
- Deriv API: v3
- Telegram Bot API: Latest
- Python: 3.8+ required

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**Risk Warning**: Trading financial instruments involves substantial risk of loss and may not be suitable for all investors. This software is provided "as-is" without warranty. Users trade at their own risk.

**Not Financial Advice**: This bot is a tool for trade execution. It does not provide financial advice. Conduct your own research and consider your financial situation before trading.

## 🔗 Related Projects

- [Deriv API Documentation](https://developers.deriv.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [MetaTrader 5 Python](https://www.mql5.com/en/docs/integration/python_metatrader5)

## 🏷️ Tags

`trading-bot` `telegram` `deriv` `mt5` `forex` `cryptocurrency` `automation` `python` `financial-markets` `algorithmic-trading`

---

**Made with ❤️ for the trading community**

For support: [Create an Issue](https://github.com/yourusername/deriv-telegram-bot/issues)
