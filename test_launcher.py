#!/usr/bin/env python3
"""
Quick Test Launcher for Deriv Bot
Provides options for running specific test categories or full suite
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_test_suite import (
    ConnectionTests, 
    APITests, 
    BotIntegrationTests, 
    PerformanceTests,
    TestRunner
)


async def run_quick_tests():
    """Run essential tests quickly"""
    print("🚀 Quick Test Suite - Essential Tests Only")
    print("=" * 50)
    
    tests = [
        ("Demo Connection", ConnectionTests.test_demo_connection),
        ("Invalid Token", ConnectionTests.test_invalid_token),
        ("Public Endpoints", APITests.test_public_endpoints),
        ("Authorization Check", APITests.test_authorization_required_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"   ✅ PASS")
            else:
                print(f"   ❌ FAIL")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 Quick Test Results: {passed}/{total} passed")
    return passed == total


async def run_connection_tests():
    """Run only connection tests"""
    print("🔗 Connection Tests Only")
    runner = TestRunner()
    results = await runner.run_test_category("Connection Tests", ConnectionTests)
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\n📊 Connection Test Results: {passed}/{total} passed")


async def run_api_tests():
    """Run only API tests"""
    print("🔌 API Tests Only")
    runner = TestRunner()
    results = await runner.run_test_category("API Tests", APITests)
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\n📊 API Test Results: {passed}/{total} passed")


def show_menu():
    """Show test menu options"""
    print("\n" + "=" * 60)
    print("🧪 Deriv Bot Test Launcher")
    print("=" * 60)
    print("1. Quick Tests (essential tests only)")
    print("2. Full Test Suite (all tests)")
    print("3. Connection Tests only")
    print("4. API Tests only")
    print("5. Integration Tests only")
    print("6. Performance Tests only")
    print("0. Exit")
    print("-" * 60)


async def main():
    """Main menu loop"""
    while True:
        show_menu()
        try:
            choice = input("Select option (0-6): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                await run_quick_tests()
            elif choice == "2":
                runner = TestRunner()
                await runner.run_all_tests()
            elif choice == "3":
                await run_connection_tests()
            elif choice == "4":
                await run_api_tests()
            elif choice == "5":
                runner = TestRunner()
                await runner.run_test_category("Integration Tests", BotIntegrationTests)
            elif choice == "6":
                runner = TestRunner()
                await runner.run_test_category("Performance Tests", PerformanceTests)
            else:
                print("❌ Invalid option. Please choose 0-6.")
        
        except KeyboardInterrupt:
            print("\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if choice != "0":
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
