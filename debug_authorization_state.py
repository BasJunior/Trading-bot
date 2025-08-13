#!/usr/bin/env python3
"""
Authorization Debug Tool - Part of Comprehensive Test Suite
Quick debugging for authorization issues
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_test_suite import ConnectionTests

async def debug_authorization():
    """Quick authorization debugging"""
    print("🔍 Authorization Debug Tool")
    print("=" * 40)
    
    print("\n1. Testing Demo Account Authorization:")
    demo_result = await ConnectionTests.test_demo_connection()
    
    print("\n2. Testing Invalid Token Rejection:")
    token_result = await ConnectionTests.test_invalid_token()
    
    print("\n" + "=" * 40)
    print("🎯 Debug Summary:")
    print(f"   Demo Account: {'✅ OK' if demo_result else '❌ ISSUE'}")
    print(f"   Token Validation: {'✅ OK' if token_result else '❌ ISSUE'}")
    
    if demo_result and token_result:
        print("\n✅ Authorization working correctly!")
        print("💡 Users need valid API tokens for account access")
    else:
        print("\n⚠️ Authorization issues detected")
        print("💡 Run full test suite for detailed analysis")


if __name__ == "__main__":
    asyncio.run(debug_authorization())
