# 🚀 Trading Strategies Guide

This guide explains the automated trading strategies available in the Deriv Telegram Bot.

## 🎯 Overview

The bot supports automated trading strategies that can analyze market data and place trades automatically based on technical indicators. All strategies use advanced technical analysis and can be customized for different markets and lot sizes.

## 📊 Available Strategies

### 1. 🎯 Scalping Strategy (EMA + RSI)
- **Best for**: Quick profits on volatility
- **Method**: Exponential Moving Average + Relative Strength Index
- **Recommended duration**: 5 ticks
- **Suitable markets**: R_75, R_100, R_50, BOOM500, BOOM1000
- **Risk level**: Medium

**How it works:**
- Uses 20-period EMA to identify trend direction
- Uses 14-period RSI to find overbought/oversold conditions
- **BUY CALL**: When price is above EMA and RSI is oversold (< 30)
- **BUY PUT**: When price is below EMA and RSI is overbought (> 70)

**Recommended settings:**
- **Lot size**: $0.1 - $2.0
- **Markets**: R_75, R_100, BOOM500
- **Trading hours**: High volatility periods

### 2. 📈 Swing Trading Strategy (Bollinger Bands + MACD)
- **Best for**: Trend following and momentum trading
- **Method**: Bollinger Bands + MACD crossover
- **Recommended duration**: 10 ticks
- **Suitable markets**: R_75, R_100, R_25, CRASH500, CRASH1000
- **Risk level**: Low to Medium

**How it works:**
- Uses 20-period Bollinger Bands (2 standard deviations)
- Uses MACD (12, 26, 9) for momentum confirmation
- **BUY CALL**: When price hits lower Bollinger Band and MACD is bullish
- **BUY PUT**: When price hits upper Bollinger Band and MACD is bearish

**Recommended settings:**
- **Lot size**: $0.001 - $1.0
- **Markets**: R_75, R_25, CRASH500
- **Trading hours**: Trending market conditions

## 🎮 How to Use Strategies

### Interactive Button Interface:
1. **Start the bot** → Send `/start` to your bot
2. **Auto Trading** → Press the "🤖 Auto Trading" button
3. **Choose Strategy** → Select either "🎯 Start Scalping" or "📈 Start Swing Trading"
4. **Select Market** → Choose from available markets (R_75, R_100, BOOM500, etc.)
5. **Pick Lot Size** → Select from recommended lot sizes
6. **Start Trading** → Your strategy will begin automatically

### Command Interface:
```
/strategy start step_scalping    # Start scalping on R_100
/strategy start v75_swing        # Start swing trading on R_75
/strategy status                 # Check strategy status
/strategy stop                   # Stop all strategies
```

## 📈 Supported Markets

### Volatility Indices:
- **R_75** (Volatility 75 Index) - Recommended for swing trading
- **R_100** (Volatility 100 Index) - Good for both strategies
- **R_50** (Volatility 50 Index) - Lower volatility, good for beginners
- **R_25** (Volatility 25 Index) - Very low volatility, swing trading

### Boom & Crash:
- **BOOM500** - Spike markets, good for scalping
- **BOOM1000** - Higher spike frequency
- **CRASH500** - Drop markets, good for swing trading
- **CRASH1000** - Higher drop frequency

## 🔧 Technical Indicators Explained

### 1. **EMA (Exponential Moving Average)**
- **Purpose**: Identifies trend direction
- **Period**: 20 (default)
- **Signal**: Price above EMA = uptrend, below = downtrend

### 2. **RSI (Relative Strength Index)**
- **Purpose**: Identifies overbought/oversold conditions
- **Period**: 14 (default)
- **Overbought**: > 70 (potential sell signal)
- **Oversold**: < 30 (potential buy signal)

### 3. **Bollinger Bands**
- **Purpose**: Identifies price volatility and potential reversal points
- **Period**: 20 (default)
- **Standard Deviation**: 2
- **Signal**: Price touching bands indicates potential reversal

### 4. **MACD (Moving Average Convergence Divergence)**
- **Purpose**: Momentum indicator
- **Fast EMA**: 12
- **Slow EMA**: 26
- **Signal Line**: 9
- **Bullish**: MACD line above signal line
- **Bearish**: MACD line below signal line

## 💰 Lot Size Recommendations

### Scalping Strategy:
- **Beginner**: $0.1 - $0.5
- **Intermediate**: $0.5 - $1.0
- **Advanced**: $1.0 - $2.0
- **Professional**: $2.0+

### Swing Trading:
- **Beginner**: $0.001 - $0.01
- **Intermediate**: $0.01 - $0.1
- **Advanced**: $0.1 - $0.5
- **Professional**: $0.5+

## ⚠️ Risk Management

### Important Guidelines:
1. **Never risk more than 2% of your account per trade**
2. **Start with small lot sizes** until you understand the strategy
3. **Monitor your strategies regularly**
4. **Use stop-loss mentally** - the bot doesn't have built-in stop-loss
5. **Don't run multiple strategies on the same market** simultaneously

### Daily Limits:
- **Maximum daily loss**: Set in config (default: $100)
- **Maximum trades per hour**: 10 (configurable)
- **Maximum position size**: $10 (configurable)

## 📊 Strategy Performance Monitoring

### Available Metrics:
- **Total trades**: Number of trades executed
- **Win rate**: Percentage of profitable trades
- **Total profit/loss**: Overall P&L
- **Average profit per trade**: Profit divided by number of trades
- **Strategy status**: Active/stopped

### How to Monitor:
1. **Real-time**: Use "📊 Strategy Status" button
2. **Command**: `/strategy status`
3. **Refresh**: Status updates every 5 seconds

## 🛠️ Troubleshooting

### Common Issues:

#### Strategy Not Starting:
- **Check account connection**: Ensure you're connected with `/connect`
- **Verify balance**: Make sure you have sufficient funds
- **Check market status**: Some markets may be closed

#### No Trades Being Placed:
- **Market conditions**: Strategy may be waiting for proper signals
- **Lot size**: Ensure lot size is appropriate for your balance
- **Indicators**: Need minimum data points (usually 20-30 ticks)

#### Poor Performance:
- **Market selection**: Some strategies work better on specific markets
- **Lot size**: Adjust lot size based on risk tolerance
- **Market conditions**: Strategies perform differently in trending vs ranging markets

### Getting Help:
- **Strategy Status**: Shows current strategy state
- **Error Messages**: Check bot responses for error details
- **Restart Strategy**: Stop and restart if issues persist

## 🎯 Best Practices

### For Scalping:
1. **Use during high volatility** periods
2. **Monitor closely** - scalping requires active management
3. **Quick decisions** - be ready to stop if not performing
4. **Smaller lot sizes** - more trades, smaller risk per trade

### For Swing Trading:
1. **Use during trending markets**
2. **Longer timeframes** - let the strategy work
3. **Larger lot sizes** - fewer trades, higher profit potential
4. **Patience** - swing trading requires patience

### General Tips:
1. **Start small** - always test with minimum lot sizes first
2. **One strategy at a time** - don't run multiple strategies simultaneously
3. **Regular monitoring** - check performance at least once per hour
4. **Risk management** - never risk more than you can afford to lose
5. **Market awareness** - understand the markets you're trading

## 📱 Strategy Commands Quick Reference

### Starting Strategies:
```
🤖 Auto Trading → 🎯 Start Scalping → Select Market → Choose Lot Size
🤖 Auto Trading → 📈 Start Swing Trading → Select Market → Choose Lot Size
```

### Monitoring:
```
📊 Strategy Status (button)
/strategy status (command)
```

### Stopping:
```
🛑 Stop All Strategies (button)
/strategy stop (command)
```

### Account Management:
```
📊 Balance → Check current balance
📋 Portfolio → View open positions
```

## 🚀 Advanced Features

### Custom Strategy Parameters:
- **Market Selection**: Choose from 8+ supported markets
- **Lot Size Customization**: From $0.001 to $10+
- **Real-time Monitoring**: Live updates every 5 seconds
- **Multi-strategy Support**: Run different strategies on different markets

### Technical Analysis:
- **Real-time Calculations**: All indicators calculated live
- **Historical Data**: Maintains price history for accurate signals
- **Signal Validation**: Multiple confirmations before trade placement

### User Management:
- **Session Tracking**: Maintains user trading history
- **Performance Statistics**: Win rate, profit/loss, trade count
- **Multi-account Support**: Each user has independent strategies

## 📚 Educational Resources

### Understanding Markets:
- **Volatility Indices**: Simulated markets with controlled volatility
- **Boom/Crash**: Spike markets with sudden price movements
- **Market Hours**: Most synthetic markets trade 24/7

### Technical Analysis Basics:
- **Trend Following**: EMA helps identify market direction
- **Momentum Trading**: RSI and MACD show market strength
- **Mean Reversion**: Bollinger Bands show price extremes

### Risk Management:
- **Position Sizing**: Never risk more than 2% per trade
- **Diversification**: Don't put all funds in one strategy
- **Stop Loss**: Manual monitoring and stopping when necessary

## 🎉 Getting Started Checklist

### Before You Start:
- [ ] ✅ Bot is running and responsive
- [ ] ✅ Account connected with `/connect`
- [ ] ✅ Sufficient balance for trading
- [ ] ✅ Understand the strategy you want to use
- [ ] ✅ Chosen appropriate lot size
- [ ] ✅ Selected suitable market

### Your First Strategy:
1. **Start small**: Use minimum lot size
2. **Choose familiar market**: R_100 is good for beginners
3. **Pick one strategy**: Either scalping or swing trading
4. **Monitor closely**: Watch for first 30 minutes
5. **Evaluate performance**: Check win rate and profit

### Scaling Up:
1. **Consistent profitability**: Only increase lot size after consistent wins
2. **Diversify markets**: Try different markets once comfortable
3. **Multiple strategies**: Run different strategies on different markets
4. **Advanced features**: Explore custom parameters and advanced monitoring

---

## 🔧 Support

If you encounter any issues or need help:
1. **Check Strategy Status**: Use the status button/command
2. **Restart Strategy**: Stop and start again if needed
3. **Review Settings**: Ensure proper configuration
4. **Monitor Performance**: Check if market conditions are suitable

**Happy Trading!** 🚀💰

Remember: **Trading involves risk. Never trade with money you cannot afford to lose.**
