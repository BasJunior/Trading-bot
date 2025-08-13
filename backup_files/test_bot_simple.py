#!/usr/bin/env python3
"""
Simple test script to check if the bot can start and respond to /start
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simple start command test"""
    try:
        logger.info(f"Received /start from user {update.effective_user.id}")
        
        welcome_message = "🎯 Bot is working! This is a test response."
        
        keyboard = [
            [InlineKeyboardButton("✅ Test Button", callback_data="test")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        logger.info("Start command completed successfully")
        
    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        await update.message.reply_text("❌ An error occurred.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot"""
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    """Main function"""
    try:
        # Create application
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_error_handler(error_handler)
        
        print("🤖 Starting Simple Test Bot...")
        print(f"Token configured: {'Yes' if Config.TELEGRAM_BOT_TOKEN else 'No'}")
        
        # Run the bot
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    main()
