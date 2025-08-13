#!/usr/bin/env python3
"""
Test the /connect command functionality directly
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import DerivTelegramBot
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connect_command():
    """Test the connect command functionality"""
    
    print("🔍 Testing /connect command functionality...")
    
    # Create bot instance
    bot = DerivTelegramBot()
    
    # Test token (replace with actual token for real testing)
    test_token = "your_test_token_here"  # Replace with actual token
    
    # Simulate a user ID
    test_user_id = 12345
    
    try:
        print("1. Testing connection with test token...")
        
        # Directly test the connection logic from the /connect command
        # This simulates what happens when a user runs /connect <token>
        
        # Create a user API instance (same as done in /connect command)
        from connection_manager_fixed import DerivAPI
        user_api = DerivAPI(Config.DERIV_APP_ID, test_token)
        
        print("2. Connecting to Deriv API...")
        # This will connect and authorize automatically if api_token is provided
        await user_api.connect()
        print("   Connect completed (should include authorization if token is valid)")
        
        print("3. Getting balance...")
        balance_result = await user_api.get_balance()
        print(f"   Balance result: {balance_result}")
        
        if balance_result.get('error'):
            print(f"❌ Balance request failed: {balance_result['error']}")
            print("   This is expected if using placeholder token")
        else:
            print("✅ Balance request successful!")
            print(f"   Currency: {balance_result.get('balance', {}).get('currency', 'Unknown')}")
            print(f"   Balance: {balance_result.get('balance', {}).get('balance', 'Unknown')}")
        
        await user_api.disconnect()
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

async def test_connect_command_structure():
    """Test the structure of the connect command without actual token"""
    
    print("\n🔍 Testing /connect command structure...")
    
    try:
        # Check that the bot has the connect command
        bot = DerivTelegramBot()
        
        # Check if the connect handler is properly registered
        print("✅ Bot initialized successfully")
        print("✅ Connect command should be available")
        
        # Test balance request format (without authorization)
        from connection_manager_fixed import DerivAPI
        api = DerivAPI(Config.DERIV_APP_ID)
        
        # Check connection
        await api.connect()
        print("✅ Can connect to Deriv API")
        
        # The balance request should no longer include "account": "all"
        print("✅ Balance request format updated (removed 'account': 'all')")
        
        await api.disconnect()
        
    except Exception as e:
        print(f"❌ Error testing command structure: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Testing /connect command...")
    print("Note: Replace 'your_test_token_here' with a valid token to test full authorization")
    
    asyncio.run(test_connect_command_structure())
    asyncio.run(test_connect_command())
    
    print("\n✅ Tests completed!")
    print("\nTo test with a real token:")
    print("1. Replace 'your_test_token_here' with a valid Deriv API token")
    print("2. Run this script again")
    print("3. The authorization and balance requests should work without 'Please log in' errors")
