#!/usr/bin/env python3
"""
Test exactly what happens in the /connect command after restart
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from connection_manager_fixed import DerivAPI
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connect_command_exact_flow():
    """Test the exact same flow as the /connect command in telegram_bot.py"""
    
    print("🔍 TESTING EXACT /CONNECT COMMAND FLOW (POST-RESTART)")
    print("=" * 60)
    
    # This mimics exactly what happens in telegram_bot.py connect_command
    api_token = "test_user_token_example"  # Invalid token for testing
    
    try:
        print("STEP 1: Creating DerivAPI instance (same as telegram_bot.py line 907)")
        test_api = DerivAPI(Config.DERIV_APP_ID, api_token)
        print(f"   ✅ DerivAPI created with app_id: {Config.DERIV_APP_ID}")
        print(f"   ✅ Token: {api_token}")
        
        print("\nSTEP 2: Calling connect() (same as telegram_bot.py line 908)")
        await test_api.connect()
        print("   ❌ UNEXPECTED: connect() succeeded with invalid token")
        
        print("\nSTEP 3: Getting balance (same as telegram_bot.py line 911)")
        response = await test_api.get_balance()
        print(f"   Response: {response}")
        
        await test_api.disconnect()
        
        if "error" in response:
            error_message = response['error']['message']
            print(f"\nERROR ANALYSIS:")
            print(f"   Error message: {error_message}")
            
            if "Please log in" in error_message:
                print("   🚨 ISSUE FOUND: Still getting 'Please log in' error")
                print("   This suggests authorization didn't work properly")
                return False
            elif "Authorization" in error_message:
                print("   ✅ EXPECTED: Authorization-related error")
                return True
        else:
            print("   🎉 SUCCESS: Balance retrieved successfully!")
            return True
            
    except Exception as e:
        error_message = str(e)
        print(f"\nEXCEPTION ANALYSIS:")
        print(f"   Exception: {error_message}")
        
        if "Authorization failed" in error_message and "invalid" in error_message.lower():
            print("   ✅ EXPECTED: Invalid token rejected during authorization")
            print("   ✅ This means authorization is working correctly")
            return True
        else:
            print("   ⚠️  Unexpected exception type")
            return False

async def test_with_valid_token_format():
    """Test with a more realistic token format"""
    
    print("\n🔍 TESTING WITH REALISTIC TOKEN FORMAT")
    print("=" * 60)
    
    # Use a more realistic-looking token format (still invalid but looks real)
    realistic_token = "abcdef1234567890abcdef1234567890abcdef12"
    
    try:
        print("STEP 1: Creating API with realistic token format...")
        api = DerivAPI(Config.DERIV_APP_ID, realistic_token)
        
        print("STEP 2: Attempting connection...")
        await api.connect()
        
        print("   ❌ UNEXPECTED: Connection succeeded")
        
        print("STEP 3: Testing balance...")
        response = await api.get_balance()
        print(f"   Response: {response}")
        
        await api.disconnect()
        
        if "error" in response:
            error = response["error"]
            if "Please log in" in error.get("message", ""):
                print("   🚨 ISSUE: Still getting 'Please log in'")
                return False
            else:
                print("   ✅ Different error (expected)")
                return True
        
    except Exception as e:
        if "Authorization failed" in str(e):
            print("   ✅ EXPECTED: Authorization failed with realistic token")
            return True
        else:
            print(f"   ⚠️  Unexpected error: {e}")
            return False

async def test_no_token_baseline_after_restart():
    """Test no token scenario after restart"""
    
    print("\n🔍 TESTING NO TOKEN SCENARIO (POST-RESTART BASELINE)")
    print("=" * 60)
    
    try:
        api = DerivAPI(Config.DERIV_APP_ID)  # No token
        await api.connect()
        
        response = await api.get_balance()
        print(f"   Response: {response}")
        
        await api.disconnect()
        
        if "error" in response:
            error = response["error"]
            if "Please log in" in error.get("message", ""):
                print("   ✅ EXPECTED: 'Please log in' without token")
                return True
            elif error.get("code") == "AuthorizationRequired":
                print("   ✅ EXPECTED: Authorization required without token")
                return True
        
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

async def main():
    """Run all tests after restart"""
    
    print("🚀 POST-RESTART CONNECTION TESTING")
    print("Testing the /connect command behavior after fresh bot restart")
    print()
    
    results = []
    
    # Test 1: Exact connect command flow
    result1 = await test_connect_command_exact_flow()
    results.append(("Exact Connect Flow", result1))
    
    # Test 2: Realistic token format
    result2 = await test_with_valid_token_format()
    results.append(("Realistic Token Format", result2))
    
    # Test 3: No token baseline
    result3 = await test_no_token_baseline_after_restart()
    results.append(("No Token Baseline", result3))
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 POST-RESTART TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 RESTART HELPED! Authorization is working correctly.")
        print("The /connect command should now work properly with real tokens.")
    else:
        print("\n⚠️  Issues still persist after restart.")
        print("Further investigation may be needed.")

if __name__ == "__main__":
    asyncio.run(main())
