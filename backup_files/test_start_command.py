#!/usr/bin/env python3
"""
Test the start command functionality to ensure it works without errors
"""

import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import DerivTelegramBot
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes

async def test_start_command():
    """Test the start command functionality"""
    try:
        print("🧪 Testing start command...")
        
        # Create bot instance
        bot = DerivTelegramBot()
        print("✅ Bot instance created")
        
        # Create mock update and context
        user = Mock(spec=User)
        user.id = 12345
        user.first_name = "Test User"
        
        chat = Mock(spec=Chat)
        chat.id = 12345
        
        message = Mock(spec=Message)
        message.reply_text = AsyncMock()
        
        update = Mock(spec=Update)
        update.effective_user = user
        update.message = message
        
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        
        print("✅ Mock objects created")
        
        # Test the start command
        await bot.start_command(update, context)
        print("✅ Start command executed successfully")
        
        # Verify that reply_text was called
        assert message.reply_text.called, "reply_text should have been called"
        print("✅ Reply message was sent")
        
        # Check the call arguments
        call_args = message.reply_text.call_args
        if call_args:
            args, kwargs = call_args
            print(f"✅ Message sent with text length: {len(args[0])}")
            print(f"✅ Reply markup included: {'reply_markup' in kwargs}")
        
        print("\n🎉 All start command tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_start_command())
    if success:
        print("\n✅ Start command test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Start command test failed!")
        sys.exit(1)
