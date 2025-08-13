#!/usr/bin/env python3
"""
Test script to validate Deriv App ID and basic API connectivity
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

class DerivAppIdTester:
    """Test Deriv App ID and basic API functionality"""
    
    def __init__(self):
        self.config = Config()
        self.api_url = f"wss://ws.binaryws.com/websockets/v3?app_id={self.config.DERIV_APP_ID}"
        
    async def test_basic_connection(self):
        """Test basic WebSocket connection without authentication"""
        try:
            print("🔗 Testing basic WebSocket connection...")
            async with websockets.connect(self.api_url) as websocket:
                print("✅ WebSocket connection established")
                return True
        except Exception as e:
            print(f"❌ WebSocket connection failed: {e}")
            return False
    
    async def test_ping_pong(self):
        """Test ping/pong functionality"""
        try:
            print(f"🏓 Testing ping/pong with App ID: {self.config.DERIV_APP_ID}")
            
            async with websockets.connect(self.api_url) as websocket:
                # Send ping request
                ping_request = {
                    "ping": 1,
                    "req_id": 1
                }
                await websocket.send(json.dumps(ping_request))
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                response_data = json.loads(response)
                
                if "ping" in response_data and response_data["ping"] == "pong":
                    print("✅ Ping/pong successful - API is responsive")
                    return True
                else:
                    print(f"❌ Unexpected ping response: {response_data}")
                    return False
                    
        except asyncio.TimeoutError:
            print("❌ Ping test timed out")
            return False
        except Exception as e:
            print(f"❌ Ping test failed: {e}")
            return False
    
    async def test_server_time(self):
        """Test server time retrieval"""
        try:
            print("🕐 Testing server time retrieval...")
            
            async with websockets.connect(self.api_url) as websocket:
                # Request server time
                time_request = {
                    "time": 1,
                    "req_id": 2
                }
                await websocket.send(json.dumps(time_request))
                
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                response_data = json.loads(response)
                
                if "time" in response_data:
                    server_time = response_data["time"]
                    print(f"✅ Server time retrieved: {server_time}")
                    return True
                else:
                    print(f"❌ Server time test failed: {response_data}")
                    return False
                    
        except asyncio.TimeoutError:
            print("❌ Server time test timed out")
            return False
        except Exception as e:
            print(f"❌ Server time test failed: {e}")
            return False
    
    async def test_active_symbols(self):
        """Test active symbols retrieval (doesn't require authentication)"""
        try:
            print("📊 Testing active symbols retrieval...")
            
            async with websockets.connect(self.api_url) as websocket:
                # Request active symbols
                symbols_request = {
                    "active_symbols": "brief",
                    "product_type": "basic",
                    "req_id": 3
                }
                await websocket.send(json.dumps(symbols_request))
                
                response = await asyncio.wait_for(websocket.recv(), timeout=15)
                response_data = json.loads(response)
                
                if "active_symbols" in response_data:
                    symbols = response_data["active_symbols"]
                    print(f"✅ Active symbols retrieved: {len(symbols)} symbols available")
                    
                    # Show a few examples
                    if symbols:
                        print("   Sample symbols:")
                        for i, symbol in enumerate(symbols[:5]):
                            print(f"   - {symbol.get('symbol', 'Unknown')}: {symbol.get('display_name', 'Unknown')}")
                    
                    return True
                else:
                    print(f"❌ Active symbols test failed: {response_data}")
                    return False
                    
        except asyncio.TimeoutError:
            print("❌ Active symbols test timed out")
            return False
        except Exception as e:
            print(f"❌ Active symbols test failed: {e}")
            return False
    
    async def test_app_id_validation(self):
        """Test App ID validation by trying to get website status"""
        try:
            print(f"🔍 Testing App ID validation: {self.config.DERIV_APP_ID}")
            
            async with websockets.connect(self.api_url) as websocket:
                # Request website status
                status_request = {
                    "website_status": 1,
                    "req_id": 4
                }
                await websocket.send(json.dumps(status_request))
                
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                response_data = json.loads(response)
                
                if "website_status" in response_data:
                    status = response_data["website_status"]
                    print(f"✅ App ID is valid - Website status: {status.get('site_status', 'Unknown')}")
                    return True
                elif "error" in response_data:
                    error = response_data["error"]
                    print(f"❌ App ID validation failed: {error.get('message', 'Unknown error')}")
                    return False
                else:
                    print(f"❌ Unexpected response: {response_data}")
                    return False
                    
        except asyncio.TimeoutError:
            print("❌ App ID validation timed out")
            return False
        except Exception as e:
            print(f"❌ App ID validation failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all App ID and basic connectivity tests"""
        print("🧪 Starting Deriv App ID Tests")
        print("=" * 50)
        
        tests = [
            ("Basic Connection", self.test_basic_connection),
            ("Ping/Pong", self.test_ping_pong),
            ("Server Time", self.test_server_time),
            ("App ID Validation", self.test_app_id_validation),
            ("Active Symbols", self.test_active_symbols)
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
            print("\n🎉 All tests passed! Your Deriv App ID configuration is working correctly.")
            return True
        else:
            print("\n⚠️  Some tests failed. Please check your configuration.")
            return False

def check_environment():
    """Check if required environment variables are set"""
    print("🔧 Checking environment configuration...")
    
    required_vars = ['DERIV_APP_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\n💡 Please ensure your .env file contains:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        return False
    
    print(f"✅ Environment variables are set")
    print(f"   DERIV_APP_ID: {os.getenv('DERIV_APP_ID')}")
    return True

def main():
    """Main function"""
    try:
        # Check environment first
        if not check_environment():
            sys.exit(1)
        
        # Validate configuration
        Config.validate()
        
        # Run tests
        tester = DerivAppIdTester()
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
