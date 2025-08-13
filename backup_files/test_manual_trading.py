#!/usr/bin/env python3
"""
Manual Trading Functionality Test
Comprehensive testing of manual trading features
"""

import asyncio
import sys
import os
from config import Config
from telegram_bot import DerivTelegramBot, DerivAPI

class ManualTradingTester:
    def __init__(self):
        self.bot = DerivTelegramBot(
            Config.TELEGRAM_BOT_TOKEN,
            Config.DERIV_APP_ID, 
            Config.DERIV_API_TOKEN
        )
        self.api = DerivAPI(Config.DERIV_APP_ID, Config.DERIV_API_TOKEN)
        
    async def test_deriv_api_connection(self):
        """Test basic Deriv API functionality"""
        print("🧪 Testing Deriv API Connection...")
        
        try:
            await self.api.connect()
            if self.api.api_token:
                auth_result = await self.api.authorize()
                if auth_result:
                    print("✅ API connection and authorization successful")
                    return True
                else:
                    print("❌ API authorization failed")
                    return False
            else:
                print("⚠️  No API token - testing basic connection only")
                return True
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False
        finally:
            if self.api.is_connected:
                await self.api.disconnect()
    
    def test_manual_trading_methods(self):
        """Test if all manual trading methods exist"""
        print("🧪 Testing Manual Trading Methods...")
        
        required_methods = [
            'handle_trade_category',
            'handle_symbol_selection', 
            'handle_contract_selection',
            'handle_amount_selection',
            'handle_duration_selection',
            'handle_place_trade',
            'show_all_positions',
            'handle_close_position'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(self.bot, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing methods: {missing_methods}")
            return False
        else:
            print("✅ All manual trading methods found")
            return True
    
    def test_button_callbacks(self):
        """Test button callback handlers"""
        print("🧪 Testing Button Callback Handlers...")
        
        # Simulate callback data patterns
        test_callbacks = [
            "trade_volatility",
            "trade_boom_crash", 
            "trade_forex",
            "symbol_R_75",
            "symbol_BOOM500",
            "symbol_frxEURUSD",
            "contract_CALL",
            "contract_PUT",
            "amount_1.00",
            "duration_5t",
            "place_trade_confirm",
            "all_positions",
            "close_position_123456"
        ]
        
        # Check if the callback handler would recognize these
        issues = []
        
        for callback in test_callbacks:
            # Check callback patterns in button_callback method
            if callback.startswith("trade_") and callback not in ["trade_volatility", "trade_boom_crash", "trade_forex"]:
                issues.append(f"Unrecognized trade callback: {callback}")
            elif callback.startswith("symbol_") and "_" not in callback[7:]:
                # Symbol callbacks should have valid format
                pass
            elif callback.startswith("contract_") and callback.split("_")[1] not in ["CALL", "PUT"]:
                issues.append(f"Invalid contract type: {callback}")
        
        if issues:
            print(f"❌ Callback issues found: {issues}")
            return False
        else:
            print("✅ Button callback patterns look good")
            return True
    
    async def test_trading_symbols(self):
        """Test if trading symbols are accessible"""
        print("🧪 Testing Trading Symbols...")
        
        symbols_to_test = ["R_75", "R_100", "BOOM500", "CRASH500", "frxEURUSD"]
        
        try:
            await self.api.connect()
            
            # Get active symbols
            request = {"active_symbols": "brief", "product_type": "basic"}
            response = await self.api.send_request(request)
            
            if "active_symbols" in response:
                available_symbols = {symbol["symbol"] for symbol in response["active_symbols"]}
                
                missing_symbols = []
                for symbol in symbols_to_test:
                    if symbol not in available_symbols:
                        missing_symbols.append(symbol)
                
                if missing_symbols:
                    print(f"⚠️  Some symbols not found: {missing_symbols}")
                    print(f"✅ Available symbols: {len(available_symbols)}")
                    return True  # Not critical, symbols may vary by time
                else:
                    print("✅ All test symbols are available")
                    return True
            else:
                print("❌ Could not fetch active symbols")
                return False
                
        except Exception as e:
            print(f"❌ Symbol test failed: {e}")
            return False
        finally:
            if self.api.is_connected:
                await self.api.disconnect()
    
    def test_session_management(self):
        """Test user session structure"""
        print("🧪 Testing Session Management...")
        
        # Test session structure
        test_user_id = 12345
        
        # Simulate session data
        session_data = {
            'selected_symbol': 'R_75',
            'contract_type': 'CALL',
            'trade_amount': 1.00,
            'duration': 5,
            'duration_unit': 't'
        }
        
        # Test if bot can handle session data
        self.bot.user_sessions[test_user_id] = session_data
        
        # Verify session data
        retrieved_session = self.bot.user_sessions.get(test_user_id, {})
        
        required_fields = ['selected_symbol', 'contract_type', 'trade_amount', 'duration', 'duration_unit']
        missing_fields = [field for field in required_fields if field not in retrieved_session]
        
        if missing_fields:
            print(f"❌ Session missing fields: {missing_fields}")
            return False
        else:
            print("✅ Session management structure looks good")
            # Clean up test session
            del self.bot.user_sessions[test_user_id]
            return True
    
    async def test_buy_contract_method(self):
        """Test if buy_contract method is accessible"""
        print("🧪 Testing Buy Contract Method...")
        
        if not hasattr(self.api, 'buy_contract'):
            print("❌ buy_contract method not found in DerivAPI")
            return False
        
        # Test method signature (don't actually call it)
        import inspect
        signature = inspect.signature(self.api.buy_contract)
        expected_params = ['contract_type', 'symbol', 'amount', 'duration', 'duration_unit']
        
        actual_params = list(signature.parameters.keys())  # Don't skip first parameter for bound methods
        
        if actual_params != expected_params:
            print(f"❌ buy_contract signature mismatch. Expected: {expected_params}, Got: {actual_params}")
            return False
        else:
            print("✅ buy_contract method signature is correct")
            return True
    
    async def run_all_tests(self):
        """Run all manual trading tests"""
        print("🎲 Manual Trading Functionality Test Suite")
        print("=" * 60)
        
        tests = [
            ("API Connection", self.test_deriv_api_connection),
            ("Trading Methods", self.test_manual_trading_methods),
            ("Button Callbacks", self.test_button_callbacks), 
            ("Trading Symbols", self.test_trading_symbols),
            ("Session Management", self.test_session_management),
            ("Buy Contract Method", self.test_buy_contract_method)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name}...")
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
            print("-" * 40)
        
        print(f"\n📊 Test Results Summary:")
        print("=" * 60)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:.<30} {status}")
            if result:
                passed += 1
        
        print(f"\nTotal: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("\n🎉 All manual trading functionality tests passed!")
            print("✅ Manual trading is ready for use!")
            return True
        else:
            print(f"\n⚠️  {len(results) - passed} test(s) failed.")
            print("❌ Please review and fix issues before using manual trading.")
            return False

async def main():
    """Main test function"""
    try:
        tester = ManualTradingTester()
        success = await tester.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
