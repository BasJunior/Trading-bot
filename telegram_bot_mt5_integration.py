#!/usr/bin/env python3
"""
Example integration of MT5 CFD trading into the existing Telegram bot
This shows how to add CFD functionality alongside Digital Options
"""

# Example additions to telegram_bot.py for CFD trading

"""
===============================================================================
TELEGRAM BOT INTEGRATION - MT5 CFD TRADING
===============================================================================

Add these imports to the top of telegram_bot.py:
"""

# Additional imports for MT5 CFD trading
try:
    from mt5_cfd_trading import (
        setup_user_mt5_account,
        place_cfd_trade, 
        close_cfd_trade,
        get_cfd_positions,
        get_mt5_account_info,
        MT5CFDTrader,
        OrderType,
        TradeResult
    )
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MT5 module not available. CFD trading disabled.")

"""
===============================================================================
NEW COMMAND HANDLERS
===============================================================================
"""

async def mt5_connect_command(self, update, context):
    """Connect user's MT5 account"""
    user_id = update.effective_user.id
    
    if not MT5_AVAILABLE:
        await update.message.reply_text("❌ MT5 CFD trading is not available on this bot.")
        return
    
    # Check if user already has MT5 connected
    from mt5_cfd_trading import mt5_integration
    if mt5_integration.get_user_mt5(user_id):
        await update.message.reply_text("✅ You already have an MT5 account connected. Use /mt5_disconnect to change accounts.")
        return
    
    await update.message.reply_text(
        "🔗 **Connect Your MT5 Account**\n\n"
        "To enable CFD trading, please provide your MT5 credentials:\n\n"
        "Format: `/mt5_setup <login> <password> <server>`\n\n"
        "Example: `/mt5_setup 12345678 MyPassword123 Deriv-Demo`\n\n"
        "⚠️ **Security Note:** Your credentials are used only to connect to MT5 and are not stored permanently.",
        parse_mode='Markdown'
    )

async def mt5_setup_command(self, update, context):
    """Setup MT5 account with credentials"""
    user_id = update.effective_user.id
    
    if not MT5_AVAILABLE:
        await update.message.reply_text("❌ MT5 CFD trading is not available.")
        return
    
    if len(context.args) != 3:
        await update.message.reply_text(
            "❌ Invalid format. Use: `/mt5_setup <login> <password> <server>`",
            parse_mode='Markdown'
        )
        return
    
    try:
        login = int(context.args[0])
        password = context.args[1]
        server = context.args[2]
        
        # Attempt to setup MT5 account
        await update.message.reply_text("🔄 Connecting to your MT5 account...")
        
        success = await setup_user_mt5_account(user_id, login, password, server)
        
        if success:
            # Get account info
            account_info = get_mt5_account_info(user_id)
            balance = account_info.get('balance', 0)
            currency = account_info.get('currency', 'USD')
            
            await update.message.reply_text(
                f"✅ **MT5 Account Connected Successfully!**\n\n"
                f"💰 Balance: {balance} {currency}\n"
                f"🏢 Broker: {account_info.get('company', 'Unknown')}\n"
                f"🖥️ Server: {server}\n\n"
                f"You can now use CFD trading commands:\n"
                f"• /cfd_trade - Place CFD trades\n"
                f"• /cfd_positions - View open positions\n"
                f"• /mt5_balance - Check account balance",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ Failed to connect to MT5 account.\n\n"
                "Please check:\n"
                "• Login credentials are correct\n"
                "• Server name is correct\n"
                "• MT5 platform is running\n"
                "• Account allows API trading"
            )
    
    except ValueError:
        await update.message.reply_text("❌ Invalid login number. Login must be numeric.")
    except Exception as e:
        logger.error(f"MT5 setup error for user {user_id}: {e}")
        await update.message.reply_text("❌ An error occurred while setting up MT5 account.")

async def cfd_trade_command(self, update, context):
    """Place a CFD trade"""
    user_id = update.effective_user.id
    
    if not MT5_AVAILABLE:
        await update.message.reply_text("❌ MT5 CFD trading is not available.")
        return
    
    # Check if user has MT5 connected
    from mt5_cfd_trading import mt5_integration
    if not mt5_integration.get_user_mt5(user_id):
        await update.message.reply_text(
            "❌ No MT5 account connected. Use /mt5_connect to setup your account first."
        )
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "❌ Invalid format. Use: `/cfd_trade <symbol> <direction> <volume> [sl] [tp]`\n\n"
            "Examples:\n"
            "• `/cfd_trade EURUSD BUY 0.1` - Buy 0.1 lots EUR/USD\n"
            "• `/cfd_trade XAUUSD SELL 0.05 1950 1970` - Sell Gold with SL/TP\n"
            "• `/cfd_trade US30 BUY 0.1` - Buy US30 index",
            parse_mode='Markdown'
        )
        return
    
    try:
        symbol = context.args[0].upper()
        direction = context.args[1].upper()
        volume = float(context.args[2])
        sl = float(context.args[3]) if len(context.args) > 3 else 0
        tp = float(context.args[4]) if len(context.args) > 4 else 0
        
        if direction not in ['BUY', 'SELL']:
            await update.message.reply_text("❌ Direction must be BUY or SELL")
            return
        
        if volume <= 0 or volume > 10:  # Max 10 lots for safety
            await update.message.reply_text("❌ Volume must be between 0.01 and 10.0")
            return
        
        await update.message.reply_text("🔄 Placing CFD trade...")
        
        # Place the trade
        result = await place_cfd_trade(user_id, symbol, direction, volume, sl, tp)
        
        if result.success:
            await update.message.reply_text(
                f"✅ **CFD Trade Executed Successfully!**\n\n"
                f"📊 Trade Details:\n"
                f"• Ticket: #{result.ticket}\n"
                f"• Symbol: {symbol}\n"
                f"• Direction: {direction}\n"
                f"• Volume: {volume} lots\n"
                f"• Price: {result.price}\n"
                f"• SL: {sl if sl > 0 else 'Not set'}\n"
                f"• TP: {tp if tp > 0 else 'Not set'}\n\n"
                f"Use /cfd_positions to monitor your trade.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ **Trade Failed**\n\n"
                f"Error: {result.error_description}\n\n"
                f"Please check:\n"
                f"• Symbol is available for trading\n"
                f"• Sufficient margin in account\n"
                f"• Market is open for trading"
            )
    
    except ValueError:
        await update.message.reply_text("❌ Invalid volume or price values. Use numeric values only.")
    except Exception as e:
        logger.error(f"CFD trade error for user {user_id}: {e}")
        await update.message.reply_text("❌ An error occurred while placing the trade.")

async def cfd_positions_command(self, update, context):
    """Show user's CFD positions"""
    user_id = update.effective_user.id
    
    if not MT5_AVAILABLE:
        await update.message.reply_text("❌ MT5 CFD trading is not available.")
        return
    
    # Check if user has MT5 connected
    from mt5_cfd_trading import mt5_integration
    if not mt5_integration.get_user_mt5(user_id):
        await update.message.reply_text(
            "❌ No MT5 account connected. Use /mt5_connect to setup your account first."
        )
        return
    
    try:
        positions = get_cfd_positions(user_id)
        
        if not positions:
            await update.message.reply_text("📊 No open CFD positions.")
            return
        
        positions_text = "📊 **Your CFD Positions:**\n\n"
        total_profit = 0
        
        for i, pos in enumerate(positions, 1):
            direction = "BUY" if pos.type == 0 else "SELL"
            profit_emoji = "🟢" if pos.profit >= 0 else "🔴"
            
            positions_text += f"{profit_emoji} **Position #{i}**\n"
            positions_text += f"• Ticket: #{pos.ticket}\n"
            positions_text += f"• Symbol: {pos.symbol}\n"
            positions_text += f"• Direction: {direction}\n"
            positions_text += f"• Volume: {pos.volume} lots\n"
            positions_text += f"• Open Price: {pos.price_open}\n"
            positions_text += f"• Current Price: {pos.price_current}\n"
            positions_text += f"• P&L: ${pos.profit:.2f}\n"
            positions_text += f"• Swap: ${pos.swap:.2f}\n\n"
            
            total_profit += pos.profit
        
        total_emoji = "🟢" if total_profit >= 0 else "🔴"
        positions_text += f"{total_emoji} **Total P&L: ${total_profit:.2f}**\n\n"
        positions_text += f"💡 Use `/cfd_close <ticket>` to close a position"
        
        await update.message.reply_text(positions_text, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Error getting CFD positions for user {user_id}: {e}")
        await update.message.reply_text("❌ An error occurred while fetching your positions.")

async def cfd_close_command(self, update, context):
    """Close a CFD position"""
    user_id = update.effective_user.id
    
    if not MT5_AVAILABLE:
        await update.message.reply_text("❌ MT5 CFD trading is not available.")
        return
    
    # Check if user has MT5 connected
    from mt5_cfd_trading import mt5_integration
    if not mt5_integration.get_user_mt5(user_id):
        await update.message.reply_text(
            "❌ No MT5 account connected. Use /mt5_connect to setup your account first."
        )
        return
    
    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ Invalid format. Use: `/cfd_close <ticket>`\n\n"
            "Example: `/cfd_close 123456789`\n\n"
            "Use /cfd_positions to see your open positions and their ticket numbers.",
            parse_mode='Markdown'
        )
        return
    
    try:
        ticket = int(context.args[0])
        
        await update.message.reply_text("🔄 Closing CFD position...")
        
        result = await close_cfd_trade(user_id, ticket)
        
        if result.success:
            await update.message.reply_text(
                f"✅ **Position Closed Successfully!**\n\n"
                f"• Ticket: #{ticket}\n"
                f"• Close Price: {result.price}\n"
                f"• Volume: {result.volume} lots\n\n"
                f"Use /mt5_balance to check your updated balance.",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ **Failed to Close Position**\n\n"
                f"Error: {result.error_description}\n\n"
                f"Please check:\n"
                f"• Position ticket number is correct\n"
                f"• Position is still open\n"
                f"• Market is open for trading"
            )
    
    except ValueError:
        await update.message.reply_text("❌ Invalid ticket number. Ticket must be numeric.")
    except Exception as e:
        logger.error(f"Error closing CFD position for user {user_id}: {e}")
        await update.message.reply_text("❌ An error occurred while closing the position.")

async def mt5_balance_command(self, update, context):
    """Show MT5 account balance"""
    user_id = update.effective_user.id
    
    if not MT5_AVAILABLE:
        await update.message.reply_text("❌ MT5 CFD trading is not available.")
        return
    
    # Check if user has MT5 connected
    from mt5_cfd_trading import mt5_integration
    if not mt5_integration.get_user_mt5(user_id):
        await update.message.reply_text(
            "❌ No MT5 account connected. Use /mt5_connect to setup your account first."
        )
        return
    
    try:
        account_info = get_mt5_account_info(user_id)
        
        if not account_info:
            await update.message.reply_text("❌ Could not retrieve account information.")
            return
        
        balance = account_info.get('balance', 0)
        equity = account_info.get('equity', 0)
        margin = account_info.get('margin', 0)
        free_margin = account_info.get('margin_free', 0)
        margin_level = account_info.get('margin_level', 0)
        currency = account_info.get('currency', 'USD')
        profit = account_info.get('profit', 0)
        
        balance_text = f"💰 **MT5 Account Summary**\n\n"
        balance_text += f"💵 Balance: {balance:.2f} {currency}\n"
        balance_text += f"💎 Equity: {equity:.2f} {currency}\n"
        balance_text += f"📊 Floating P&L: {profit:.2f} {currency}\n"
        balance_text += f"🔒 Margin Used: {margin:.2f} {currency}\n"
        balance_text += f"🆓 Free Margin: {free_margin:.2f} {currency}\n"
        
        if margin > 0:
            balance_text += f"📈 Margin Level: {margin_level:.1f}%\n\n"
            
            if margin_level < 50:
                balance_text += "🚨 **WARNING: Low margin level!**\n"
            elif margin_level < 100:
                balance_text += "⚠️ **CAUTION: Monitor margin level**\n"
        else:
            balance_text += f"📈 Margin Level: No positions\n\n"
        
        balance_text += f"🏢 Broker: {account_info.get('company', 'Unknown')}\n"
        balance_text += f"🖥️ Server: {account_info.get('server', 'Unknown')}"
        
        await update.message.reply_text(balance_text, parse_mode='Markdown')
    
    except Exception as e:
        logger.error(f"Error getting MT5 balance for user {user_id}: {e}")
        await update.message.reply_text("❌ An error occurred while fetching account information.")

"""
===============================================================================
UPDATE MAIN MENU TO INCLUDE CFD OPTIONS
===============================================================================
"""

def get_enhanced_main_menu(self, has_personal_account=False):
    """Enhanced main menu with CFD options"""
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="balance")],
    ]
    
    if has_personal_account:
        # Digital Options (existing)
        keyboard.append([InlineKeyboardButton("🎲 Digital Options", callback_data="manual_trade")])
        
        # CFD Trading (new)
        if MT5_AVAILABLE:
            keyboard.append([InlineKeyboardButton("📊 CFD Trading", callback_data="cfd_menu")])
        
        keyboard.extend([
            [InlineKeyboardButton("📋 All Positions", callback_data="all_positions")],
            [InlineKeyboardButton("🤖 Auto Strategies", callback_data="auto_strategies")],
            [InlineKeyboardButton("📈 Market Analysis", callback_data="analysis")]
        ])
    else:
        keyboard.extend([
            [InlineKeyboardButton("🎲 Demo Trading", callback_data="manual_trade")],
            [InlineKeyboardButton("🔗 Connect Account", callback_data="connect_account")]
        ])
    
    keyboard.extend([
        [InlineKeyboardButton("📊 Live Prices", callback_data="live_prices")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
    ])
    
    return InlineKeyboardMarkup(keyboard)

"""
===============================================================================
HANDLER SETUP
===============================================================================
"""

def setup_mt5_handlers(self):
    """Add MT5 CFD trading handlers to the bot"""
    if MT5_AVAILABLE:
        self.application.add_handler(CommandHandler("mt5_connect", self.mt5_connect_command))
        self.application.add_handler(CommandHandler("mt5_setup", self.mt5_setup_command))
        self.application.add_handler(CommandHandler("cfd_trade", self.cfd_trade_command))
        self.application.add_handler(CommandHandler("cfd_positions", self.cfd_positions_command))
        self.application.add_handler(CommandHandler("cfd_close", self.cfd_close_command))
        self.application.add_handler(CommandHandler("mt5_balance", self.mt5_balance_command))
        
        logger.info("✅ MT5 CFD trading handlers added")
    else:
        logger.info("⚠️ MT5 not available, CFD handlers skipped")

# Add this to your existing setup_handlers method:
# self.setup_mt5_handlers()

if __name__ == "__main__":
    print("📖 MT5 CFD Integration Example")
    print("Add these functions to your telegram_bot.py to enable CFD trading")
    print("See MT5_INTEGRATION_GUIDE.py for complete setup instructions")
