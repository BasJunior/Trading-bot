#!/usr/bin/env python3
"""
Quick test to verify the bot is responding and the connection manager is working
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from connection_manager_fixed import DerivAPI, get_connection_manager
from config import Config

async def test_connection_manager():
    """Test the fixed connection manager"""
    print("🧪 Testing Fixed Connection Manager")
    
    try:
        # Test connection manager
        print("1. Testing connection manager creation...")
        manager = get_connection_manager(Config.DERIV_APP_ID)
        print("✅ Connection manager created successfully")
        
        # Test connection
        print("2. Testing WebSocket connection...")
        await manager.connect()
        print("✅ Connected to Deriv WebSocket")
        
        # Test API call
        print("3. Testing API call (get_balance)...")
        response = await manager.get_balance()
        print(f"✅ Balance response: {response.get('balance', {}).get('balance', 'N/A')} {response.get('balance', {}).get('currency', 'USD')}")
        
        # Test another API call
        print("4. Testing get_active_symbols...")
        symbols_response = await manager.get_active_symbols()
        symbols_count = len(symbols_response.get('active_symbols', []))
        print(f"✅ Active symbols count: {symbols_count}")
        
        # Test DerivAPI class
        print("5. Testing DerivAPI class...")
        api = DerivAPI(Config.DERIV_APP_ID, Config.DERIV_API_TOKEN)
        await api.connect()
        balance_response = await api.get_balance()
        print(f"✅ DerivAPI balance: {balance_response.get('balance', {}).get('balance', 'N/A')} {balance_response.get('balance', {}).get('currency', 'USD')}")
        
        await api.disconnect()
        await manager.disconnect()
        
        print("🎉 All tests passed! Connection manager is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection_manager())
    exit(0 if success else 1)
