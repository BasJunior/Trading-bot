#!/bin/bash

# Start Deriv Telegram Bot
echo "🚀 Starting Deriv Telegram Bot..."

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your tokens"
    exit 1
fi

# Check if tokens are configured
if grep -q "your_telegram_bot_token_here" .env; then
    echo "❌ Telegram bot token not configured!"
    echo "Please update TELEGRAM_BOT_TOKEN in .env file"
    exit 1
fi

# Start the bot
echo "Starting bot..."
python3 telegram_bot.py
