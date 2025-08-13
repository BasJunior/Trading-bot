#!/usr/bin/env python3
"""
Test script to verify bot functionality by simulating user interaction
"""
import asyncio
import os
from telegram import Bot
from telegram.ext import Application
from dotenv import load_dotenv

async def test_bot_info():
    """Test if we can get bot information"""
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ No TELEGRAM_BOT_TOKEN found in .env file")
        return False
    
    try:
        bot = Bot(token=token)
        bot_info = await bot.get_me()
        print(f"✅ Bot is accessible: @{bot_info.username}")
        print(f"   Bot ID: {bot_info.id}")
        print(f"   Bot Name: {bot_info.first_name}")
        return True
    except Exception as e:
        print(f"❌ Error accessing bot: {e}")
        return False

async def main():
    print("🔍 Testing bot accessibility...")
    success = await test_bot_info()
    
    if success:
        print("\n✅ Bot test completed successfully!")
        print("🤖 You can now test the bot by sending /start in Telegram")
    else:
        print("\n❌ Bot test failed!")

if __name__ == "__main__":
    asyncio.run(main())
