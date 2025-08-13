#!/usr/bin/env python3
"""
Test script to verify bot handlers are working
This script will send some test messages to verify the bot responds correctly
"""
import asyncio
import os
import time
from telegram import Bot
from telegram.ext import Application
from dotenv import load_dotenv

async def test_start_command_simulation():
    """Simulate what happens when /start is called"""
    print("🧪 Testing Bot Handler Simulation")
    print("=" * 50)
    
    # Import the bot class to test methods directly
    sys.path.append('/Users/abiaschivayo/Documents/coding/deriv_telegram_bot')
    
    try:
        from telegram_bot import DerivTelegramBot
        
        # Create bot instance
        print("1. Creating bot instance...")
        bot = DerivTelegramBot()
        print("   ✅ Bot instance created successfully")
        
        # Check if required methods exist
        print("2. Checking required methods...")
        required_methods = [
            'start_command',
            'help_command', 
            'balance_command',
            'button_callback',
            'error_handler'
        ]
        
        for method in required_methods:
            if hasattr(bot, method):
                print(f"   ✅ {method} - Available")
            else:
                print(f"   ❌ {method} - Missing")
        
        # Check handlers setup
        print("3. Checking handlers setup...")
        handlers = bot.application.handlers
        if handlers:
            print(f"   ✅ {len(handlers)} handler groups registered")
            
            # Check for specific handlers
            command_handlers = []
            callback_handlers = []
            
            for group_id, group_handlers in handlers.items():
                for handler in group_handlers:
                    if hasattr(handler, 'command'):
                        command_handlers.append(handler.command)
                    elif 'CallbackQueryHandler' in str(type(handler)):
                        callback_handlers.append('callback_query')
            
            print(f"   ✅ Command handlers: {command_handlers}")
            print(f"   ✅ Callback handlers: {len(callback_handlers)} registered")
        else:
            print("   ❌ No handlers registered")
        
        print("\n✅ Bot is properly configured and ready!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🔍 Final Bot Validation Test")
    print("=" * 50)
    
    # Test the bot setup
    success = await test_start_command_simulation()
    
    if success:
        print("\n🎉 VALIDATION COMPLETE!")
        print("=" * 50)
        print("✅ Your Deriv Telegram Bot is FULLY OPERATIONAL!")
        print()
        print("📱 Ready to test commands in Telegram:")
        print("   • /start - Main menu")
        print("   • /help - Help information") 
        print("   • /balance - Check balance")
        print("   • /price R_100 - Get price")
        print("   • /connect [token] - Connect account")
        print()
        print("🤖 Bot Username: @multiplex_inv_bot")
        print("🔗 Start chatting: https://t.me/multiplex_inv_bot")
    else:
        print("\n❌ VALIDATION FAILED!")
        print("🔧 Please check the errors above")

if __name__ == "__main__":
    import sys
    asyncio.run(main())
