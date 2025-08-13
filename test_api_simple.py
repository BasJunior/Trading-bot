#!/usr/bin/env python3
"""
Simple test to verify DerivAPI functionality
Tests the fixed recursion issue and basic API operations
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import DerivAPI
from config import Config

async def test_deriv_api():
    """Test basic DerivAPI functionality"""
    print("🧪 Testing DerivAPI class...")
    
    try:
        # Initialize API
        print("📡 Initializing DerivAPI...")
        api = DerivAPI(Config.DERIV_APP_ID, Config.DERIV_API_TOKEN)
        print(f"✅ API initialized with app_id: {api.app_id}")
        
        # Test connection
        print("🔗 Testing connection...")
        connect_result = await api.connect()
        print(f"Connection result: {connect_result}")
        
        if connect_result:
            print("✅ Connected successfully!")
            
            # Test simple request (get active symbols - no auth needed)
            print("📊 Testing active symbols request...")
            symbols_response = await api.get_active_symbols()
            
            if "error" in symbols_response:
                print(f"❌ Symbols request failed: {symbols_response['error']}")
            else:
                symbols = symbols_response.get('active_symbols', [])
                print(f"✅ Got {len(symbols)} active symbols")
                if symbols:
                    print(f"📈 Sample symbols: {[s.get('symbol', 'N/A') for s in symbols[:5]]}")
            
            # Test authorized request (balance - requires auth)
            if api.api_token:
                print("💰 Testing balance request (requires auth)...")
                balance_response = await api.get_balance()
                
                if "error" in balance_response:
                    print(f"❌ Balance request failed: {balance_response['error']}")
                else:
                    balance = balance_response.get('balance', {})
                    print(f"✅ Balance: {balance.get('balance', 'N/A')} {balance.get('currency', 'USD')}")
            else:
                print("⚠️ No API token configured - skipping auth tests")
            
            # Test tick data
            print("📈 Testing tick data for R_100...")
            tick_response = await api.get_ticks("R_100")
            
            if "error" in tick_response:
                print(f"❌ Tick request failed: {tick_response['error']}")
            else:
                tick = tick_response.get('tick', {})
                if tick:
                    print(f"✅ R_100 current price: {tick.get('quote', 'N/A')}")
                else:
                    print("⚠️ No tick data received yet")
            
            # Disconnect
            await api.disconnect()
            print("🔌 Disconnected from API")
            
        else:
            print("❌ Failed to connect to Deriv API")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

async def test_recursion_fix():
    """Test that the recursion issue is fixed"""
    print("\n🔄 Testing recursion fix...")
    
    try:
        # Create API with invalid token to trigger auth failure scenarios
        api = DerivAPI(Config.DERIV_APP_ID, "invalid_token_test")
        
        print("🔗 Attempting connection with invalid token...")
        connect_result = await api.connect()
        
        if not connect_result:
            print("✅ Connection properly failed with invalid token (no recursion)")
        else:
            print("⚠️ Unexpected success with invalid token")
            
        await api.disconnect()
        
    except Exception as e:
        if "maximum recursion depth" in str(e):
            print(f"❌ RECURSION ISSUE STILL EXISTS: {e}")
        else:
            print(f"✅ No recursion - got expected error: {e}")

if __name__ == "__main__":
    print("🚀 Starting DerivAPI Tests...")
    print("=" * 50)
    
    # Run tests
    asyncio.run(test_deriv_api())
    asyncio.run(test_recursion_fix())
    
    print("=" * 50)
    print("✅ Tests completed!")
