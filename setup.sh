#!/bin/bash

# Deriv Telegram Bot Setup Script
# This script will set up the environment and install all dependencies

echo "🚀 Deriv Telegram Bot Setup Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python 3 is installed
check_python() {
    print_info "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python 3 found: $PYTHON_VERSION"
        return 0
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        return 1
    fi
}

# Check if pip is installed
check_pip() {
    print_info "Checking pip installation..."
    if command -v pip3 &> /dev/null; then
        print_status "pip3 found"
        return 0
    else
        print_error "pip3 is not installed. Please install pip3."
        return 1
    fi
}

# Install system dependencies (macOS)
install_system_deps() {
    print_info "Installing system dependencies..."
    
    # Check if we're on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # Check if Homebrew is installed
        if command -v brew &> /dev/null; then
            print_status "Homebrew found"
            
            # Install TA-Lib system dependency
            print_info "Installing TA-Lib system dependency..."
            brew install ta-lib
            
            if [ $? -eq 0 ]; then
                print_status "TA-Lib installed successfully"
            else
                print_warning "TA-Lib installation may have failed, continuing..."
            fi
        else
            print_warning "Homebrew not found. Please install Homebrew first:"
            print_info "Visit: https://brew.sh/"
            print_info "Or run: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        fi
    else
        print_info "Non-macOS system detected. Please install TA-Lib manually."
        print_info "Ubuntu/Debian: sudo apt-get install libta-lib-dev"
        print_info "CentOS/RHEL: sudo yum install ta-lib-devel"
    fi
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    # Upgrade pip first
    print_info "Upgrading pip..."
    python3 -m pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        print_info "Installing packages from requirements.txt..."
        pip3 install -r requirements.txt
        
        if [ $? -eq 0 ]; then
            print_status "All Python dependencies installed successfully"
        else
            print_error "Failed to install some Python dependencies"
            return 1
        fi
    else
        print_error "requirements.txt not found!"
        return 1
    fi
}

# Create virtual environment (optional)
create_venv() {
    print_info "Creating virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
        
        print_info "To activate virtual environment, run:"
        print_info "source venv/bin/activate"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Check configuration files
check_config() {
    print_info "Checking configuration files..."
    
    # Check .env file
    if [ -f ".env" ]; then
        print_status ".env file found"
        
        # Check if tokens are configured
        if grep -q "your_telegram_bot_token_here" .env; then
            print_warning "Telegram bot token not configured in .env file"
            print_info "Please update TELEGRAM_BOT_TOKEN in .env file"
        else
            print_status "Telegram bot token configured"
        fi
        
        if grep -q "your_deriv_api_token_here" .env; then
            print_warning "Deriv API token not configured in .env file"
            print_info "Please update DERIV_API_TOKEN in .env file"
        else
            print_status "Deriv API token configured"
        fi
    else
        print_error ".env file not found!"
        return 1
    fi
    
    # Check config.py
    if [ -f "config.py" ]; then
        print_status "config.py file found"
    else
        print_error "config.py file not found!"
        return 1
    fi
}

# Test the bot
test_bot() {
    print_info "Testing bot configuration..."
    
    if [ -f "test_bot.py" ]; then
        python3 test_bot.py
        
        if [ $? -eq 0 ]; then
            print_status "Bot test passed successfully"
        else
            print_error "Bot test failed"
            return 1
        fi
    else
        print_warning "test_bot.py not found, skipping test"
    fi
}

# Create startup script
create_startup_script() {
    print_info "Creating startup script..."
    
    cat > start_bot.sh << 'EOF'
#!/bin/bash

# Start Deriv Telegram Bot
echo "🚀 Starting Deriv Telegram Bot..."

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your tokens"
    exit 1
fi

# Start the bot
echo "Starting bot..."
python3 telegram_bot.py
EOF

    chmod +x start_bot.sh
    print_status "Startup script created: start_bot.sh"
}

# Main setup function
main() {
    echo ""
    print_info "Starting setup process..."
    echo ""
    
    # Check prerequisites
    if ! check_python; then
        exit 1
    fi
    
    if ! check_pip; then
        exit 1
    fi
    
    # Install system dependencies
    install_system_deps
    
    # Create virtual environment (optional)
    read -p "Do you want to create a virtual environment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_venv
        print_info "To use virtual environment, run: source venv/bin/activate"
    fi
    
    # Install Python dependencies
    if ! install_python_deps; then
        exit 1
    fi
    
    # Check configuration
    if ! check_config; then
        exit 1
    fi
    
    # Test the bot
    test_bot
    
    # Create startup script
    create_startup_script
    
    echo ""
    print_status "Setup completed successfully!"
    echo ""
    print_info "📋 Next steps:"
    echo "1. Make sure your tokens are configured in .env file"
    echo "2. Run the bot with: python3 telegram_bot.py"
    echo "3. Or use the startup script: ./start_bot.sh"
    echo ""
    print_info "🎯 Your bot features:"
    echo "• Interactive button interface"
    echo "• Automated trading strategies"
    echo "• Multi-market support"
    echo "• Real-time monitoring"
    echo "• Custom lot sizes"
    echo ""
    print_status "Happy trading! 🚀"
}

# Run main function
main "$@"
