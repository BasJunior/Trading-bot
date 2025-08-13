#!/usr/bin/env python3
"""
Fresh test script for the bot - bypassing any caching issues
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Import and test
print("Testing fresh bot import...")

from telegram_bot import DerivTelegramBot

print("Creating bot instance...")
bot = DerivTelegramBot()

print("Checking attributes:")
for attr in ['user_accounts', 'user_sessions', 'default_deriv_api', 'strategy_manager']:
    has_attr = hasattr(bot, attr)
    print(f"  {attr}: {has_attr}")
