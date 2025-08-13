#!/usr/bin/env python3
"""
How to Buy on Deriv - Complete Trading Guide
"""

# 🎯 COMPLETE GUIDE: How to Buy Contracts on Deriv Using Your Telegram Bot

"""
===============================================================================
� IMPORTANT: WHAT THIS BOT SUPPORTS
===============================================================================

✅ SUPPORTED:
- Digital Options (Rise/Fall) - CALL/PUT contracts
- Fixed payout options (80-95% return)
- Synthetic Indices (R_10, R_25, R_50, R_75, R_100)
- Boom & Crash indices (BOOM500, BOOM1000, CRASH500, CRASH1000)
- Jump indices (JD50, JD75, JD100)
- Forex pairs (frxEURAUD, frxAUDJPY, etc.)
- Cryptocurrency pairs (cryBTCUSD, cryETHUSD)

❌ NOT SUPPORTED:
- CFD Trading (Contract for Difference)
- Multiplier contracts
- Turbo options
- Accumulator options
- Lookback options
- Variable payout options

If you need CFDs or Multipliers, use the main Deriv platform or DTrader app.

===============================================================================
�🚀 HOW TO BUY ON DERIV - TELEGRAM BOT GUIDE
===============================================================================

⚠️  IMPORTANT: CONTRACT TYPES SUPPORTED ⚠️

Your Deriv Telegram Bot currently supports:
• 📊 DIGITAL OPTIONS (Rise/Fall) - CALL/PUT contracts only
• 🚫 Does NOT support CFDs or Multipliers
• 🚫 Does NOT support Turbo options or other exotic contracts

===============================================================================
📱 1. GETTING STARTED
===============================================================================

1. Start your bot:
   ./start_bot_simple.sh
   
2. Open Telegram and find your bot
   
3. Send /start to begin

4. Connect your Deriv account:
   /connect
   (Enter your API token when prompted)

===============================================================================
🎲 2. MANUAL TRADING (Primary Method)
===============================================================================

Step 1: Access Manual Trading
- Click "🎲 Manual Trade" from main menu

Step 2: Choose Market Type
Available Markets:
- 📊 Synthetic Indices (R_10, R_25, R_50, R_75, R_100)
- 💥 Boom & Crash (BOOM500, BOOM1000, CRASH500, CRASH1000)
- 🎯 Jump Indices (JD50, JD75, JD100)
- 💱 Forex (frxAUDJPY, frxAUDUSD, frxEURAUD, etc.)
- 🪙 Crypto (cryBTCUSD, cryETHUSD)

Step 3: Trading Process
1. Select symbol (e.g., R_100)
2. Choose contract type:
   - CALL (Higher) - price goes up
   - PUT (Lower) - price goes down
3. Set stake amount ($1-$1000)
4. Set duration (1-60 ticks)
5. Confirm trade

===============================================================================
🤖 3. AUTOMATED STRATEGIES
===============================================================================

The bot offers automated trading strategies:

A) Scalping Strategy:
   - Uses EMA + RSI indicators
   - Quick trades (5-10 ticks)
   - Good for volatile synthetic indices

B) Swing Trading:
   - Uses Bollinger Bands + MACD
   - Longer trades (10-30 ticks)
   - Good for trending markets

To start automated trading:
1. Click "🤖 Auto Strategies"
2. Choose strategy type
3. Set parameters
4. Start strategy

===============================================================================
💡 4. CONTRACT TYPES EXPLAINED (DIGITAL OPTIONS ONLY)
===============================================================================

CALL (Higher) Contract:
- You predict price will GO UP at expiry
- Fixed payout (usually 80-95% profit)
- Example: R_100 at 1000.50 → CALL → price ends at 1001.00 = WIN

PUT (Lower) Contract:
- You predict price will GO DOWN at expiry
- Fixed payout (usually 80-95% profit)
- Example: R_100 at 1000.50 → PUT → price ends at 999.80 = WIN

⚠️  NOT SUPPORTED:
- ❌ CFD trading (leverage trading)
- ❌ Multiplier contracts
- ❌ Accumulator options
- ❌ Turbo options

===============================================================================
⚙️ 5. TRADING PARAMETERS
===============================================================================

Stake Amount:
- Minimum: $1
- Maximum: $1000 (varies by account type)
- This is your stake/investment per trade

Duration:
- Ticks only: 1-60 tick movements
- No time-based duration for digital options
- Shorter duration = faster results

Symbol Examples:
- R_100: Rise/Fall 100 Index (most popular)
- R_50: Rise/Fall 50 Index
- BOOM1000: Boom 1000 Index
- frxEURAUD: Euro vs Australian Dollar

Payout Structure:
- Fixed percentage payout (typically 80-95%)
- Example: $10 stake → Win $18-19 total return
- Lose = lose entire stake amount

===============================================================================
📊 6. USING THE BOT INTERFACE
===============================================================================

Main Menu Options:
🔗 Connect - Link your Deriv account
💰 Balance - Check account balance  
🎲 Manual Trade - Place individual digital option trades
🤖 Auto Strategies - Automated trading strategies
📋 Portfolio - View open positions
📈 Analysis - Market analysis tools

Manual Trading Flow:
1. Main Menu → 🎲 Manual Trade
2. Choose market type (Synthetic/Forex/Crypto)
3. Select specific symbol (e.g., R_100)
4. Choose CALL (Higher) or PUT (Lower)
5. Set stake amount and duration (ticks)
6. Confirm trade

⚠️  Note: This bot only supports Digital Options (Rise/Fall)
For CFDs or Multipliers, you need to use the main Deriv platform.

===============================================================================
🛡️ 7. RISK MANAGEMENT
===============================================================================

Built-in Safety Features:
- Maximum stake limits per trade
- Daily loss limits (configurable)
- Trade frequency limits
- Balance checks before trading

Best Practices for Digital Options:
- Start with small stakes ($1-$5)
- Use longer durations (10+ ticks) for better odds
- Avoid over-trading
- Set daily loss limits
- Don't chase losses
- Focus on high-probability setups

Digital Options Risks:
- All-or-nothing payout structure
- Can lose entire stake on each trade
- High frequency can lead to rapid losses
- Market volatility affects success rates

===============================================================================
📈 8. MONITORING YOUR TRADES
===============================================================================

View Active Positions:
- Click "📋 Portfolio" from main menu
- See all open contracts
- Real-time P&L updates
- Close positions early if needed

Trade History:
- Use /profit command
- View past trade results
- Analyze performance
- Track win rates

===============================================================================
🔍 9. EXAMPLE TRADING SESSION (DIGITAL OPTIONS)
===============================================================================

Example: Buying a CALL (Higher) on R_100

1. Start bot → /start
2. Connect account → /connect
3. Main menu → 🎲 Manual Trade
4. Choose → 📊 Synthetic Indices
5. Select → R_100
6. Choose → CALL (Higher) - predict price up
7. Stake → $10
8. Duration → 15 ticks
9. Confirm → ✅ Trade placed
10. Monitor → 📋 Portfolio

Result after 15 ticks:
- If R_100 price is higher → You win $18-19 total
- If R_100 price is lower → You lose your $10 stake

===============================================================================
💰 10. PAYOUT STRUCTURE (DIGITAL OPTIONS ONLY)
===============================================================================

Digital Options (Rise/Fall):
- Fixed payout percentage (typically 80-95%)
- Payout is predetermined before trade
- Example: $10 stake at 85% payout → Win $18.50 total ($8.50 profit)
- Loss = entire stake lost

Factors affecting payout:
- Market volatility
- Duration selected
- Current market conditions
- Account type and tier

⚠️  IMPORTANT LIMITATIONS:
- No CFD trading (no leverage, no variable P&L)
- No Multiplier contracts (no multiplier effect)
- No partial profits - it's all or nothing
- Cannot close positions early in most cases

===============================================================================
🆘 11. TROUBLESHOOTING
===============================================================================

Common Issues:

"❌ No API token configured":
- Solution: Use /connect command to add your token

"❌ Failed to authorize":
- Check your API token is valid
- Ensure account has trading permissions
- Verify account is not restricted

"❌ Insufficient balance":
- Add funds to your Deriv account
- Reduce stake amount

"❌ Market closed":
- Synthetic indices trade 24/7
- Forex has specific hours
- Try different symbol

"❌ Invalid contract type":
- Bot only supports CALL/PUT digital options
- Use main Deriv platform for CFDs/Multipliers

===============================================================================
🎓 12. LEARNING RESOURCES
===============================================================================

Practice Mode:
- Use demo account first
- No real money risk
- Learn the interface

Market Analysis:
- Check built-in indicators
- Use /analysis command
- Monitor market trends

Strategy Testing:
- Start with small amounts
- Test different timeframes
- Compare manual vs auto trading

===============================================================================
📞 13. GETTING HELP
===============================================================================

Bot Commands:
/help - Show all commands
/status - Check connection status
/balance - Check account balance
/connect - Connect/reconnect account

If you encounter issues:
1. Check bot logs
2. Restart bot
3. Verify API token
4. Check Deriv account status

===============================================================================
✅ QUICK START CHECKLIST
===============================================================================

□ Bot is running
□ Telegram bot started (/start)
□ Deriv account connected (/connect)
□ Account balance checked (💰 Balance)
□ First manual trade placed (🎲 Manual Trade)
□ Portfolio monitored (📋 Portfolio)

===============================================================================

Remember: 
- Trading involves risk
- Start small and learn
- Use proper risk management
- The bot is a tool - final decisions are yours

Happy Trading! 🚀
"""

if __name__ == "__main__":
    print("📖 Deriv Trading Guide")
    print("This guide explains how to buy contracts using your Telegram bot.")
    print("Please read the complete guide above for detailed instructions.")
