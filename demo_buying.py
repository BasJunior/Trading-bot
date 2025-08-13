#!/usr/bin/env python3
"""
Demo: How to Buy Contracts on Deriv
This script demonstrates the programmatic way to buy contracts
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from connection_manager_fixed import DerivAPI
from config import Config

async def demo_buying_process():
    """Demonstrate how to buy contracts on Deriv"""
    
    print("🎯 DERIV BUYING DEMO")
    print("=" * 50)
    
    # Initialize API connection
    api = DerivAPI(Config.DERIV_APP_ID, Config.DERIV_API_TOKEN)
    
    try:
        # Step 1: Connect to Deriv
        print("1️⃣ Connecting to Deriv...")
        await api.connect()
        print("✅ Connected successfully!")
        
        # Step 2: Check balance
        print("\n2️⃣ Checking account balance...")
        balance_response = await api.get_balance()
        if "balance" in balance_response:
            balance = balance_response["balance"]["balance"]
            currency = balance_response["balance"]["currency"]
            print(f"💰 Account Balance: {balance} {currency}")
        else:
            print("⚠️ Could not fetch balance (demo mode)")
        
        # Step 3: Get available symbols
        print("\n3️⃣ Getting available trading symbols...")
        symbols_response = await api.get_active_symbols()
        if "active_symbols" in symbols_response:
            # Show some popular symbols
            symbols = symbols_response["active_symbols"]
            volatility_symbols = [s for s in symbols if s["symbol"].startswith("R_") or "V" in s["symbol"]][:5]
            
            print("📊 Popular Volatility Symbols:")
            for symbol in volatility_symbols:
                print(f"   • {symbol['symbol']}: {symbol['display_name']}")
        
        # Step 4: Get current price for a symbol
        print("\n4️⃣ Getting current price for V75...")
        try:
            ticks_response = await api.get_ticks("R_75")  # V75 equivalent
            if "tick" in ticks_response:
                current_price = ticks_response["tick"]["quote"]
                print(f"📈 Current V75 Price: {current_price}")
            else:
                print("📈 Current price: Demo data (12345.67)")
                current_price = 12345.67
        except:
            print("📈 Using demo price: 12345.67")
            current_price = 12345.67
        
        # Step 5: Get proposal (price quote) for a trade
        print("\n5️⃣ Getting trade proposal...")
        try:
            proposal_response = await api.get_proposal(
                contract_type="CALL",
                symbol="R_75",
                amount=5.0,
                duration=10,
                duration_unit="t"
            )
            
            if "proposal" in proposal_response:
                proposal = proposal_response["proposal"]
                payout = proposal.get("payout", 0)
                ask_price = proposal.get("ask_price", 0)
                
                print(f"💡 Trade Proposal:")
                print(f"   • Contract: CALL on R_75")
                print(f"   • Stake: $5.00")
                print(f"   • Duration: 10 ticks")
                print(f"   • Ask Price: ${ask_price}")
                print(f"   • Potential Payout: ${payout}")
                print(f"   • Potential Profit: ${payout - ask_price:.2f}")
            else:
                print("💡 Demo Proposal: CALL R_75, $5 stake, $9.50 payout")
                
        except Exception as e:
            print(f"💡 Demo Proposal: CALL R_75, $5 stake, $9.50 payout")
            print(f"   (Proposal error: {e})")
        
        # Step 6: Demonstrate buy process (without actually buying)
        print("\n6️⃣ Buy Process Demonstration...")
        print("🚨 NOTE: This is a DEMO - no actual trade will be placed")
        
        print("\n📝 To buy a contract, you would:")
        print("1. Choose contract type: CALL (up) or PUT (down)")
        print("2. Select symbol: R_75 (Volatility 75)")
        print("3. Set amount: $5.00")
        print("4. Set duration: 10 ticks")
        print("5. Execute buy command")
        
        # Show the actual buy command structure
        print("\n💻 Buy Command Structure:")
        buy_request = {
            "buy": 1,
            "price": 5.0,
            "parameters": {
                "contract_type": "CALL",
                "symbol": "R_75", 
                "duration": 10,
                "duration_unit": "t",
                "amount": 5.0
            }
        }
        print(f"   Request: {buy_request}")
        
        # Simulate what would happen
        print("\n🎲 If this was a real trade:")
        print("   ✅ Trade would be executed")
        print("   📊 Position would appear in portfolio")
        print("   ⏱️ Contract would expire in 10 ticks")
        print("   💰 You'd win or lose based on price movement")
        
        # Step 7: Show portfolio check
        print("\n7️⃣ Checking portfolio...")
        try:
            portfolio_response = await api.get_portfolio()
            if "portfolio" in portfolio_response:
                contracts = portfolio_response["portfolio"]["contracts"]
                print(f"📋 Active Positions: {len(contracts)}")
                for contract in contracts[:3]:  # Show first 3
                    symbol = contract.get("symbol", "Unknown")
                    contract_type = contract.get("contract_type", "Unknown")
                    profit_loss = contract.get("profit_loss", 0)
                    status = "🟢" if profit_loss > 0 else "🔴" if profit_loss < 0 else "🟡"
                    print(f"   {status} {symbol} {contract_type}: ${profit_loss:.2f}")
            else:
                print("📋 No active positions (or demo mode)")
        except Exception as e:
            print(f"📋 Portfolio check: Demo mode ({e})")
        
        print("\n" + "=" * 50)
        print("✅ DEMO COMPLETED!")
        print("\n💡 To place real trades:")
        print("1. Start your Telegram bot: ./start_bot_simple.sh")
        print("2. Send /start in Telegram")
        print("3. Use /connect to add your API token")
        print("4. Click '🎲 Manual Trade' to start trading")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("💡 This is normal if you don't have a valid API token")
        print("   The demo shows how the buying process works")
    
    finally:
        # Cleanup
        try:
            await api.disconnect()
            print("🔌 Disconnected from Deriv")
        except:
            pass

async def show_buying_examples():
    """Show different buying scenarios"""
    
    print("\n" + "=" * 50)
    print("📚 BUYING EXAMPLES")
    print("=" * 50)
    
    examples = [
        {
            "name": "Quick Volatility Trade",
            "contract_type": "CALL",
            "symbol": "R_75",
            "amount": 5.0,
            "duration": 5,
            "duration_unit": "t",
            "description": "5-tick CALL on V75, expecting price to go up"
        },
        {
            "name": "Forex Swing Trade", 
            "contract_type": "PUT",
            "symbol": "frxEURUSD",
            "amount": 10.0,
            "duration": 15,
            "duration_unit": "m",
            "description": "15-minute PUT on EUR/USD, expecting price to go down"
        },
        {
            "name": "Boom Crash Scalp",
            "contract_type": "CALL",
            "symbol": "BOOM1000",
            "amount": 2.0,
            "duration": 1,
            "duration_unit": "m",
            "description": "1-minute CALL on Boom 1000, quick scalp"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}️⃣ {example['name']}")
        print(f"   Contract Type: {example['contract_type']}")
        print(f"   Symbol: {example['symbol']}")
        print(f"   Amount: ${example['amount']}")
        print(f"   Duration: {example['duration']} {example['duration_unit']}")
        print(f"   Strategy: {example['description']}")
        
        # Show JSON structure
        buy_structure = {
            "buy": 1,
            "price": example['amount'],
            "parameters": {
                "contract_type": example['contract_type'],
                "symbol": example['symbol'],
                "duration": example['duration'],
                "duration_unit": example['duration_unit'],
                "amount": example['amount']
            }
        }
        print(f"   API Call: {buy_structure}")

if __name__ == "__main__":
    print("🚀 Starting Deriv Buying Demo...")
    
    # Run the demo
    asyncio.run(demo_buying_process())
    
    # Show examples
    asyncio.run(show_buying_examples())
    
    print("\n📖 For complete guide, see: HOW_TO_BUY_GUIDE.py")
    print("🤖 For live trading, start your Telegram bot!")
