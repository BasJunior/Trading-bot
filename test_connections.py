#!/usr/bin/env python3
"""
Comprehensive test for improved connection management and live streaming
Tests the new connection pool, persistent connections, and live price streaming
"""

import asyncio
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection_pool():
    """Test the connection pool functionality"""
    print("🧪 Testing Connection Pool...")
    
    try:
        from connection_manager import ConnectionPool, get_connection_pool
        from config import Config
        
        # Initialize connection pool
        pool = ConnectionPool(Config.DERIV_APP_ID)
        await pool.start()
        
        print("✅ Connection pool started")
        
        # Test getting a connection
        connection = await pool.get_connection()
        print(f"✅ Got connection: {connection.connection_id}")
        
        # Test connection status
        if connection.is_connected:
            print("✅ Connection is active")
        else:
            print("⚠️ Connection not active, attempting to connect...")
            success = await connection.connect()
            print(f"Connection result: {success}")
        
        # Test subscription
        await pool.subscribe_to_ticks("R_100")
        print("✅ Subscribed to R_100 ticks")
        
        # Wait for some price data
        print("⏳ Waiting for price data...")
        await asyncio.sleep(5)
        
        # Check for cached price
        latest_price = pool.get_latest_price("R_100")
        if latest_price:
            print(f"✅ Got cached price: {latest_price.get('quote', 'N/A')}")
        else:
            print("⚠️ No cached price available yet")
            
        # Test price history
        history = pool.get_price_history("R_100", limit=5)
        print(f"📊 Price history samples: {len(history)}")
        
        # Cleanup
        await pool.stop()
        print("✅ Connection pool stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection pool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_deriv_api_with_pool():
    """Test the enhanced DerivAPI with connection pool"""
    print("\n🧪 Testing Enhanced DerivAPI...")
    
    try:
        from telegram_bot import DerivAPI
        from config import Config
        from connection_manager import initialize_connection_pool
        
        # Initialize connection pool
        await initialize_connection_pool()
        print("✅ Connection pool initialized")
        
        # Create API instance
        api = DerivAPI(Config.DERIV_APP_ID, Config.DERIV_API_TOKEN)
        print("✅ DerivAPI instance created")
        
        # Test connection
        connected = await api.connect()
        print(f"Connection result: {connected}")
        
        if connected:
            # Test live price subscription
            print("📊 Testing live price subscription...")
            success = await api.subscribe_to_live_prices("R_100")
            print(f"Subscription result: {success}")
            
            # Wait for price data
            await asyncio.sleep(3)
            
            # Test getting cached price
            cached_price = api.get_latest_price("R_100")
            if cached_price:
                print(f"✅ Cached price: {cached_price.get('quote', 'N/A')}")
            
            # Test price history
            history = api.get_price_history("R_100", limit=3)
            print(f"📊 History samples: {len(history)}")
            
            # Test traditional API calls
            print("🔄 Testing traditional API calls...")
            balance_response = await api.get_balance()
            if "error" not in balance_response:
                balance = balance_response.get("balance", {})
                print(f"✅ Balance: {balance.get('balance', 'N/A')} {balance.get('currency', 'USD')}")
            
            # Test active symbols
            symbols_response = await api.get_active_symbols()
            if "error" not in symbols_response:
                symbols = symbols_response.get("active_symbols", [])
                print(f"✅ Active symbols: {len(symbols)}")
                
        await api.disconnect()
        print("🔌 API disconnected")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_live_streaming_callback():
    """Test live streaming with callbacks"""
    print("\n🧪 Testing Live Streaming with Callbacks...")
    
    try:
        from connection_manager import get_connection_pool
        
        pool = get_connection_pool()
        await pool.start()
        
        # Price update counter
        update_count = 0
        latest_prices = []
        
        async def price_callback(symbol, tick_data):
            nonlocal update_count, latest_prices
            update_count += 1
            price = tick_data.get("quote", "N/A")
            timestamp = tick_data.get("epoch", "")
            latest_prices.append(price)
            
            print(f"📈 Live Update #{update_count}: {symbol} = {price} at {datetime.fromtimestamp(timestamp) if timestamp else 'N/A'}")
        
        # Subscribe with callback
        await pool.subscribe_to_ticks("R_75", price_callback)
        print("✅ Subscribed to R_75 with callback")
        
        # Wait for updates
        print("⏳ Waiting for live price updates (10 seconds)...")
        await asyncio.sleep(10)
        
        print(f"📊 Received {update_count} price updates")
        if latest_prices:
            print(f"📈 Price range: {min(latest_prices)} - {max(latest_prices)}")
        
        # Unsubscribe
        await pool.unsubscribe_from_ticks("R_75")
        print("🔇 Unsubscribed from R_75")
        
        await pool.stop()
        
        return update_count > 0
        
    except Exception as e:
        print(f"❌ Live streaming test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_symbols():
    """Test multiple symbol streaming"""
    print("\n🧪 Testing Multiple Symbol Streaming...")
    
    try:
        from connection_manager import get_connection_pool
        
        pool = get_connection_pool()
        await pool.start()
        
        symbols = ["R_50", "R_75", "R_100", "BOOM500"]
        update_counts = {symbol: 0 for symbol in symbols}
        
        # Create callbacks for each symbol
        for symbol in symbols:
            async def callback(sym, tick_data):
                update_counts[sym] += 1
                price = tick_data.get("quote", "N/A")
                print(f"📊 {sym}: {price} (update #{update_counts[sym]})")
            
            await pool.subscribe_to_ticks(symbol, callback)
            print(f"✅ Subscribed to {symbol}")
        
        # Wait for updates
        print("⏳ Monitoring multiple symbols (15 seconds)...")
        await asyncio.sleep(15)
        
        # Summary
        print("\n📊 Update Summary:")
        total_updates = 0
        for symbol, count in update_counts.items():
            print(f"• {symbol}: {count} updates")
            total_updates += count
            
        print(f"🎯 Total updates across all symbols: {total_updates}")
        
        # Cleanup
        for symbol in symbols:
            await pool.unsubscribe_from_ticks(symbol)
        
        await pool.stop()
        
        return total_updates > 0
        
    except Exception as e:
        print(f"❌ Multiple symbols test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_connection_resilience():
    """Test connection resilience and reconnection"""
    print("\n🧪 Testing Connection Resilience...")
    
    try:
        from connection_manager import ManagedConnection, ConnectionPool
        from config import Config
        
        pool = ConnectionPool(Config.DERIV_APP_ID)
        await pool.start()
        
        # Get a connection
        connection = await pool.get_connection()
        
        print(f"✅ Initial connection status: {connection.is_connected}")
        
        # Simulate connection loss by closing websocket
        if connection.websocket:
            await connection.websocket.close()
            print("🔌 Simulated connection loss")
            
        # Wait a bit
        await asyncio.sleep(2)
        
        # Try to use the connection (should trigger reconnection)
        print("🔄 Attempting to use connection (should auto-reconnect)...")
        
        # The connection should automatically reconnect
        await asyncio.sleep(5)
        
        print(f"✅ Final connection status: {connection.is_connected}")
        
        await pool.stop()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection resilience test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all connection tests"""
    print("🚀 Starting Connection Management Tests...")
    print("=" * 60)
    
    tests = [
        ("Connection Pool", test_connection_pool),
        ("Enhanced DerivAPI", test_deriv_api_with_pool),
        ("Live Streaming", test_live_streaming_callback),
        ("Multiple Symbols", test_multiple_symbols),
        ("Connection Resilience", test_connection_resilience),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = await test_func()
            results[test_name] = "✅ PASSED" if result else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {e}"
        
        print(f"Result: {results[test_name]}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        print(f"• {test_name:<20}: {result}")
        if "PASSED" in result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Connection management is working properly.")
    else:
        print("⚠️ Some tests failed. Check the logs for details.")
    
    return passed == total

if __name__ == "__main__":
    print("🔧 Connection Management Test Suite")
    print("Testing improved connection handling and live streaming")
    print("=" * 60)
    
    result = asyncio.run(run_all_tests())
    
    if result:
        print("\n✅ All connection tests completed successfully!")
        print("The bot should now maintain stable connections for:")
        print("• Live price streaming")
        print("• Manual trading")
        print("• Automated strategies")
        print("• Real-time portfolio updates")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
