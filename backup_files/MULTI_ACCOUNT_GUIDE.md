# 👥 Multi-Account Management Guide

This guide explains how to manage multiple Deriv accounts with the Telegram Bot, including setup, configuration, and best practices.

## 📋 Overview

The Deriv Telegram Bot supports managing multiple trading accounts, allowing you to:
- Trade on different Deriv accounts
- Separate strategies by account
- Manage risk across accounts
- Monitor multiple portfolios
- Switch between accounts easily

## 🏗️ Architecture

### Account Structure
```
Bot Instance
├── Account 1 (Main)
│   ├── API Token 1
│   ├── Trading Strategy A
│   └── Risk Settings A
├── Account 2 (Demo)
│   ├── API Token 2
│   ├── Trading Strategy B
│   └── Risk Settings B
└── Account 3 (Backup)
    ├── API Token 3
    ├── Trading Strategy C
    └── Risk Settings C
```

### User Management
- Each Telegram user can have multiple accounts
- Account switching via bot commands
- Session-based account selection
- Persistent account preferences

## 🔧 Setup Methods

### Method 1: Environment Variables (Simple)
```env
# Primary Account
DERIV_API_TOKEN=your_primary_token_here
DERIV_APP_ID=1089

# Secondary Account
DERIV_API_TOKEN_2=your_secondary_token_here
DERIV_APP_ID_2=1089

# Tertiary Account
DERIV_API_TOKEN_3=your_tertiary_token_here
DERIV_APP_ID_3=1089
```

### Method 2: Configuration File (Advanced)
Create `accounts.json`:
```json
{
  "accounts": {
    "main": {
      "name": "Main Trading Account",
      "api_token": "your_main_token",
      "app_id": "1089",
      "default_lot_size": 0.1,
      "max_daily_loss": 100.0,
      "strategies": ["scalping", "swing"]
    },
    "demo": {
      "name": "Demo Account",
      "api_token": "your_demo_token",
      "app_id": "1089",
      "default_lot_size": 0.01,
      "max_daily_loss": 50.0,
      "strategies": ["scalping"]
    },
    "backup": {
      "name": "Backup Account",
      "api_token": "your_backup_token",
      "app_id": "1089",
      "default_lot_size": 0.05,
      "max_daily_loss": 75.0,
      "strategies": ["swing"]
    }
  }
}
```

### Method 3: Interactive Setup
```bash
# Run multi-account setup wizard
python3 setup_tokens.py --multi-account

# Or use the configuration wizard
python3 -c "from user_management import setup_multi_account; setup_multi_account()"
```

## 🎮 Using Multiple Accounts

### Account Selection
The bot provides several ways to select accounts:

**1. Command-based Selection**
```
/account main       # Switch to main account
/account demo       # Switch to demo account
/account backup     # Switch to backup account
/account list       # List all accounts
```

**2. Button Interface**
- Choose "👥 Account Settings"
- Select from available accounts
- View account details
- Switch active account

**3. Quick Switch**
- Long-press on trade buttons
- Select account from popup
- Execute trade on selected account

### Account Information
View account details:
```
/account info main
```

Output example:
```
📊 Account: Main Trading Account
💰 Balance: $1,250.00 USD
📈 P&L Today: +$25.50
🎯 Strategy: Scalping (Active)
⚙️ Lot Size: 0.1
🛡️ Risk Limit: $100.00 (75% remaining)
📊 Trades Today: 15/50
```

## 🔐 Security Considerations

### Token Management
- **Separate tokens**: Each account needs its own API token
- **Limited permissions**: Only grant necessary permissions
- **Regular rotation**: Rotate tokens monthly
- **Secure storage**: Use environment variables or encrypted files

### Access Control
- **User restrictions**: Limit who can access which accounts
- **Account isolation**: Prevent cross-account operations
- **Audit logging**: Track account switches and operations

### Risk Management
- **Individual limits**: Set different risk parameters per account
- **Global limits**: Implement overall portfolio limits
- **Emergency stops**: Quick way to stop all accounts

## 📊 Configuration Examples

### Conservative Multi-Account Setup
```env
# Main account - Conservative strategy
MAIN_API_TOKEN=your_main_token
MAIN_DEFAULT_LOT_SIZE=0.1
MAIN_MAX_DAILY_LOSS=50.0
MAIN_MAX_TRADES_PER_HOUR=5
MAIN_STRATEGIES=swing

# Demo account - Testing new strategies
DEMO_API_TOKEN=your_demo_token
DEMO_DEFAULT_LOT_SIZE=0.01
DEMO_MAX_DAILY_LOSS=20.0
DEMO_MAX_TRADES_PER_HOUR=10
DEMO_STRATEGIES=scalping,swing

# Backup account - Emergency trading
BACKUP_API_TOKEN=your_backup_token
BACKUP_DEFAULT_LOT_SIZE=0.05
BACKUP_MAX_DAILY_LOSS=30.0
BACKUP_MAX_TRADES_PER_HOUR=3
BACKUP_STRATEGIES=swing
```

### Aggressive Multi-Account Setup
```env
# High-volume account
HIGH_VOLUME_API_TOKEN=your_hv_token
HIGH_VOLUME_DEFAULT_LOT_SIZE=0.5
HIGH_VOLUME_MAX_DAILY_LOSS=200.0
HIGH_VOLUME_MAX_TRADES_PER_HOUR=20
HIGH_VOLUME_STRATEGIES=scalping

# Swing trading account
SWING_API_TOKEN=your_swing_token
SWING_DEFAULT_LOT_SIZE=0.2
SWING_MAX_DAILY_LOSS=100.0
SWING_MAX_TRADES_PER_HOUR=8
SWING_STRATEGIES=swing

# Experimental account
EXPERIMENTAL_API_TOKEN=your_exp_token
EXPERIMENTAL_DEFAULT_LOT_SIZE=0.01
EXPERIMENTAL_MAX_DAILY_LOSS=25.0
EXPERIMENTAL_MAX_TRADES_PER_HOUR=15
EXPERIMENTAL_STRATEGIES=scalping,swing
```

## 🔄 Account Switching

### Automatic Switching
The bot can automatically switch accounts based on:
- **Time of day**: Different accounts for different sessions
- **Market conditions**: Conservative account during high volatility
- **Performance**: Switch to backup if main account hits limits

### Manual Switching
Users can manually switch accounts:
1. Via bot commands
2. Through button interface
3. Using quick actions

### Session Management
- **Persistent sessions**: Remember last used account
- **User preferences**: Default account per user
- **Context awareness**: Account-specific settings

## 📈 Performance Monitoring

### Individual Account Metrics
```
📊 Account Performance Dashboard

Main Account:
├── Balance: $1,250.00 → $1,275.50 (+2.04%)
├── Trades: 15 (12 wins, 3 losses)
├── Win Rate: 80%
└── Risk Used: 75% of daily limit

Demo Account:
├── Balance: $100.00 → $102.50 (+2.50%)
├── Trades: 8 (6 wins, 2 losses)
├── Win Rate: 75%
└── Risk Used: 40% of daily limit

Backup Account:
├── Balance: $500.00 → $498.00 (-0.40%)
├── Trades: 3 (2 wins, 1 loss)
├── Win Rate: 67%
└── Risk Used: 20% of daily limit
```

### Combined Portfolio View
```
💼 Portfolio Summary

Total Portfolio Value: $1,975.50
Today's P&L: +$27.50 (+1.41%)
Total Trades: 26
Overall Win Rate: 77%
Risk Utilization: 65% average
```

## 🛠️ Advanced Features

### Account Synchronization
- **Strategy sync**: Apply same strategy to multiple accounts
- **Risk sync**: Maintain consistent risk parameters
- **Performance sync**: Compare performance across accounts

### Load Balancing
- **Trade distribution**: Spread trades across accounts
- **Risk distribution**: Avoid concentration in single account
- **Performance balancing**: Favor better-performing accounts

### Automated Management
- **Auto-switching**: Switch based on performance
- **Auto-rebalancing**: Maintain target allocations
- **Auto-scaling**: Adjust lot sizes based on performance

## 🧪 Testing Multi-Account Setup

### Test Script
```bash
# Test all accounts
python3 test_multi_account.py

# Test specific account
python3 test_token.py --account main
python3 test_token.py --account demo
python3 test_token.py --account backup
```

### Validation Checklist
- [ ] All API tokens are valid
- [ ] Account balances are retrievable
- [ ] Risk limits are properly configured
- [ ] Account switching works correctly
- [ ] Performance tracking is functional
- [ ] Security measures are in place

## 🚨 Risk Management

### Per-Account Limits
```python
# Example risk configuration
ACCOUNT_RISK_LIMITS = {
    'main': {
        'max_daily_loss': 100.0,
        'max_position_size': 10.0,
        'max_trades_per_hour': 10,
        'max_concurrent_trades': 3
    },
    'demo': {
        'max_daily_loss': 50.0,
        'max_position_size': 5.0,
        'max_trades_per_hour': 20,
        'max_concurrent_trades': 5
    }
}
```

### Portfolio-Level Limits
```python
# Global portfolio limits
PORTFOLIO_LIMITS = {
    'max_total_daily_loss': 250.0,
    'max_total_exposure': 50.0,
    'max_correlation_risk': 0.7,
    'emergency_stop_threshold': 500.0
}
```

### Circuit Breakers
- **Account-level**: Stop trading if account hits limits
- **Portfolio-level**: Stop all trading if portfolio hits limits
- **Emergency stop**: Manual override to stop all accounts

## 📚 Best Practices

### Setup Best Practices
1. **Start small**: Begin with 2-3 accounts maximum
2. **Test thoroughly**: Validate each account individually
3. **Document everything**: Keep track of account purposes
4. **Regular reviews**: Monitor account performance regularly

### Trading Best Practices
1. **Diversification**: Use different strategies per account
2. **Risk management**: Set appropriate limits per account
3. **Performance tracking**: Monitor individual and combined performance
4. **Regular rebalancing**: Adjust allocations based on performance

### Security Best Practices
1. **Token security**: Keep API tokens secure and separate
2. **Access control**: Limit who can access which accounts
3. **Audit trails**: Log all account operations
4. **Regular updates**: Keep tokens and configurations updated

## 🔧 Troubleshooting

### Common Issues

**1. Account Not Switching**
- Check API token validity
- Verify account configuration
- Test individual account connection

**2. Performance Issues**
- Monitor system resources
- Check network connectivity
- Optimize trading frequency

**3. Synchronization Problems**
- Verify time synchronization
- Check API rate limits
- Monitor connection stability

### Debug Commands
```bash
# Check account status
python3 -c "from user_management import check_all_accounts; check_all_accounts()"

# Test account switching
python3 -c "from user_management import test_account_switch; test_account_switch()"

# Validate configuration
python3 -c "from config import validate_multi_account; validate_multi_account()"
```

## 📞 Support

### Account-Specific Issues
1. Test individual accounts: `python3 test_token.py --account <name>`
2. Check account configuration
3. Verify API token permissions
4. Monitor account activity

### Multi-Account Issues
1. Test overall configuration: `python3 test_multi_account.py`
2. Check account synchronization
3. Monitor performance metrics
4. Review security settings

---

**Multi-Account Setup Complete! 🎉**

You can now manage multiple Deriv accounts seamlessly through the Telegram bot. Use `/account` commands to switch between accounts and monitor your portfolio performance across all accounts.
