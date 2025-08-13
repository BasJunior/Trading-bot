#!/usr/bin/env python3
"""
Test script to validate Deriv API token and connection
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv
import websockets
from config import Config

# Load environment variables
load_dotenv()

class DerivTokenTester:
    """Test Deriv API token and connection"""
    
    def __init__(self):
        self.config = Config()
        self.api_url = f"wss://ws.binaryws.com/websockets/v3?app_id={self.config.DERIV_APP_ID}"
        
    async def test_connection(self):
        """Test basic WebSocket connection"""
        try:
            print("🔗 Testing WebSocket connection...")
            async with websockets.connect(self.api_url) as websocket:
                print("✅ WebSocket connection successful")
                return True
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            return False
    
    async def test_app_id(self):
        """Test Deriv App ID"""
        try:
            print(f"🔑 Testing Deriv App ID: {self.config.DERIV_APP_ID}")
            
            async with websockets.connect(self.api_url) as websocket:
                # Send ping request with app_id
                ping_request = {
                    "ping": 1,
                    "req_id": 1
                }
                await websocket.send(json.dumps(ping_request))
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if "ping" in response_data:
                    print("✅ App ID is valid - basic connection working")
                    return True
                else:
                    print(f"❌ Unexpected response: {response_data}")
                    return False
                    
        except Exception as e:
            print(f"❌ App ID test failed: {e}")
            return False
    
    async def test_token(self):
        """Test Deriv API token"""
        if not self.config.DERIV_API_TOKEN:
            print("⚠️  No Deriv API token found in environment")
            return False
            
        try:
            print("🔐 Testing Deriv API token...")
            
            async with websockets.connect(self.api_url) as websocket:
                # Authorize with token
                auth_request = {
                    "authorize": self.config.DERIV_API_TOKEN,
                    "req_id": 2
                }
                await websocket.send(json.dumps(auth_request))
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if "authorize" in response_data:
                    account_info = response_data["authorize"]
                    print(f"✅ Token is valid!")
                    print(f"   Account ID: {account_info.get('loginid', 'Unknown')}")
                    print(f"   Currency: {account_info.get('currency', 'Unknown')}")
                    print(f"   Country: {account_info.get('country', 'Unknown')}")
                    print(f"   Email: {account_info.get('email', 'Unknown')}")
                    return True
                elif "error" in response_data:
                    error = response_data["error"]
                    print(f"❌ Token validation failed: {error.get('message', 'Unknown error')}")
                    return False
                else:
                    print(f"❌ Unexpected response: {response_data}")
                    return False
                    
        except Exception as e:
            print(f"❌ Token test failed: {e}")
            return False
    
    async def test_balance(self):
        """Test getting account balance"""
        if not self.config.DERIV_API_TOKEN:
            print("⚠️  No API token - skipping balance test")
            return False
            
        try:
            print("💰 Testing balance retrieval...")
            
            async with websockets.connect(self.api_url) as websocket:
                # First authorize
                auth_request = {
                    "authorize": self.config.DERIV_API_TOKEN,
                    "req_id": 3
                }
                await websocket.send(json.dumps(auth_request))
                await websocket.recv()  # Skip auth response
                
                # Get balance
                balance_request = {
                    "balance": 1,
                    "subscribe": 1,
                    "req_id": 4
                }
                await websocket.send(json.dumps(balance_request))
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if "balance" in response_data:
                    balance_info = response_data["balance"]
                    print(f"✅ Balance retrieved successfully!")
                    print(f"   Current Balance: {balance_info.get('balance', 'Unknown')} {balance_info.get('currency', '')}")
                    return True
                else:
                    print(f"❌ Balance test failed: {response_data}")
                    return False
                    
        except Exception as e:
            print(f"❌ Balance test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all token and connection tests"""
        print("🧪 Starting Deriv API Token Tests")
        print("=" * 50)
        
        tests = [
            ("Connection Test", self.test_connection),
            ("App ID Test", self.test_app_id),
            ("Token Test", self.test_token),
            ("Balance Test", self.test_balance)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name}...")
            result = await test_func()
            results.append((test_name, result))
            print("-" * 30)
        
        print(f"\n📊 Test Results Summary:")
        print("=" * 50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nTotal: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("\n🎉 All tests passed! Your Deriv API configuration is working correctly.")
            return True
        else:
            print("\n⚠️  Some tests failed. Please check your configuration.")
            return False

def main():
    """Main function"""
    try:
        # Validate configuration
        Config.validate()
        
        # Run tests
        tester = DerivTokenTester()
        success = asyncio.run(tester.run_all_tests())
        
        sys.exit(0 if success else 1)
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n💡 Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
