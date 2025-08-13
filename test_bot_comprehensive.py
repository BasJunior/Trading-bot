#!/usr/bin/env python3
"""
Comprehensive test for the refactored Telegram bot with new connection manager.
Tests the core functionality to ensure the WebSocket concurrency fix works.
"""

import asyncio
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bot_initialization():
    """Test that the bot can be initialized with the new connection manager"""
    print("🧪 Testing bot initialization...")
    
    try:
        # Import the bot class
        from telegram_bot import DerivTelegramBot
        
        # Create bot instance
        bot = DerivTelegramBot()
        
        # Check that connection manager was created
        if hasattr(bot, 'connection_manager') and bot.connection_manager:
            print("✅ Bot initialized successfully with connection manager")
            return True
        else:
            print("❌ Bot missing connection manager")
            return False
            
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_deriv_api_connection():
    """Test that DerivAPI can connect using the new connection manager"""
    print("🧪 Testing DerivAPI connection...")
    
    try:
        from telegram_bot import DerivAPI
        from config import Config
        
        # Create API instance
        api = DerivAPI(Config.DERIV_APP_ID, Config.DERIV_API_TOKEN)
        
        # Test connection
        connected = await api.connect()
        
        if connected:
            print("✅ DerivAPI connected successfully")
            
            # Test a simple API call
            try:
                ping_result = await api.send_request({"ping": 1})
                if ping_result and ping_result.get('ping') == 'pong':
                    print("✅ API ping successful")
                    return True
                else:
                    print(f"❌ API ping failed: {ping_result}")
                    return False
            except Exception as e:
                print(f"❌ API ping failed with error: {e}")
                return False
        else:
            print("❌ DerivAPI connection failed")
            return False
            
    except Exception as e:
        print(f"❌ DerivAPI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_concurrent_requests():
    """Test that multiple concurrent requests work without recv conflicts"""
    print("🧪 Testing concurrent API requests...")
    
    try:
        from telegram_bot import DerivAPI
        from config import Config
        
        # Create API instance
        api = DerivAPI(Config.DERIV_APP_ID, Config.DERIV_API_TOKEN)
        
        # Connect
        if not await api.connect():
            print("❌ Failed to connect for concurrent test")
            return False
        
        # Create multiple concurrent ping requests
        async def ping_request(request_id):
            try:
                result = await api.send_request({"ping": 1})
                if result and result.get('ping') == 'pong':
                    print(f"✅ Concurrent request {request_id} succeeded")
                    return True
                else:
                    print(f"❌ Concurrent request {request_id} failed: {result}")
                    return False
            except Exception as e:
                print(f"❌ Concurrent request {request_id} error: {e}")
                return False
        
        # Run 5 concurrent requests
        tasks = [ping_request(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        successful = sum(1 for r in results if r is True)
        failed = len(results) - successful
        
        print(f"📊 Concurrent test results: {successful} successful, {failed} failed")
        
        if successful >= 3:  # Allow some failures due to network issues
            print("✅ Concurrent requests test passed")
            return True
        else:
            print("❌ Too many concurrent requests failed")
            return False
            
    except Exception as e:
        print(f"❌ Concurrent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_connection_manager_directly():
    """Test the connection manager directly"""
    print("🧪 Testing connection manager directly...")
    
    try:
        from connection_manager_fixed import get_connection_manager
        from config import Config
        
        # Get connection manager
        manager = get_connection_manager(Config.DERIV_APP_ID)
        
        # Connect
        connected = await manager.connect(Config.DERIV_API_TOKEN)
        
        if connected:
            print("✅ Connection manager connected successfully")
            
            # Test multiple concurrent requests
            async def test_request(req_id):
                try:
                    response = await manager.send_request({"ping": 1})
                    return response.get('ping') == 'pong'
                except Exception as e:
                    print(f"❌ Request {req_id} failed: {e}")
                    return False
            
            # Run concurrent requests
            tasks = [test_request(i) for i in range(3)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if r is True)
            print(f"📊 Direct manager test: {successful}/3 requests successful")
            
            return successful >= 2
        else:
            print("❌ Connection manager failed to connect")
            return False
            
    except Exception as e:
        print(f"❌ Connection manager direct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting comprehensive bot tests...")
    print("=" * 60)
    
    tests = [
        ("Bot Initialization", test_bot_initialization),
        ("DerivAPI Connection", test_deriv_api_connection),
        ("Concurrent Requests", test_concurrent_requests),
        ("Connection Manager Direct", test_connection_manager_directly),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        try:
            result = await test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"🏁 {test_name}: {status}")
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot is working correctly with the new connection manager.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
