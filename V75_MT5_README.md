# V75 Expert Advisor for MetaTrader 5

This is the MQL5 version of the V75 Expert Advisor that can be deployed in MetaEditor and run on MetaTrader 5 terminal.

## Features

The MQL5 EA implements the same trading strategies as the Python version:

### Trading Strategies
1. **EMA Crossover Strategy** - Trend following using fast/slow EMA crossovers
2. **RSI Reversal Strategy** - Mean reversion on RSI oversold/overbought exits  
3. **Bollinger Band Breakout Strategy** - Volatility breakout with momentum confirmation
4. **MACD Momentum Strategy** - Momentum trading using MACD crossovers
5. **Combined Strategy** - Multi-indicator confirmation (requires 2+ agreeing signals)

### Risk Management
- Configurable stop loss and take profit (in pips)
- Trailing stop functionality
- Maximum daily loss limit (default 5%)
- Maximum drawdown protection (default 10%)
- Maximum concurrent trades limit (default 3)
- Rate limiting (max trades per hour)
- Cooldown period after losses

## Installation Instructions

### Step 1: Copy the EA File

1. Locate the file: `V75_Expert_Advisor.mq5`
2. Copy it to your MetaTrader 5 data folder:
   - Windows: `C:\Users\[YourUsername]\AppData\Roaming\MetaQuotes\Terminal\[BrokerID]\MQL5\Experts\`
   - Or open MT5 → File → Open Data Folder → MQL5 → Experts
3. Paste the `V75_Expert_Advisor.mq5` file there

### Step 2: Compile in MetaEditor

1. Open MetaEditor (Press F4 in MT5 or Tools → MetaQuotes Language Editor)
2. Navigate to File → Open → Browse to the `V75_Expert_Advisor.mq5` file
3. Click "Compile" button (F7) or Tools → Compile
4. Check for any errors in the "Toolbox" window at the bottom
5. If compilation is successful, you'll see "0 error(s), 0 warning(s)"

### Step 3: Deploy on Chart

1. In MT5, open a chart for your V75 symbol (e.g., Volatility 75 Index)
2. In the Navigator window (Ctrl+N), expand "Expert Advisors"
3. Find "V75_Expert_Advisor" in the list
4. Drag and drop it onto the V75 chart
5. Enable "Allow automated trading" checkbox in the EA properties
6. Click OK

### Step 4: Enable Automated Trading

1. In MT5, click the "AutoTrading" button in the toolbar (or press Ctrl+E)
2. The button should turn green, indicating automated trading is enabled
3. You should see a smiley face icon in the top-right corner of the chart

## Configuration Parameters

### Core Trading Parameters
- **Lot Size** (0.01): Trade volume per position
- **Min Lot Size** (0.01): Minimum allowed lot size
- **Max Lot Size** (10.0): Maximum allowed lot size

### Risk Management
- **Stop Loss Pips** (50.0): Stop loss distance in pips
- **Take Profit Pips** (100.0): Take profit distance in pips
- **Risk Per Trade** (2.0): Risk percentage per trade
- **Max Daily Loss** (5.0): Maximum daily loss percentage
- **Max Drawdown** (10.0): Maximum drawdown percentage before stopping
- **Trailing Stop Pips** (30.0): Trailing stop distance in pips
- **Enable Trailing Stop** (true): Enable/disable trailing stop

### Position Management
- **Max Open Trades** (3): Maximum concurrent positions
- **Max Trades Per Hour** (10): Rate limit for trades
- **Cooldown After Loss** (60): Seconds to wait after a loss

### Strategy Parameters

**EMA Strategy:**
- **EMA Fast Period** (9): Fast EMA period
- **EMA Slow Period** (21): Slow EMA period

**RSI Strategy:**
- **RSI Period** (14): RSI calculation period
- **RSI Overbought** (70.0): Overbought threshold
- **RSI Oversold** (30.0): Oversold threshold

**Bollinger Bands:**
- **BB Period** (20): Bollinger Bands period
- **BB Deviation** (2.0): Standard deviation multiplier

**MACD Strategy:**
- **MACD Fast** (12): MACD fast EMA period
- **MACD Slow** (26): MACD slow EMA period  
- **MACD Signal** (9): MACD signal line period

**V75 Specific:**
- **Volatility Threshold** (0.02): Threshold for volatility detection
- **Breakout Lookback** (20): Candles to look back for breakout
- **Momentum Threshold** (0.5): Minimum momentum strength

### General Settings
- **Magic Number** (75001): Unique identifier for this EA's trades
- **Trade Comment** ("V75_EA"): Comment added to each trade
- **Enable Detailed Log** (false): Enable verbose logging

## Optimizing Parameters

### For Backtesting
1. In MT5, go to View → Strategy Tester (Ctrl+R)
2. Select "V75_Expert_Advisor" as the Expert Advisor
3. Choose your V75 symbol
4. Set the date range for backtesting
5. Click "Start" to run the backtest
6. Review results in the "Results" and "Graph" tabs

### For Optimization
1. Open Strategy Tester
2. Click the "Optimization" tab
3. Select parameters you want to optimize (check the boxes)
4. Set ranges for each parameter (From/To/Step)
5. Choose optimization criterion (e.g., "Balance", "Profit Factor")
6. Click "Start" to begin optimization
7. Review optimized parameters in the "Optimization Results" tab

## Trading on V75

### Recommended Broker Requirements
- Offers Volatility 75 Index (V75) or synthetic indices
- Low spreads on V75
- Allows Expert Advisors
- MT5 trading platform
- ECN or STP execution preferred

### Recommended Settings for V75
```
Lot Size: 0.01 - 0.05 (depending on account size)
Stop Loss: 30-50 pips
Take Profit: 60-100 pips
Max Open Trades: 2-3
Timeframe: M1 or M5 (for best signals)
```

### Risk Management Tips
1. **Start Small**: Begin with minimum lot size (0.01)
2. **Test First**: Run on demo account before live trading
3. **Monitor Daily**: Check daily loss limits regularly
4. **Adjust Parameters**: Optimize for your broker's V75 specifications
5. **Account Size**: Ensure adequate margin for max open trades

## Monitoring the EA

### What to Watch
- **Open Positions**: Number of active trades
- **Daily P&L**: Profit/loss for current day
- **Win Rate**: Percentage of winning trades
- **Drawdown**: Current drawdown percentage

### EA Logs
Check the "Experts" tab in MT5 terminal to see:
- Trade open/close notifications
- Signal detection messages
- Risk limit warnings
- Error messages (if any)

### Performance Metrics
The EA logs performance statistics on deinitialization:
- Total Trades
- Winning/Losing Trades
- Win Rate percentage
- Total Profit/Loss
- Net Profit
- Maximum Drawdown

## Troubleshooting

### Common Issues

**1. EA Not Trading**
- Check if AutoTrading is enabled (green button)
- Verify EA has smiley face icon on chart
- Check "Experts" tab for error messages
- Ensure sufficient account balance and margin

**2. Compilation Errors**
- Make sure you're using MT5 (not MT4)
- Update MetaTrader 5 to latest version
- Check that file is saved as `.mq5` extension

**3. No Trades Opening**
- Check if risk limits are preventing trades (daily loss, drawdown)
- Verify symbol name matches (must be V75 or Volatility 75)
- Check if rate limits are active (max trades per hour)
- Review market conditions (EA uses combined strategy requiring 2+ signals)

**4. Stops Not Working**
- Verify broker allows SL/TP on V75
- Check minimum stop level for your broker
- Increase stop loss distance if needed

## Differences from Python Version

### What's the Same
- All 5 trading strategies (EMA, RSI, Bollinger, MACD, Combined)
- Risk management features
- Configuration parameters
- Trading logic and signal generation

### What's Different
- **Language**: MQL5 instead of Python
- **Platform**: Runs inside MT5 terminal instead of as external bot
- **API**: Uses MT5 trading functions instead of Deriv WebSocket API
- **Symbol**: Uses broker's V75 symbol instead of R_75
- **Execution**: Event-driven (OnTick) instead of polling-based
- **No Telegram**: Does not integrate with Telegram (pure MT5 EA)

## Support and Updates

For issues or questions:
1. Check the Experts tab for error messages
2. Review this README for troubleshooting
3. Test on demo account first
4. Open an issue on GitHub if needed

## Version History

**v1.00** - Initial release
- Ported from Python version
- Implements all 5 trading strategies
- Full risk management suite
- Trailing stop support
- Comprehensive logging

## License

Same as the main Trading Bot project (MIT License)

## Disclaimer

This Expert Advisor is for educational purposes only. Trading involves significant risk. Always:
- Test thoroughly on demo accounts
- Use proper risk management
- Start with small position sizes
- Monitor your trades actively
- Never risk more than you can afford to lose

---

**Happy Trading! 🚀**
