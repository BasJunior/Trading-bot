#!/usr/bin/env python3
"""
Minimal bot test to isolate the /start command issue
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalBot:
    def __init__(self):
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Minimal start command"""
        try:
            logger.info(f"Start command received from user {update.effective_user.id}")
            
            welcome_message = f"""
🎯 Welcome to Deriv Trading Bot, {update.effective_user.first_name}!

This is a test response to confirm the bot is working.
            """
            
            keyboard = [
                [InlineKeyboardButton("✅ Test Button", callback_data="test")],
                [InlineKeyboardButton("❓ Help", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
            logger.info("Start command completed successfully")
            
        except Exception as e:
            logger.error(f"Error in start_command: {e}")
            await update.message.reply_text("❌ An error occurred while starting.")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "test":
            await query.edit_message_text("✅ Button test successful!")
        elif query.data == "help":
            await query.edit_message_text("ℹ️ This is a minimal test bot.")
    
    def run(self):
        self.application.run_polling()

if __name__ == "__main__":
    try:
        bot = MinimalBot()
        print("🤖 Starting Minimal Test Bot...")
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Bot error: {e}")
