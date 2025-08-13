#!/usr/bin/env python3
"""
Quick test for the fixed connection manager
"""
import asyncio
import logging
from connection_manager_fixed import get_connection_manager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def quick_test():
    """Quick test of the fixed connection manager"""
    print("🔧 Quick test of FIXED Connection Manager...")
    
    # Get connection manager
    manager = get_connection_manager("1089")
    
    try:
        # Test connection
        print("🔗 Connecting...")
        connected = await asyncio.wait_for(manager.connect(), timeout=30)
        
        if not connected:
            print("❌ Failed to connect")
            return
            
        print("✅ Connected successfully!")
        
        # Test single request
        print("📊 Testing active symbols request...")
        response = await asyncio.wait_for(
            manager.send_request({"active_symbols": "brief", "product_type": "basic"}),
            timeout=10
        )
        
        if "error" in response:
            print(f"❌ Request failed: {response['error']}")
        else:
            symbols = response.get("active_symbols", [])
            print(f"✅ Got {len(symbols)} active symbols")
            sample_symbols = [s.get("symbol", "unknown") for s in symbols[:5]]
            print(f"📈 Sample symbols: {sample_symbols}")
            
        # Test concurrent requests (this was the main issue)
        print("🔄 Testing 3 concurrent requests...")
        
        tasks = []
        for i in range(3):
            task = asyncio.create_task(
                manager.send_request({"ping": 1})
            )
            tasks.append(task)
            
        # Wait for all requests with timeout
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=15
        )
        
        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Concurrent request {i+1} failed: {result}")
            else:
                success_count += 1
                print(f"✅ Concurrent request {i+1} succeeded")
                
        print(f"📊 {success_count}/{len(tasks)} concurrent requests succeeded")
        
        if success_count == len(tasks):
            print("🎉 CONCURRENCY ISSUE FIXED!")
        else:
            print("⚠️ Some concurrent requests failed")
            
    except asyncio.TimeoutError:
        print("❌ Test timed out")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔌 Disconnecting...")
        try:
            await asyncio.wait_for(manager.disconnect(), timeout=5)
        except asyncio.TimeoutError:
            print("⚠️ Disconnect timed out")
        print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(quick_test())
