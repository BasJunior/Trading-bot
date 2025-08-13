#!/bin/bash

# Simple bot start script
echo "🚀 Starting Deriv Telegram Bot..."
echo "📱 Press Ctrl+C to stop the bot"
echo ""

cd "$(dirname "$0")"
python3 telegram_bot.py
