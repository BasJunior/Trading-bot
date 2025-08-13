#!/usr/bin/env python3
"""
Verification script to check all files in the Deriv Telegram Bot project
"""

import os
import sys
from pathlib import Path

def check_file_status(file_path):
    """Check if a file exists and is not empty"""
    if not os.path.exists(file_path):
        return "❌ Missing"
    
    if os.path.getsize(file_path) == 0:
        return "⚠️  Empty"
    
    return "✅ OK"

def main():
    """Main verification function"""
    print("🔍 Deriv Telegram Bot - File Verification")
    print("=" * 50)
    
    # Define all project files
    files_to_check = [
        # Core files
        ("telegram_bot.py", "Main bot application"),
        ("config.py", "Configuration management"),
        ("user_management.py", "User session management"),
        ("requirements.txt", "Python dependencies"),
        
        # Setup and utility scripts
        ("setup.sh", "Environment setup script"),
        ("start_bot.sh", "Bot startup script"),
        ("setup_tokens.py", "Interactive token setup wizard"),
        
        # Test scripts
        ("test_bot.py", "Comprehensive bot tests"),
        ("test_token.py", "Deriv API token validation"),
        ("test_app_id.py", "Deriv App ID validation"),
        
        # Documentation
        ("README.md", "Main project documentation"),
        ("TRADING_STRATEGIES_GUIDE.md", "Trading strategies guide"),
        ("SETUP_GUIDE.md", "Setup instructions"),
        ("MULTI_ACCOUNT_GUIDE.md", "Multi-account management"),
        ("BOT_FIX_SUMMARY.md", "Recent fixes and improvements"),
        
        # Configuration
        (".env", "Environment variables"),
    ]
    
    print(f"{'File':<35} {'Status':<15} {'Description'}")
    print("-" * 80)
    
    all_ok = True
    for file_name, description in files_to_check:
        status = check_file_status(file_name)
        print(f"{file_name:<35} {status:<15} {description}")
        
        if "❌" in status or "⚠️" in status:
            all_ok = False
    
    print("-" * 80)
    
    if all_ok:
        print("🎉 All files are present and non-empty!")
    else:
        print("⚠️  Some files are missing or empty.")
    
    print("\n📋 Next Steps:")
    print("1. Run setup: ./setup.sh")
    print("2. Configure tokens: python3 setup_tokens.py")
    print("3. Test configuration: python3 test_app_id.py && python3 test_token.py")
    print("4. Start bot: ./start_bot.sh")
    print("\n📚 Documentation: cat README.md")

if __name__ == "__main__":
    main()
