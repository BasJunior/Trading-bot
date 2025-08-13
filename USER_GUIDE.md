# 📖 Deriv Telegram Bot - Complete User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Account Setup](#account-setup)
3. [Bot Commands](#bot-commands)
4. [Main Menu Features](#main-menu-features)
5. [Trading Features](#trading-features)
6. [Account Management](#account-management)
7. [Technical Analysis](#technical-analysis)
8. [Risk Management](#risk-management)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## 🚀 Getting Started

### What is the Deriv Telegram Bot?

The Deriv Telegram Bot is an advanced trading assistant that connects to your Deriv account through Telegram. It provides:
- **Real-time market data** and price monitoring
- **Automated trading strategies** with technical analysis
- **Manual trading** capabilities
- **Account management** and portfolio tracking
- **Risk management** tools

### First Steps

1. **Start the bot** by sending `/start` in Telegram
2. **Choose your account type**:
   - **Demo Mode**: Limited functionality, good for testing
   - **Personal Account**: Full functionality with your Deriv API token

---

## 🔐 Account Setup

### Using Demo Mode

When you first start the bot, you'll be in demo mode with limited functionality:
- ✅ View market prices
- ✅ Access trading symbols
- ✅ Test basic features
- ❌ No real account data
- ❌ No real trading

### Connecting Your Deriv Account

For full functionality, connect your personal Deriv account:

#### Step 1: Get Your Deriv API Token
1. Log in to [Deriv.com](https://deriv.com)
2. Go to **Settings** → **API Token**
3. Create a new token with these permissions:
   - ✅ **Read**: Access account information
   - ✅ **Trade**: Place trades
   - ✅ **Trading Information**: View trading data
   - ✅ **Payments**: View transaction history
4. **Copy your token** (keep it secure!)

#### Step 2: Connect to the Bot
1. Send `/connect` command
2. **Paste your API token** when prompted
3. ✅ **Success!** You now have full bot functionality

---

## 🤖 Bot Commands

### Essential Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Launch the bot and show main menu | `/start` |
| `/help` | Show help information | `/help` |
| `/connect <token>` | Connect your Deriv account | `/connect abc123...` |
| `/disconnect` | Disconnect your account | `/disconnect` |

### Trading Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/balance` | Show account balance | `/balance` |
| `/portfolio` | View open positions | `/portfolio` |
| `/symbols` | List available trading symbols | `/symbols` |
| `/price <symbol>` | Get current price | `/price R_50` |
| `/account` | Show account information | `/account` |

### Advanced Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/profit` | View profit/loss table | `/profit` |
| `/users` | Admin command (if authorized) | `/users` |

---

## 📱 Main Menu Features

The bot's main menu provides quick access to all features through interactive buttons:

### 🤖 Auto Trading
Access automated trading strategies:
- **🎯 Start Scalping**: Quick trades using EMA + RSI
- **📈 Start Swing Trading**: Trend following with Bollinger Bands + MACD
- **📊 Strategy Status**: View active strategies
- **🛑 Stop All Strategies**: Emergency stop for all automated trading

### 💰 Balance
- View your current account balance
- See currency and available funds
- Quick balance refresh

### 📈 Live Prices
- Real-time price monitoring
- Subscribe to price updates
- Multiple symbol tracking

### 🎲 Manual Trade
- Place individual trades manually
- Choose contract types (Call/Put)
- Set stake amounts and duration

### 📋 Portfolio
- View all open positions
- Track profit/loss in real-time
- Position management

### 🔗 Connect Account / 👤 Account Info
- **Connect Account**: Link your Deriv API token (if not connected)
- **Account Info**: View account details (if connected)

### ❓ Help
- Access this user guide
- Command reference
- Support information

---

## 💹 Trading Features

### Automated Trading Strategies

#### 🎯 Scalping Strategy
**Best for**: Quick profits on high-volatility markets
**Timeframe**: 1-5 minutes
**Indicators**: EMA (20) + RSI (14)

**How it works**:
1. Monitors price movements using EMA
2. Uses RSI to identify overbought/oversold conditions
3. Places quick trades when conditions align
4. Automatically closes positions for profit/loss

**Settings**:
- **Stake Amount**: $1 - $100 per trade
- **Duration**: 1-5 minutes
- **Risk Level**: Medium-High

#### 📈 Swing Trading Strategy
**Best for**: Trend following and medium-term trades
**Timeframe**: 15 minutes - 4 hours
**Indicators**: Bollinger Bands + MACD

**How it works**:
1. Identifies trends using Bollinger Bands
2. Confirms signals with MACD crossovers
3. Enters positions in trend direction
4. Holds positions longer for bigger profits

**Settings**:
- **Stake Amount**: $5 - $500 per trade
- **Duration**: 15 minutes - 4 hours
- **Risk Level**: Medium

### Manual Trading

#### Placing a Trade
1. Click **🎲 Manual Trade**
2. **Select Symbol**: Choose from available markets (R_50, R_100, etc.)
3. **Choose Direction**:
   - **📈 Call**: Price will go up
   - **📉 Put**: Price will go down
4. **Set Parameters**:
   - **Stake**: Amount to invest ($1 minimum)
   - **Duration**: How long the trade runs (1 minute - 24 hours)
5. **Confirm Trade**: Review and execute

#### Contract Types Available
- **Rise/Fall**: Predict if price goes up or down
- **Higher/Lower**: Price ends higher or lower than entry
- **Touch/No Touch**: Price touches or doesn't touch a barrier
- **Matches/Differs**: Last digit matches or differs

---

## 👤 Account Management

### Account Information
View your account details:
- **Account Type**: Real or Demo
- **Currency**: USD, EUR, etc.
- **Balance**: Available funds
- **Equity**: Total account value
- **Country**: Account registration country

### Transaction History
Track your trading activity:
- **Recent Trades**: Last 10 trades
- **Profit/Loss**: Daily, weekly, monthly P&L
- **Win Rate**: Success percentage
- **Total Volume**: Amount traded

### Multiple Account Support
The bot supports multiple Deriv accounts:
- Switch between accounts easily
- Track performance separately
- Manage different strategies per account

---

## 📊 Technical Analysis

### Available Indicators

#### Moving Averages
- **EMA (Exponential Moving Average)**: Responds quickly to price changes
- **SMA (Simple Moving Average)**: Smooth average over time period

#### Momentum Indicators
- **RSI (Relative Strength Index)**: Measures overbought/oversold conditions
  - RSI > 70: Overbought (consider selling)
  - RSI < 30: Oversold (consider buying)

#### Volatility Indicators
- **Bollinger Bands**: Shows price volatility and potential reversal points
  - Price near upper band: Potentially overbought
  - Price near lower band: Potentially oversold

#### Trend Indicators
- **MACD (Moving Average Convergence Divergence)**: Shows trend changes
  - MACD above signal line: Bullish trend
  - MACD below signal line: Bearish trend

### Reading Market Signals

#### Bullish Signals (Buy/Call)
- ✅ Price above EMA
- ✅ RSI recovering from oversold (< 30)
- ✅ MACD crossing above signal line
- ✅ Price bouncing off lower Bollinger Band

#### Bearish Signals (Sell/Put)
- ❌ Price below EMA
- ❌ RSI falling from overbought (> 70)
- ❌ MACD crossing below signal line
- ❌ Price rejecting upper Bollinger Band

---

## ⚠️ Risk Management

### Built-in Risk Controls

#### Position Sizing
- **Maximum stake per trade**: Configurable limit
- **Daily loss limit**: Stops trading if daily loss exceeds limit
- **Percentage risk**: Never risk more than X% of balance per trade

#### Stop-Loss Protection
- **Automatic stop-loss**: Closes losing positions
- **Trailing stops**: Lock in profits as trade moves favorably
- **Time-based exits**: Close positions after set time

#### Strategy Limits
- **Maximum concurrent trades**: Limit number of open positions
- **Cool-down periods**: Prevent overtrading
- **Win/loss streaks**: Adjust strategy after consecutive wins/losses

### Best Practices

#### For Beginners
1. **Start small**: Use minimum stake amounts
2. **Use demo first**: Test strategies before real money
3. **Learn gradually**: Start with manual trading
4. **Set limits**: Define daily loss limits
5. **Stay informed**: Monitor economic news

#### For Advanced Users
1. **Diversify strategies**: Use multiple approaches
2. **Monitor correlation**: Avoid highly correlated positions
3. **Adjust parameters**: Fine-tune based on market conditions
4. **Review performance**: Regular strategy evaluation
5. **Stay disciplined**: Stick to your trading plan

### Risk Warnings
⚠️ **Important Disclaimers**:
- Trading derivatives involves significant risk
- You may lose more than your initial investment
- Past performance doesn't guarantee future results
- Only trade with money you can afford to lose
- Consider your experience and risk tolerance

---

## 🛠️ Troubleshooting

### Common Issues

#### "Authorization Required" Error
**Problem**: Can't access account information
**Solutions**:
1. Check if you're connected: `/account`
2. Reconnect your account: `/connect <your_token>`
3. Verify token permissions on Deriv.com
4. Ensure token hasn't expired

#### Bot Not Responding
**Problem**: Commands don't work
**Solutions**:
1. Try `/start` to restart the bot
2. Check your internet connection
3. Wait a few minutes and try again
4. Contact support if problem persists

#### Trading Errors
**Problem**: Can't place trades
**Solutions**:
1. Check account balance
2. Verify market is open
3. Ensure symbol is available
4. Check minimum stake requirements

#### Connection Issues
**Problem**: "Failed to connect" messages
**Solutions**:
1. Verify API token is correct
2. Check Deriv account status
3. Ensure trading is enabled on your account
4. Try disconnecting and reconnecting

### Getting Help

#### Contact Information
- **Bot Support**: Send `/help` for assistance
- **Deriv Support**: Visit [Deriv.com/contact](https://deriv.com/contact)
- **API Issues**: Check [Deriv API Documentation](https://developers.deriv.com/)

#### Reporting Bugs
When reporting issues, include:
1. **Error message** (exact text)
2. **Command used** that caused the error
3. **Account type** (demo/real)
4. **Time** the error occurred

---

## ❓ FAQ

### General Questions

**Q: Is the bot free to use?**
A: Yes, the bot is free. You only pay standard trading costs to Deriv.

**Q: Is my API token safe?**
A: Your token is used only to connect to Deriv's API. Never share it with others.

**Q: Can I use multiple accounts?**
A: Yes, you can connect different Deriv accounts using different tokens.

**Q: What markets can I trade?**
A: All markets available on Deriv: Synthetics, Forex, Stocks, Commodities.

### Trading Questions

**Q: What's the minimum deposit?**
A: Minimum trade stake is usually $0.35, but check with Deriv for current limits.

**Q: Can I modify trades after placing them?**
A: Most binary options cannot be modified once placed. Plan carefully.

**Q: How accurate are the strategies?**
A: No strategy guarantees profits. Success rates vary with market conditions.

**Q: Can I run multiple strategies simultaneously?**
A: Yes, but be careful of overexposure and correlation risks.

### Technical Questions

**Q: Why do I need an API token?**
A: The token allows the bot to access your account and place trades on your behalf.

**Q: How often are prices updated?**
A: Real-time updates, typically every second for subscribed symbols.

**Q: Can I customize the strategies?**
A: Currently, strategies have preset parameters, but customization may be added.

**Q: Does the bot work 24/7?**
A: The bot runs continuously, but trading depends on market hours.

### Security Questions

**Q: Can the bot access my funds directly?**
A: No, the bot can only place trades within your account's available balance.

**Q: What permissions does the API token need?**
A: Read, Trade, Trading Information, and Payments permissions are recommended.

**Q: How do I revoke access?**
A: Delete the API token in your Deriv account settings, then use `/disconnect`.

**Q: Is my personal information stored?**
A: The bot only stores your Telegram user ID and trading preferences locally.

---

## 📞 Support and Resources

### Official Resources
- **Deriv Platform**: [deriv.com](https://deriv.com)
- **API Documentation**: [developers.deriv.com](https://developers.deriv.com)
- **Educational Content**: [academy.deriv.com](https://academy.deriv.com)

### Learning Materials
- **Trading Basics**: Start with Deriv Academy
- **Technical Analysis**: Learn about indicators and chart patterns
- **Risk Management**: Understand position sizing and stop-losses
- **Market Analysis**: Follow economic calendars and news

### Emergency Actions
- **Stop All Trading**: Use `🛑 Stop All Strategies` button
- **Disconnect Account**: Send `/disconnect`
- **Contact Support**: Visit Deriv's official support channels

---

## 📝 Changelog and Updates

The bot is regularly updated with new features and improvements. Recent additions include:
- Enhanced connection stability
- Improved error handling
- Better risk management tools
- Additional trading strategies
- Updated user interface

---

**⚠️ Disclaimer**: This bot is for educational and convenience purposes. Trading derivatives carries significant risk. Always trade responsibly and never risk more than you can afford to lose. The bot's performance doesn't guarantee future profits. Please read Deriv's terms and conditions before trading.

**📄 Last Updated**: July 27, 2025
**🤖 Bot Version**: 2.0
**📧 Support**: Contact through `/help` command in the bot

---

*Happy Trading! 🚀📈*
