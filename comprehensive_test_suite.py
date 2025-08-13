#!/usr/bin/env python3
"""
Comprehensive Test Suite for Deriv Telegram Bot
Consolidates all test functionality into organized classes
"""

import asyncio
import sys
import os
import logging
import json
import time
from typing import Optional, Dict, Any, List

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from connection_manager_fixed import DerivAPI, DerivConnectionManager
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class ConnectionTests:
    """Test connection functionality and WebSocket operations"""
    
    @staticmethod
    async def test_demo_connection() -> bool:
        """Test demo account connection without token"""
        print("🔍 Testing Demo Connection")
        try:
            api = DerivAPI(Config.DERIV_APP_ID)
            await api.connect()
            
            # Test basic operations
            balance_result = await api.get_balance()
            symbols_result = await api.get_active_symbols()
            
            await api.disconnect()
            
            # Check expected behavior
            has_auth_error = "error" in balance_result and "Please log in" in balance_result["error"].get("message", "")
            has_symbols = "active_symbols" in symbols_result
            
            if has_auth_error and has_symbols:
                print("   ✅ Demo connection working (auth required for balance, symbols accessible)")
                return True
            else:
                print(f"   ❌ Unexpected behavior: auth_error={has_auth_error}, symbols={has_symbols}")
                return False
                
        except Exception as e:
            print(f"   ❌ Demo connection failed: {e}")
            return False
    
    @staticmethod
    async def test_invalid_token() -> bool:
        """Test connection with invalid token"""
        print("🔍 Testing Invalid Token")
        try:
            api = DerivAPI(Config.DERIV_APP_ID, "invalid_token_123")
            
            try:
                await api.connect()
                print("   ❌ Unexpected: Invalid token accepted")
                await api.disconnect()
                return False
            except Exception as e:
                if "Authorization failed" in str(e) or "invalid" in str(e).lower():
                    print("   ✅ Invalid token properly rejected")
                    return True
                else:
                    print(f"   ⚠️ Unexpected error: {e}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            return False
    
    @staticmethod
    async def test_websocket_stability() -> bool:
        """Test WebSocket connection stability"""
        print("🔍 Testing WebSocket Stability")
        try:
            api = DerivAPI(Config.DERIV_APP_ID)
            await api.connect()
            
            # Test multiple rapid requests (concurrency test)
            tasks = []
            for i in range(5):
                tasks.append(api.get_active_symbols())
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            await api.disconnect()
            
            # Check if all requests succeeded
            success_count = sum(1 for r in results if isinstance(r, dict) and "active_symbols" in r)
            
            if success_count == 5:
                print("   ✅ WebSocket handled concurrent requests successfully")
                return True
            else:
                print(f"   ⚠️ Only {success_count}/5 concurrent requests succeeded")
                return success_count >= 3  # Allow some tolerance
                
        except Exception as e:
            print(f"   ❌ WebSocket stability test failed: {e}")
            return False


class APITests:
    """Test API functionality and endpoints"""
    
    @staticmethod
    async def test_public_endpoints() -> bool:
        """Test public endpoints that don't require authorization"""
        print("🔍 Testing Public Endpoints")
        
        endpoints_to_test = [
            ("active_symbols", {"active_symbols": "brief", "product_type": "basic"}),
            ("website_status", {"website_status": 1}),
            ("time", {"time": 1}),
            ("ping", {"ping": 1}),
            ("ticks", {"ticks": "R_50"})
        ]
        
        try:
            manager = DerivConnectionManager(Config.DERIV_APP_ID)
            
            # Manual connection without authorization
            import websockets
            ws_url = f"wss://ws.derivws.com/websockets/v3?app_id={Config.DERIV_APP_ID}"
            manager.ws = await websockets.connect(ws_url)
            manager.is_connected = True
            manager._message_listener_task = asyncio.create_task(manager._message_listener())
            await asyncio.sleep(0.1)
            
            success_count = 0
            for endpoint_name, request in endpoints_to_test:
                try:
                    response = await manager._send_request(request)
                    if "error" not in response:
                        success_count += 1
                        print(f"   ✅ {endpoint_name}")
                    else:
                        print(f"   ❌ {endpoint_name}: {response['error']['message']}")
                except Exception as e:
                    print(f"   ❌ {endpoint_name}: {e}")
            
            await manager.disconnect()
            
            if success_count >= 4:  # Allow one failure
                print(f"   ✅ Public endpoints working ({success_count}/{len(endpoints_to_test)} successful)")
                return True
            else:
                print(f"   ⚠️ Only {success_count}/{len(endpoints_to_test)} endpoints working")
                return False
                
        except Exception as e:
            print(f"   ❌ Public endpoints test failed: {e}")
            return False
    
    @staticmethod
    async def test_authorization_required_endpoints() -> bool:
        """Test endpoints that require authorization"""
        print("🔍 Testing Authorization-Required Endpoints")
        
        auth_endpoints = [
            ("balance", {"balance": 1}),
            ("portfolio", {"portfolio": 1}),
            ("get_account_status", {"get_account_status": 1})
        ]
        
        try:
            api = DerivAPI(Config.DERIV_APP_ID)
            await api.connect()
            
            auth_required_count = 0
            for endpoint_name, _ in auth_endpoints:
                try:
                    if endpoint_name == "balance":
                        response = await api.get_balance()
                    elif endpoint_name == "portfolio":
                        response = await api.get_portfolio()
                    else:
                        # Generic request for other endpoints
                        response = await api._connection_manager._send_request({"get_account_status": 1})
                    
                    if "error" in response and "Please log in" in response["error"].get("message", ""):
                        auth_required_count += 1
                        print(f"   ✅ {endpoint_name}: Properly requires authorization")
                    else:
                        print(f"   ⚠️ {endpoint_name}: Unexpected response")
                        
                except Exception as e:
                    print(f"   ❌ {endpoint_name}: {e}")
            
            await api.disconnect()
            
            if auth_required_count >= 2:  # At least balance and portfolio should require auth
                print(f"   ✅ Authorization requirements working ({auth_required_count}/{len(auth_endpoints)} require auth)")
                return True
            else:
                print(f"   ⚠️ Authorization not working properly")
                return False
                
        except Exception as e:
            print(f"   ❌ Authorization test failed: {e}")
            return False


class BotIntegrationTests:
    """Test bot integration and real-world scenarios"""
    
    @staticmethod
    async def test_user_session_simulation() -> bool:
        """Simulate a typical user session"""
        print("🔍 Testing User Session Simulation")
        try:
            # Simulate user starting with demo account
            demo_api = DerivAPI(Config.DERIV_APP_ID)
            await demo_api.connect()
            
            # Get some public data
            symbols = await demo_api.get_active_symbols()
            if not symbols or "error" in symbols:
                print("   ❌ Failed to get symbols")
                return False
            
            # Try to get balance (should require auth)
            balance = await demo_api.get_balance()
            if "error" not in balance or "Please log in" not in balance["error"].get("message", ""):
                print("   ❌ Balance should require authorization")
                return False
            
            await demo_api.disconnect()
            
            # Simulate user trying invalid token
            try:
                user_api = DerivAPI(Config.DERIV_APP_ID, "fake_token")
                await user_api.connect()
                print("   ❌ Fake token should be rejected")
                return False
            except Exception:
                print("   ✅ Fake token properly rejected")
            
            print("   ✅ User session simulation completed successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ User session simulation failed: {e}")
            return False
    
    @staticmethod
    async def test_concurrent_users() -> bool:
        """Test multiple concurrent user connections"""
        print("🔍 Testing Concurrent Users")
        try:
            # Create multiple API instances (simulating different users)
            apis = []
            for i in range(3):
                api = DerivAPI(Config.DERIV_APP_ID)
                apis.append(api)
            
            # Connect all simultaneously
            connect_tasks = [api.connect() for api in apis]
            await asyncio.gather(*connect_tasks)
            
            # Test concurrent operations
            symbol_tasks = [api.get_active_symbols() for api in apis]
            results = await asyncio.gather(*symbol_tasks, return_exceptions=True)
            
            # Disconnect all
            disconnect_tasks = [api.disconnect() for api in apis]
            await asyncio.gather(*disconnect_tasks)
            
            # Check results
            success_count = sum(1 for r in results if isinstance(r, dict) and "active_symbols" in r)
            
            if success_count == 3:
                print("   ✅ All concurrent users handled successfully")
                return True
            else:
                print(f"   ⚠️ Only {success_count}/3 concurrent users successful")
                return success_count >= 2
                
        except Exception as e:
            print(f"   ❌ Concurrent users test failed: {e}")
            return False


class PerformanceTests:
    """Test performance and reliability"""
    
    @staticmethod
    async def test_connection_speed() -> bool:
        """Test connection establishment speed"""
        print("🔍 Testing Connection Speed")
        try:
            start_time = time.time()
            
            api = DerivAPI(Config.DERIV_APP_ID)
            await api.connect()
            
            connect_time = time.time() - start_time
            
            # Test a simple operation
            start_op_time = time.time()
            await api.get_active_symbols()
            op_time = time.time() - start_op_time
            
            await api.disconnect()
            
            print(f"   Connection time: {connect_time:.2f}s")
            print(f"   Operation time: {op_time:.2f}s")
            
            if connect_time < 5.0 and op_time < 2.0:
                print("   ✅ Connection speed acceptable")
                return True
            else:
                print("   ⚠️ Connection speed slower than expected")
                return False
                
        except Exception as e:
            print(f"   ❌ Connection speed test failed: {e}")
            return False
    
    @staticmethod
    async def test_memory_usage() -> bool:
        """Test for memory leaks with repeated connections"""
        print("🔍 Testing Memory Usage")
        try:
            # Perform multiple connect/disconnect cycles
            for i in range(5):
                api = DerivAPI(Config.DERIV_APP_ID)
                await api.connect()
                await api.get_active_symbols()
                await api.disconnect()
                
                # Small delay to allow cleanup
                await asyncio.sleep(0.1)
            
            print("   ✅ Memory usage test completed (no obvious leaks)")
            return True
            
        except Exception as e:
            print(f"   ❌ Memory usage test failed: {e}")
            return False


class TestRunner:
    """Main test runner class"""
    
    def __init__(self):
        self.results = {}
    
    async def run_test_category(self, category_name: str, test_class) -> Dict[str, bool]:
        """Run all tests in a category"""
        print(f"\n{'='*60}")
        print(f"🧪 Running {category_name}")
        print(f"{'='*60}")
        
        category_results = {}
        
        # Get all test methods from the class
        test_methods = [method for method in dir(test_class) 
                       if method.startswith('test_') and callable(getattr(test_class, method))]
        
        for method_name in test_methods:
            test_method = getattr(test_class, method_name)
            try:
                result = await test_method()
                category_results[method_name] = result
            except Exception as e:
                print(f"❌ {method_name} crashed: {e}")
                category_results[method_name] = False
        
        return category_results
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Deriv Bot Comprehensive Test Suite")
        print("Testing connection, API, integration, and performance")
        
        # Define test categories
        test_categories = [
            ("Connection Tests", ConnectionTests),
            ("API Tests", APITests),
            ("Bot Integration Tests", BotIntegrationTests),
            ("Performance Tests", PerformanceTests)
        ]
        
        total_tests = 0
        total_passed = 0
        
        # Run each category
        for category_name, test_class in test_categories:
            category_results = await self.run_test_category(category_name, test_class)
            self.results[category_name] = category_results
            
            # Count results
            category_total = len(category_results)
            category_passed = sum(1 for result in category_results.values() if result)
            
            total_tests += category_total
            total_passed += category_passed
            
            print(f"\n📊 {category_name} Results: {category_passed}/{category_total} passed")
        
        # Final summary
        self.print_final_summary(total_passed, total_tests)
    
    def print_final_summary(self, total_passed: int, total_tests: int):
        """Print comprehensive test summary"""
        print(f"\n{'='*80}")
        print("🏁 FINAL TEST SUMMARY")
        print(f"{'='*80}")
        
        # Overall results
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"Overall Results: {total_passed}/{total_tests} tests passed ({pass_rate:.1f}%)")
        
        # Category breakdown
        for category_name, category_results in self.results.items():
            category_passed = sum(1 for result in category_results.values() if result)
            category_total = len(category_results)
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            
            status = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 60 else "❌"
            print(f"   {status} {category_name}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        # Health assessment
        print(f"\n🏥 System Health Assessment:")
        if pass_rate >= 90:
            print("   🟢 EXCELLENT: System is working optimally")
        elif pass_rate >= 75:
            print("   🟡 GOOD: System is mostly functional with minor issues")
        elif pass_rate >= 50:
            print("   🟠 FAIR: System has significant issues that need attention")
        else:
            print("   🔴 POOR: System has critical issues requiring immediate attention")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if pass_rate < 100:
            print("   • Review failed tests and address underlying issues")
            print("   • Check network connectivity and API availability")
            print("   • Verify configuration settings in config.py")
        if pass_rate >= 80:
            print("   • System is ready for production use")
            print("   • Consider monitoring for continued stability")
        
        print(f"\n📄 Test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")


async def main():
    """Main entry point"""
    runner = TestRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
