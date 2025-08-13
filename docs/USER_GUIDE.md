# User Guide

## Getting Started

### 1. Finding the Bot
Search for your bot in Telegram using the username provided during setup.

### 2. Starting the Bot
Send `/start` to begin using the bot. You'll see the main menu with available options.

### 3. Connecting Your Account
To use real trading features, connect your Deriv account:
```
/connect YOUR_API_TOKEN
```

**Getting Your API Token:**
1. Go to https://app.deriv.com/account/api-token
2. Log in to your Deriv account
3. Create a new API token
4. Copy the token and use it with the `/connect` command

## Basic Commands

### Information Commands
- `/help` - Show all available commands
- `/balance` - Check your account balance
- `/account` - View account information
- `/symbols` - List available trading symbols

### Price Commands
- `/price SYMBOL` - Get current price for a symbol
- Live price streaming through inline buttons
- Price history and charts

### Portfolio Commands
- `/portfolio` - View open positions
- `/profit SYMBOL` - Show profit/loss history

## Digital Options Trading

### Manual Trading
1. Use `/manual_trade` or click "🎲 Manual Trade" button
2. Select market category (Volatility, Boom/Crash, Forex)
3. Choose symbol (e.g., R_100, BOOM500)
4. Select contract type (Call/Put, Higher/Lower)
5. Set amount and duration
6. Confirm and place trade

### Contract Types
- **Call/Put**: Predict if price will be higher or lower
- **Touch/No Touch**: Predict if price will touch a barrier
- **In/Out**: Predict if price stays within or goes outside barriers

### Managing Positions
- View all positions with `/portfolio`
- Close positions early using inline buttons
- Monitor real-time P&L

## MT5 CFD Trading

### Setup MT5 Account
1. Use `/mt5_connect` to start setup
2. Provide credentials with `/mt5_setup LOGIN PASSWORD SERVER`
3. Verify connection with `/mt5_balance`

### CFD Trading Commands
```
# Place trade
/cfd_trade EURUSD BUY 0.1

# With stop loss and take profit
/cfd_trade XAUUSD SELL 0.05 1950 1970

# View positions
/cfd_positions

# Close position
/cfd_close TICKET_NUMBER

# Check balance
/mt5_balance
```

### CFD Symbols
- **Forex**: EURUSD, GBPUSD, USDJPY, etc.
- **Indices**: US30, DE30, UK100, etc.
- **Commodities**: XAUUSD (Gold), XAGUSD (Silver), USOIL, etc.

## Automated Trading

### Available Strategies
1. **Scalping Strategy**: Quick trades based on EMA + RSI signals
2. **Swing Trading**: Trend following with Bollinger Bands + MACD

### Setting Up Auto Trading
1. Click "🤖 Auto Trading" in main menu
2. Select strategy type
3. Choose market (R_75, R_100, BOOM500, etc.)
4. Set lot size/amount per trade
5. Start strategy

### Monitoring Strategies
- Use "📊 Strategy Status" to monitor performance
- View win rate, profit/loss, and trade count
- Stop strategies anytime with "🛑 Stop All Strategies"

### Strategy Parameters
- **Lot Size**: Amount per trade ($0.1 - $10)
- **Market**: Symbol to trade
- **Risk Level**: Conservative, Moderate, Aggressive

## Live Prices and Market Data

### Real-Time Prices
- Use "📈 Live Prices" button for quick access
- Stream live prices for any symbol
- Price updates every few seconds

### Price History
- View recent price movements
- Historical data for analysis
- Export data for external analysis

### Market Analysis
- Technical indicators
- Support and resistance levels
- Market sentiment indicators

## Account Management

### Multiple Accounts
- Each user can connect their own account
- Secure token storage
- Account isolation between users

### Security Features
- API tokens encrypted in transit
- No permanent storage of credentials
- Rate limiting and abuse protection

### Account Types
- **Demo Accounts**: Practice trading without risk
- **Real Accounts**: Live trading with real money
- **MT5 Accounts**: CFD trading capabilities

## Settings and Configuration

### Bot Settings
- Notification preferences
- Display currency
- Time zone settings
- Language preferences (if supported)

### Trading Settings
- Default trade amounts
- Risk management parameters
- Auto-trading preferences
- Position size limits

### Privacy Settings
- Data sharing preferences
- Trading history visibility
- Performance analytics

## Safety and Risk Management

### Trading Limits
- Maximum position size: $1,000 per trade
- Maximum daily loss: $500
- Maximum open positions: 10

### Best Practices
1. **Start Small**: Begin with small amounts
2. **Use Demo**: Practice with demo accounts first
3. **Set Limits**: Define your risk tolerance
4. **Diversify**: Don't put all funds in one trade
5. **Monitor**: Regularly check your positions

### Risk Warnings
- Trading involves substantial risk of loss
- Past performance doesn't guarantee future results
- Only trade with money you can afford to lose
- Consider your investment objectives and risk tolerance

## Troubleshooting

### Common Issues

#### Bot Not Responding
1. Check internet connection
2. Try `/start` command again
3. Contact support if problem persists

#### Connection Errors
1. Verify API token is correct
2. Check Deriv account status
3. Ensure account has trading permissions

#### Trading Errors
1. Check account balance
2. Verify market is open
3. Ensure symbol is available for trading

### Getting Help
- Use `/help` for command reference
- Check error messages for specific guidance
- Contact support through GitHub issues
- Join community discussions

### Log Files
If reporting issues, check log files for error details:
- Bot logs: `bot.log`
- Error patterns and timestamps
- Include relevant log excerpts when reporting issues

## Advanced Features

### Webhook Integration
For advanced users, the bot supports webhook notifications for external systems.

### API Access
Direct API access for custom integrations and automated systems.

### Custom Strategies
Framework for implementing custom trading strategies with backtesting capabilities.

### Data Export
Export trading data and performance metrics for external analysis.

## Support and Community

### Documentation
- Complete API documentation in `docs/API.md`
- Technical documentation for developers
- Integration guides and examples

### Community Resources
- GitHub repository for code and issues
- Community discussions and tips
- Educational resources and tutorials

### Professional Support
- Priority support for commercial users
- Custom development services
- Training and consultation available

---

**Remember**: This bot is a tool to assist with trading execution. Always conduct your own research and consider your financial situation before making trading decisions.
