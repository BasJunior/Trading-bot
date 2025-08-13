#!/usr/bin/env python3
"""
Interactive setup script for Deriv Telegram Bot tokens and configuration
"""

import os
import sys
import asyncio
import json
from pathlib import Path
import websockets
from dotenv import load_dotenv, set_key

class TokenSetupWizard:
    """Interactive wizard to set up bot tokens and configuration"""
    
    def __init__(self):
        self.env_file = Path(".env")
        self.api_url = "wss://ws.binaryws.com/websockets/v3"
        self.config = {}
        
    def print_header(self):
        """Print setup wizard header"""
        print("🚀 Deriv Telegram Bot - Token Setup Wizard")
        print("=" * 50)
        print("This wizard will help you configure your bot with the necessary tokens.")
        print()
    
    def get_user_input(self, prompt, default="", required=True, mask=False):
        """Get user input with validation"""
        while True:
            if default:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "
            
            if mask:
                import getpass
                value = getpass.getpass(full_prompt)
            else:
                value = input(full_prompt).strip()
            
            if not value and default:
                value = default
            
            if required and not value:
                print("❌ This field is required. Please enter a value.")
                continue
            
            return value
    
    def setup_telegram_token(self):
        """Setup Telegram bot token"""
        print("🤖 Telegram Bot Token Setup")
        print("-" * 30)
        print("To get your Telegram Bot Token:")
        print("1. Message @BotFather on Telegram")
        print("2. Send /newbot command")
        print("3. Follow the instructions to create your bot")
        print("4. Copy the token provided by BotFather")
        print()
        
        current_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        if current_token:
            print(f"Current token: {current_token[:10]}...{current_token[-10:]}")
            use_current = self.get_user_input("Use current token? (y/n)", "y", required=False)
            if use_current.lower() == 'y':
                self.config['TELEGRAM_BOT_TOKEN'] = current_token
                return
        
        token = self.get_user_input("Enter your Telegram Bot Token", mask=True)
        if not token.strip():
            print("❌ Telegram Bot Token is required!")
            return self.setup_telegram_token()
        
        self.config['TELEGRAM_BOT_TOKEN'] = token
        print("✅ Telegram Bot Token saved")
        print()
    
    def setup_deriv_app_id(self):
        """Setup Deriv App ID"""
        print("🔑 Deriv App ID Setup")
        print("-" * 30)
        print("To get your Deriv App ID:")
        print("1. Go to https://developers.deriv.com/")
        print("2. Register and create a new app")
        print("3. Copy the App ID")
        print("4. Or use the default App ID: 1089")
        print()
        
        current_app_id = os.getenv('DERIV_APP_ID', '1089')
        print(f"Current App ID: {current_app_id}")
        
        use_current = self.get_user_input("Use current App ID? (y/n)", "y", required=False)
        if use_current.lower() == 'y':
            self.config['DERIV_APP_ID'] = current_app_id
        else:
            app_id = self.get_user_input("Enter your Deriv App ID", current_app_id)
            self.config['DERIV_APP_ID'] = app_id
        
        print("✅ Deriv App ID saved")
        print()
    
    def setup_deriv_api_token(self):
        """Setup Deriv API token"""
        print("🔐 Deriv API Token Setup")
        print("-" * 30)
        print("To get your Deriv API Token:")
        print("1. Go to https://app.deriv.com/")
        print("2. Login to your account")
        print("3. Go to Settings → API Token")
        print("4. Create a new token with 'Trading' permission")
        print("5. Copy the token")
        print()
        print("⚠️  IMPORTANT: This token allows trading on your account!")
        print("   Keep it secure and never share it with anyone.")
        print()
        
        current_token = os.getenv('DERIV_API_TOKEN', '')
        if current_token:
            print(f"Current token: {current_token[:10]}...{current_token[-10:]}")
            use_current = self.get_user_input("Use current token? (y/n)", "y", required=False)
            if use_current.lower() == 'y':
                self.config['DERIV_API_TOKEN'] = current_token
                print("✅ Deriv API Token saved")
                print()
                return
        
        skip_token = self.get_user_input("Skip API token setup? (y/n)", "n", required=False)
        if skip_token.lower() == 'y':
            print("⚠️  Skipping API token - some features will be limited")
            self.config['DERIV_API_TOKEN'] = ''
            print()
            return
        
        token = self.get_user_input("Enter your Deriv API Token", mask=True)
        if token.strip():
            self.config['DERIV_API_TOKEN'] = token
            print("✅ Deriv API Token saved")
        else:
            print("⚠️  No API token provided - some features will be limited")
            self.config['DERIV_API_TOKEN'] = ''
        
        print()
    
    def setup_trading_config(self):
        """Setup trading configuration"""
        print("📊 Trading Configuration")
        print("-" * 30)
        
        # Default lot size
        default_lot = os.getenv('DEFAULT_LOT_SIZE', '0.1')
        lot_size = self.get_user_input(f"Default lot size", default_lot, required=False)
        try:
            float(lot_size)
            self.config['DEFAULT_LOT_SIZE'] = lot_size
        except ValueError:
            print("❌ Invalid lot size, using default: 0.1")
            self.config['DEFAULT_LOT_SIZE'] = '0.1'
        
        # Max trades per hour
        max_trades = os.getenv('MAX_TRADES_PER_HOUR', '10')
        trades_per_hour = self.get_user_input(f"Max trades per hour", max_trades, required=False)
        try:
            int(trades_per_hour)
            self.config['MAX_TRADES_PER_HOUR'] = trades_per_hour
        except ValueError:
            print("❌ Invalid number, using default: 10")
            self.config['MAX_TRADES_PER_HOUR'] = '10'
        
        # Max daily loss
        max_loss = os.getenv('MAX_DAILY_LOSS', '100.0')
        daily_loss = self.get_user_input(f"Max daily loss limit", max_loss, required=False)
        try:
            float(daily_loss)
            self.config['MAX_DAILY_LOSS'] = daily_loss
        except ValueError:
            print("❌ Invalid amount, using default: 100.0")
            self.config['MAX_DAILY_LOSS'] = '100.0'
        
        # Max position size
        max_position = os.getenv('MAX_POSITION_SIZE', '10.0')
        position_size = self.get_user_input(f"Max position size", max_position, required=False)
        try:
            float(position_size)
            self.config['MAX_POSITION_SIZE'] = position_size
        except ValueError:
            print("❌ Invalid amount, using default: 10.0")
            self.config['MAX_POSITION_SIZE'] = '10.0'
        
        # Log level
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        level = self.get_user_input(f"Log level (DEBUG/INFO/WARNING/ERROR)", log_level, required=False)
        if level.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            self.config['LOG_LEVEL'] = level.upper()
        else:
            print("❌ Invalid log level, using default: INFO")
            self.config['LOG_LEVEL'] = 'INFO'
        
        print("✅ Trading configuration saved")
        print()
    
    async def test_deriv_connection(self):
        """Test Deriv API connection"""
        if not self.config.get('DERIV_API_TOKEN'):
            print("⚠️  No Deriv API token configured - skipping connection test")
            return True
        
        print("🧪 Testing Deriv API connection...")
        
        try:
            # Use app_id in URL
            app_id = self.config.get('DERIV_APP_ID', '1089')
            api_url = f"wss://ws.binaryws.com/websockets/v3?app_id={app_id}"
            
            async with websockets.connect(api_url) as websocket:
                # Test authorization
                auth_request = {
                    "authorize": self.config['DERIV_API_TOKEN'],
                    "req_id": 1
                }
                await websocket.send(json.dumps(auth_request))
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                response_data = json.loads(response)
                
                if "authorize" in response_data:
                    account_info = response_data["authorize"]
                    print(f"✅ Deriv API connection successful!")
                    print(f"   Account: {account_info.get('loginid', 'Unknown')}")
                    print(f"   Currency: {account_info.get('currency', 'Unknown')}")
                    return True
                elif "error" in response_data:
                    error = response_data["error"]
                    print(f"❌ Deriv API connection failed: {error.get('message', 'Unknown error')}")
                    return False
                    
        except asyncio.TimeoutError:
            print("❌ Deriv API connection timed out")
            return False
        except Exception as e:
            print(f"❌ Deriv API connection failed: {e}")
            return False
    
    def test_telegram_token(self):
        """Test Telegram bot token"""
        print("🧪 Testing Telegram Bot token...")
        
        try:
            import requests
            
            token = self.config['TELEGRAM_BOT_TOKEN']
            url = f"https://api.telegram.org/bot{token}/getMe"
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('ok'):
                bot_info = data['result']
                print(f"✅ Telegram Bot token is valid!")
                print(f"   Bot name: {bot_info.get('first_name', 'Unknown')}")
                print(f"   Username: @{bot_info.get('username', 'Unknown')}")
                return True
            else:
                print(f"❌ Telegram Bot token is invalid: {data.get('description', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram Bot token test failed: {e}")
            return False
    
    def save_config(self):
        """Save configuration to .env file"""
        print("💾 Saving configuration...")
        
        # Create .env file if it doesn't exist
        if not self.env_file.exists():
            self.env_file.touch()
        
        # Save each configuration value
        for key, value in self.config.items():
            set_key(str(self.env_file), key, value)
        
        print(f"✅ Configuration saved to {self.env_file}")
        print()
    
    def show_summary(self):
        """Show configuration summary"""
        print("📋 Configuration Summary")
        print("=" * 50)
        
        for key, value in self.config.items():
            if 'TOKEN' in key:
                display_value = f"{value[:10]}...{value[-10:]}" if value else "Not set"
            else:
                display_value = value
            print(f"{key}: {display_value}")
        
        print()
    
    def show_next_steps(self):
        """Show next steps after setup"""
        print("🎯 Next Steps")
        print("=" * 50)
        print("1. Run the bot:")
        print("   python telegram_bot.py")
        print()
        print("2. Test your configuration:")
        print("   python test_token.py")
        print("   python test_app_id.py")
        print()
        print("3. Start trading:")
        print("   Send /start to your bot on Telegram")
        print()
        print("4. Read the documentation:")
        print("   cat TRADING_STRATEGIES_GUIDE.md")
        print()
        print("🚀 Happy trading!")
    
    async def run_setup(self):
        """Run the complete setup wizard"""
        self.print_header()
        
        # Load existing environment
        load_dotenv()
        
        # Setup each component
        self.setup_telegram_token()
        self.setup_deriv_app_id()
        self.setup_deriv_api_token()
        self.setup_trading_config()
        
        # Show summary
        self.show_summary()
        
        # Confirm save
        save_config = self.get_user_input("Save this configuration? (y/n)", "y", required=False)
        if save_config.lower() != 'y':
            print("❌ Configuration not saved. Exiting.")
            return False
        
        # Save configuration
        self.save_config()
        
        # Test connections
        print("🧪 Testing configuration...")
        print()
        
        telegram_ok = self.test_telegram_token()
        deriv_ok = await self.test_deriv_connection()
        
        if telegram_ok and deriv_ok:
            print("\n🎉 Setup completed successfully!")
        else:
            print("\n⚠️  Setup completed with some issues.")
            print("   Please check your tokens and try again.")
        
        self.show_next_steps()
        return True

def main():
    """Main function"""
    try:
        wizard = TokenSetupWizard()
        asyncio.run(wizard.run_setup())
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
