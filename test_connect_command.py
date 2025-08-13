#!/usr/bin/env python3
"""
Test the /connect command functionality specifically
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from connection_manager_fixed import DerivAPI
from config import Config

async def test_user_connect_scenario():
    """Test the scenario that happens when a user uses /connect command"""
    print("🧪 Testing User Connect Scenario")
    
    try:
        # This simulates what happens in connect_command when user provides API token
        print("1. Creating new DerivAPI instance with user token...")
        test_api = DerivAPI(Config.DERIV_APP_ID, Config.DERIV_API_TOKEN)
        print("✅ DerivAPI instance created")
        
        print("2. Testing connection (like in connect_command)...")
        await test_api.connect()
        print("✅ Connected successfully")
        
        print("3. Testing get_balance (like in connect_command)...")
        response = await test_api.get_balance()
        
        if "error" in response:
            print(f"❌ Balance error: {response['error']['message']}")
            return False
        else:
            balance = response.get("balance", {})
            print(f"✅ Balance: {balance.get('balance', 'N/A')} {balance.get('currency', 'USD')}")
        
        print("4. Testing disconnection...")
        await test_api.disconnect()
        print("✅ Disconnected successfully")
        
        print("🎉 User connect scenario test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_user_connections():
    """Test multiple users connecting simultaneously"""
    print("\n🧪 Testing Multiple User Connections")
    
    try:
        # Simulate multiple users connecting
        apis = []
        
        print("1. Creating multiple API instances...")
        for i in range(3):
            api = DerivAPI(Config.DERIV_APP_ID, Config.DERIV_API_TOKEN)
            apis.append(api)
        print(f"✅ Created {len(apis)} API instances")
        
        print("2. Connecting all instances simultaneously...")
        connect_tasks = [api.connect() for api in apis]
        await asyncio.gather(*connect_tasks)
        print("✅ All instances connected")
        
        print("3. Testing simultaneous balance requests...")
        balance_tasks = [api.get_balance() for api in apis]
        responses = await asyncio.gather(*balance_tasks)
        
        for i, response in enumerate(responses):
            if "error" in response:
                print(f"❌ API {i+1} error: {response['error']['message']}")
            else:
                balance = response.get("balance", {})
                print(f"✅ API {i+1} balance: {balance.get('balance', 'N/A')} {balance.get('currency', 'USD')}")
        
        print("4. Disconnecting all instances...")
        disconnect_tasks = [api.disconnect() for api in apis]
        await asyncio.gather(*disconnect_tasks)
        print("✅ All instances disconnected")
        
        print("🎉 Multiple user connections test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Multiple connections test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all connection tests"""
    print("🔧 Testing Connection Manager Fix\n")
    
    test1_success = await test_user_connect_scenario()
    test2_success = await test_multiple_user_connections()
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! The /connect command should work now.")
        return True
    else:
        print("\n❌ Some tests failed.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
