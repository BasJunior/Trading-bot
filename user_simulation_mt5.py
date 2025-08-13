#!/usr/bin/env python3
"""
Simplified MT5 Integration User Simulation
Tests the user experience flow for MT5 CFD trading commands
"""

import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramSimulator:
    """Simulates Telegram bot interactions for MT5 integration"""
    
    def __init__(self):
        self.user_id = 12345
        self.mt5_accounts = {}  # user_id -> account_info
        self.cfd_positions = {}  # user_id -> list of positions
        self.next_ticket = 100001
        
    async def simulate_message(self, command, args=None):
        """Simulate a user sending a command"""
        args = args or []
        full_command = f"/{command} {' '.join(args)}".strip()
        
        print(f"\n👤 User {self.user_id}: {full_command}")
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Process the command
        if command == "mt5_connect":
            return await self._handle_mt5_connect()
        elif command == "mt5_setup":
            return await self._handle_mt5_setup(args)
        elif command == "cfd_trade":
            return await self._handle_cfd_trade(args)
        elif command == "cfd_positions":
            return await self._handle_cfd_positions()
        elif command == "mt5_balance":
            return await self._handle_mt5_balance()
        elif command == "cfd_close":
            return await self._handle_cfd_close(args)
        else:
            return "❌ Unknown command"
    
    async def _handle_mt5_connect(self):
        """Handle MT5 connect command"""
        await asyncio.sleep(0.2)  # Simulate processing
        
        if self.user_id in self.mt5_accounts:
            return """✅ You already have an MT5 account connected. Use /mt5_disconnect to change accounts."""
        else:
            return """🔗 **Connect Your MT5 Account**

To enable CFD trading, please provide your MT5 credentials:

Format: `/mt5_setup <login> <password> <server>`

Example: `/mt5_setup 12345678 MyPassword123 Deriv-Demo`

⚠️ **Security Note:** Your credentials are used only to connect to MT5 and are not stored permanently."""
    
    async def _handle_mt5_setup(self, args):
        """Handle MT5 setup command"""
        if len(args) != 3:
            return """❌ Invalid format. Use: `/mt5_setup <login> <password> <server>`"""
        
        try:
            login = int(args[0])
            password = args[1]
            server = args[2]
            
            await asyncio.sleep(1.0)  # Simulate connection time
            
            # Simulate successful connection
            self.mt5_accounts[self.user_id] = {
                'login': login,
                'password': password,  # In real implementation, this would be encrypted
                'server': server,
                'balance': 10000.0,
                'equity': 10000.0,
                'margin': 0.0,
                'margin_free': 10000.0,
                'margin_level': 0.0,
                'currency': 'USD',
                'profit': 0.0,
                'company': 'Deriv Limited',
                'connected_at': datetime.now()
            }
            
            self.cfd_positions[self.user_id] = []
            
            return f"""✅ **MT5 Account Connected Successfully!**

💰 Balance: 10000.0 USD
🏢 Broker: Deriv Limited
🖥️ Server: {server}

You can now use CFD trading commands:
• /cfd_trade - Place CFD trades
• /cfd_positions - View open positions
• /mt5_balance - Check account balance"""
            
        except ValueError:
            return "❌ Invalid login number. Login must be numeric."
        except Exception as e:
            return f"❌ An error occurred while setting up MT5 account: {str(e)}"
    
    async def _handle_cfd_trade(self, args):
        """Handle CFD trade command"""
        if self.user_id not in self.mt5_accounts:
            return "❌ No MT5 account connected. Use /mt5_connect to setup your account first."
        
        if len(args) < 3:
            return """❌ Invalid format. Use: `/cfd_trade <symbol> <direction> <volume> [sl] [tp]`

Examples:
• `/cfd_trade EURUSD BUY 0.1` - Buy 0.1 lots EUR/USD
• `/cfd_trade XAUUSD SELL 0.05 1950 1970` - Sell Gold with SL/TP
• `/cfd_trade US30 BUY 0.1` - Buy US30 index"""
        
        try:
            symbol = args[0].upper()
            direction = args[1].upper()
            volume = float(args[2])
            sl = float(args[3]) if len(args) > 3 else 0
            tp = float(args[4]) if len(args) > 4 else 0
            
            if direction not in ['BUY', 'SELL']:
                return "❌ Direction must be BUY or SELL"
            
            if volume <= 0 or volume > 10:
                return "❌ Volume must be between 0.01 and 10.0"
            
            await asyncio.sleep(0.5)  # Simulate execution time
            
            # Simulate successful trade
            ticket = self.next_ticket
            self.next_ticket += 1
            
            # Mock prices based on symbol
            prices = {
                'EURUSD': 1.0950,
                'GBPUSD': 1.2650,
                'XAUUSD': 1965.50,
                'US30': 34250.0,
                'USDCAD': 1.3580
            }
            price = prices.get(symbol, 1.0000)
            
            # Create position
            position = {
                'ticket': ticket,
                'symbol': symbol,
                'type': 0 if direction == 'BUY' else 1,
                'volume': volume,
                'price_open': price,
                'price_current': price + (0.0005 if direction == 'BUY' else -0.0005),
                'profit': 5.0 * volume,  # Simulate small profit
                'swap': -0.5,
                'sl': sl,
                'tp': tp,
                'time': datetime.now()
            }
            
            self.cfd_positions[self.user_id].append(position)
            
            # Update account balance
            account = self.mt5_accounts[self.user_id]
            account['margin'] += volume * 100  # Simulate margin requirement
            account['margin_free'] = account['balance'] - account['margin']
            account['profit'] += position['profit']
            account['equity'] = account['balance'] + account['profit']
            
            return f"""✅ **CFD Trade Executed Successfully!**

📊 Trade Details:
• Ticket: #{ticket}
• Symbol: {symbol}
• Direction: {direction}
• Volume: {volume} lots
• Price: {price}
• SL: {sl if sl > 0 else 'Not set'}
• TP: {tp if tp > 0 else 'Not set'}

Use /cfd_positions to monitor your trade."""
            
        except ValueError:
            return "❌ Invalid volume or price values. Use numeric values only."
        except Exception as e:
            return f"❌ An error occurred while placing the trade: {str(e)}"
    
    async def _handle_cfd_positions(self):
        """Handle CFD positions command"""
        if self.user_id not in self.mt5_accounts:
            return "❌ No MT5 account connected. Use /mt5_connect to setup your account first."
        
        positions = self.cfd_positions.get(self.user_id, [])
        
        if not positions:
            return "📊 No open CFD positions."
        
        await asyncio.sleep(0.3)  # Simulate data retrieval
        
        positions_text = "📊 **Your CFD Positions:**\n\n"
        total_profit = 0
        
        for i, pos in enumerate(positions, 1):
            direction = "BUY" if pos['type'] == 0 else "SELL"
            profit_emoji = "🟢" if pos['profit'] >= 0 else "🔴"
            
            positions_text += f"{profit_emoji} **Position #{i}**\n"
            positions_text += f"• Ticket: #{pos['ticket']}\n"
            positions_text += f"• Symbol: {pos['symbol']}\n"
            positions_text += f"• Direction: {direction}\n"
            positions_text += f"• Volume: {pos['volume']} lots\n"
            positions_text += f"• Open Price: {pos['price_open']}\n"
            positions_text += f"• Current Price: {pos['price_current']}\n"
            positions_text += f"• P&L: ${pos['profit']:.2f}\n"
            positions_text += f"• Swap: ${pos['swap']:.2f}\n\n"
            
            total_profit += pos['profit']
        
        total_emoji = "🟢" if total_profit >= 0 else "🔴"
        positions_text += f"{total_emoji} **Total P&L: ${total_profit:.2f}**\n\n"
        positions_text += f"💡 Use `/cfd_close <ticket>` to close a position"
        
        return positions_text
    
    async def _handle_mt5_balance(self):
        """Handle MT5 balance command"""
        if self.user_id not in self.mt5_accounts:
            return "❌ No MT5 account connected. Use /mt5_connect to setup your account first."
        
        await asyncio.sleep(0.2)  # Simulate data retrieval
        
        account = self.mt5_accounts[self.user_id]
        
        balance_text = f"💰 **MT5 Account Summary**\n\n"
        balance_text += f"💵 Balance: {account['balance']:.2f} {account['currency']}\n"
        balance_text += f"💎 Equity: {account['equity']:.2f} {account['currency']}\n"
        balance_text += f"📊 Floating P&L: {account['profit']:.2f} {account['currency']}\n"
        balance_text += f"🔒 Margin Used: {account['margin']:.2f} {account['currency']}\n"
        balance_text += f"🆓 Free Margin: {account['margin_free']:.2f} {account['currency']}\n"
        
        if account['margin'] > 0:
            margin_level = (account['equity'] / account['margin']) * 100
            balance_text += f"📈 Margin Level: {margin_level:.1f}%\n\n"
            
            if margin_level < 50:
                balance_text += "🚨 **WARNING: Low margin level!**\n"
            elif margin_level < 100:
                balance_text += "⚠️ **CAUTION: Monitor margin level**\n"
        else:
            balance_text += f"📈 Margin Level: No positions\n\n"
        
        balance_text += f"🏢 Broker: {account['company']}\n"
        balance_text += f"🖥️ Server: {account['server']}"
        
        return balance_text
    
    async def _handle_cfd_close(self, args):
        """Handle CFD close command"""
        if self.user_id not in self.mt5_accounts:
            return "❌ No MT5 account connected. Use /mt5_connect to setup your account first."
        
        if len(args) != 1:
            return """❌ Invalid format. Use: `/cfd_close <ticket>`

Example: `/cfd_close 123456789`

Use /cfd_positions to see your open positions and their ticket numbers."""
        
        try:
            ticket = int(args[0])
            
            await asyncio.sleep(0.4)  # Simulate execution time
            
            positions = self.cfd_positions.get(self.user_id, [])
            
            # Find and remove position
            for i, pos in enumerate(positions):
                if pos['ticket'] == ticket:
                    closed_pos = positions.pop(i)
                    
                    # Update account
                    account = self.mt5_accounts[self.user_id]
                    account['balance'] += closed_pos['profit']
                    account['margin'] -= closed_pos['volume'] * 100
                    account['margin_free'] = account['balance'] - account['margin']
                    account['profit'] -= closed_pos['profit']
                    account['equity'] = account['balance'] + account['profit']
                    
                    return f"""✅ **Position Closed Successfully!**

• Ticket: #{ticket}
• Close Price: {closed_pos['price_current']}
• Volume: {closed_pos['volume']} lots
• Profit: ${closed_pos['profit']:.2f}

Use /mt5_balance to check your updated balance."""
            
            return f"""❌ **Failed to Close Position**

Error: Position with ticket #{ticket} not found

Please check:
• Position ticket number is correct
• Position is still open
• Use /cfd_positions to see open positions"""
            
        except ValueError:
            return "❌ Invalid ticket number. Ticket must be numeric."
        except Exception as e:
            return f"❌ An error occurred while closing the position: {str(e)}"

async def run_user_simulation():
    """Run a complete user simulation"""
    simulator = TelegramSimulator()
    
    print("🎭 MT5 CFD Trading - User Experience Simulation")
    print("=" * 60)
    
    # Simulation steps
    scenarios = [
        ("Initial connection attempt", "mt5_connect", []),
        ("Setup MT5 account", "mt5_setup", ["12345678", "MyPassword123", "Deriv-Demo"]),
        ("Check account balance", "mt5_balance", []),
        ("Place EUR/USD trade", "cfd_trade", ["EURUSD", "BUY", "0.1"]),
        ("Place Gold trade with SL/TP", "cfd_trade", ["XAUUSD", "SELL", "0.05", "1970", "1950"]),
        ("View all positions", "cfd_positions", []),
        ("Check updated balance", "mt5_balance", []),
        ("Close first position", "cfd_close", ["100001"]),
        ("View remaining positions", "cfd_positions", []),
        ("Final balance check", "mt5_balance", []),
    ]
    
    for step, (description, command, args) in enumerate(scenarios, 1):
        print(f"\n📍 Step {step}: {description}")
        print("-" * 40)
        
        response = await simulator.simulate_message(command, args)
        
        print(f"🤖 Bot Response:")
        print(response)
        
        await asyncio.sleep(0.5)  # Pause between steps
    
    print("\n" + "=" * 60)
    print("✅ User Experience Simulation Completed!")
    
    # Summary
    print(f"\n📊 Simulation Summary:")
    print(f"• MT5 accounts connected: {len(simulator.mt5_accounts)}")
    print(f"• Active CFD positions: {len(simulator.cfd_positions.get(simulator.user_id, []))}")
    print(f"• Commands tested: {len(scenarios)}")
    
    if simulator.user_id in simulator.mt5_accounts:
        account = simulator.mt5_accounts[simulator.user_id]
        print(f"• Final account balance: {account['balance']:.2f} {account['currency']}")
        print(f"• Total profit/loss: {account['profit']:.2f} {account['currency']}")

if __name__ == "__main__":
    asyncio.run(run_user_simulation())
