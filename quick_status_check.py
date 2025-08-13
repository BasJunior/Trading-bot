#!/usr/bin/env python3
"""
Quick status check for the Telegram bot and connection manager
"""
import asyncio
import sys
import os

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from connection_manager import ConnectionManager
from config import Config

async def quick_status_check():
    """Perform a quick status check of the connection manager"""
    print("🔍 Starting quick status check...")
    
    try:
        # Initialize connection manager
        print("📡 Initializing connection manager...")
        conn_manager = ConnectionManager(app_id=Config.DERIV_APP_ID)
        
        # Test basic connection
        print("🔗 Testing basic connection...")
        response = await conn_manager.send_request({
            "ping": 1
        })
        
        if response and response.get("pong") == 1:
            print("✅ Basic connection: WORKING")
        else:
            print("❌ Basic connection: FAILED")
            return False
        
        # Test active symbols
        print("📊 Testing active symbols...")
        symbols_response = await conn_manager.send_request({
            "active_symbols": "brief",
            "product_type": "basic"
        })
        
        if symbols_response and "active_symbols" in symbols_response:
            symbol_count = len(symbols_response["active_symbols"])
            print(f"✅ Active symbols: {symbol_count} symbols available")
        else:
            print("❌ Active symbols: FAILED")
            return False
        
        # Test price streaming (for a short time)
        print("💹 Testing price streaming...")
        stream_started = False
        
        def price_callback(data):
            nonlocal stream_started
            if not stream_started:
                print(f"✅ Price streaming: WORKING (received data for {data.get('symbol', 'unknown')})")
                stream_started = True
        
        # Subscribe to a popular symbol
        await conn_manager.subscribe_to_symbol("R_50", price_callback)
        
        # Wait for a few seconds to receive data
        await asyncio.sleep(3)
        
        if not stream_started:
            print("❌ Price streaming: No data received")
        
        # Unsubscribe
        await conn_manager.unsubscribe_from_symbol("R_50")
        
        # Check connection pool status
        print(f"🏊 Connection pool: {len(conn_manager.connections)} active connections")
        
        print("🎉 Status check completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Status check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            await conn_manager.close_all_connections()
            print("🔌 All connections closed")
        except Exception as e:
            print(f"Warning: Error closing connections: {e}")

if __name__ == "__main__":
    success = asyncio.run(quick_status_check())
    sys.exit(0 if success else 1)
