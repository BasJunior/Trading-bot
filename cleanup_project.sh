#!/bin/bash

echo "🧹 Cleaning up Deriv Telegram Bot project..."

# Create backup directory first
mkdir -p backup_files

# Move unnecessary files to backup
echo "📦 Moving test files to backup..."
mv test_*.py backup_files/ 2>/dev/null
mv comprehensive_test.py backup_files/ 2>/dev/null
mv debug_bot.py backup_files/ 2>/dev/null
mv minimal_bot_test.py backup_files/ 2>/dev/null
mv fresh_test.py backup_files/ 2>/dev/null
mv final_validation.py backup_files/ 2>/dev/null
mv verify_project.py backup_files/ 2>/dev/null
mv check_bot_status.py backup_files/ 2>/dev/null

echo "🗑️ Moving backup/duplicate files to backup..."
mv telegram_bot.py.corrupted backup_files/ 2>/dev/null
mv telegram_bot_backup.py backup_files/ 2>/dev/null
mv temp_bot.py backup_files/ 2>/dev/null
mv .env_backup backup_files/ 2>/dev/null
mv .env_new backup_files/ 2>/dev/null

echo "📄 Moving extra documentation to backup..."
mv BOT_FIX_SUMMARY.md backup_files/ 2>/dev/null
mv COMPLETION_REPORT.md backup_files/ 2>/dev/null
mv PROJECT_COMPLETION_SUMMARY.md backup_files/ 2>/dev/null
mv MANUAL_TRADING_FEATURES.md backup_files/ 2>/dev/null
mv MULTI_ACCOUNT_GUIDE.md backup_files/ 2>/dev/null
mv TRADING_STRATEGIES_GUIDE.md backup_files/ 2>/dev/null

echo "🔄 Removing duplicate virtual environment..."
if [ -d ".venv" ] && [ -d "venv" ]; then
    echo "Found both .venv and venv directories. Keeping .venv, moving venv to backup..."
    mv venv backup_files/ 2>/dev/null
fi

echo "📋 Current project structure after cleanup:"
ls -la

echo "✅ Cleanup complete! Backed up files are in backup_files/ directory"
echo "💡 You can delete backup_files/ directory if you don't need those files"
