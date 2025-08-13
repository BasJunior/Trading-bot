# API Documentation

## Deriv API Integration

### WebSocket Connection
The bot uses WebSocket connections to the Deriv API for real-time data and trading operations.

**Endpoint**: `wss://ws.derivws.com/websockets/v3`

### Authentication
```python
# Connect user account
await api.authorize(api_token)
```

### Market Data
```python
# Get live prices
response = await api.get_ticks("R_100")

# Subscribe to price stream  
await api.subscribe_to_live_prices("R_100", callback)
```

### Trading Operations
```python
# Place digital option trade
response = await api.buy({
    "buy": "CALL",
    "symbol": "R_100", 
    "amount": 10,
    "duration": 5,
    "duration_unit": "m"
})

# Close position
response = await api.sell(contract_id, price)
```

## Telegram Bot API

### Command Structure
All commands follow the pattern: `/<command> [arguments]`

### Response Format
Responses use Markdown formatting with inline keyboards for user interaction.

### Error Handling
- Graceful error messages
- Retry mechanisms for API failures
- User-friendly error descriptions

## MT5 CFD API

### Connection Setup
```python
# Initialize MT5 trader
trader = MT5CFDTrader(user_id, login, password, server)

# Connect to account
success = await trader.connect()
```

### Trading Operations
```python
# Place CFD trade
result = await place_cfd_trade(
    user_id, symbol, direction, volume, sl, tp
)

# Get positions
positions = get_cfd_positions(user_id)

# Close position
result = await close_cfd_trade(user_id, ticket)
```

## Configuration API

### Environment Variables
See `.env.example` for all available configuration options.

### Runtime Configuration
```python
from src.bot.config import Config

# Access configuration
max_users = Config.MAX_USERS
enable_mt5 = Config.ENABLE_MT5
```
