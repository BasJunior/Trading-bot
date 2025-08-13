#!/bin/bash
# Deriv Telegram Bot - Production Deployment Script

set -e

echo "🚀 PRODUCTION DEPLOYMENT - DERIV TELEGRAM BOT"
echo "=============================================="

# Configuration
APP_NAME="deriv-telegram-bot"
SERVICE_USER="bot"
INSTALL_DIR="/opt/$APP_NAME"
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Create service user
create_service_user() {
    if id "$SERVICE_USER" &>/dev/null; then
        print_status "Service user '$SERVICE_USER' already exists"
    else
        useradd -r -s /bin/false -d $INSTALL_DIR $SERVICE_USER
        print_status "Created service user '$SERVICE_USER'"
    fi
}

# Create installation directory
create_install_dir() {
    mkdir -p $INSTALL_DIR
    chown $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
    print_status "Created installation directory: $INSTALL_DIR"
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Update package lists
    apt-get update
    
    # Install Python and other dependencies
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        git \
        curl \
        supervisor \
        nginx \
        certbot \
        python3-certbot-nginx
    
    print_status "System dependencies installed"
}

# Deploy application
deploy_app() {
    print_status "Deploying application..."
    
    # Copy application files
    cp -r . $INSTALL_DIR/
    chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
    
    # Create virtual environment
    sudo -u $SERVICE_USER python3 -m venv $INSTALL_DIR/.venv
    
    # Install Python dependencies
    sudo -u $SERVICE_USER $INSTALL_DIR/.venv/bin/pip install --upgrade pip
    sudo -u $SERVICE_USER $INSTALL_DIR/.venv/bin/pip install -r $INSTALL_DIR/requirements.txt
    
    # Install MT5 dependencies if requested
    if [[ "$1" == "--with-mt5" ]]; then
        sudo -u $SERVICE_USER $INSTALL_DIR/.venv/bin/pip install -r $INSTALL_DIR/requirements_mt5.txt
        print_status "MT5 dependencies installed"
    fi
    
    print_status "Application deployed"
}

# Configure environment
configure_environment() {
    print_status "Configuring environment..."
    
    # Copy environment template if .env doesn't exist
    if [[ ! -f $INSTALL_DIR/.env ]]; then
        cp $INSTALL_DIR/.env.example $INSTALL_DIR/.env
        chown $SERVICE_USER:$SERVICE_USER $INSTALL_DIR/.env
        chmod 600 $INSTALL_DIR/.env
        
        print_warning "Please edit $INSTALL_DIR/.env with your actual tokens"
        print_warning "Then restart the service: systemctl restart $APP_NAME"
    fi
    
    print_status "Environment configured"
}

# Create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    cat > $SERVICE_FILE << EOF
[Unit]
Description=Deriv Telegram Trading Bot
After=network.target
Requires=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/.venv/bin
ExecStart=$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/telegram_bot.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=$APP_NAME

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_DIR

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable $APP_NAME
    
    print_status "Systemd service created and enabled"
}

# Configure logging
configure_logging() {
    print_status "Configuring logging..."
    
    # Create log directory
    mkdir -p /var/log/$APP_NAME
    chown $SERVICE_USER:$SERVICE_USER /var/log/$APP_NAME
    
    # Configure logrotate
    cat > /etc/logrotate.d/$APP_NAME << EOF
/var/log/$APP_NAME/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su $SERVICE_USER $SERVICE_USER
}
EOF
    
    print_status "Logging configured"
}

# Configure firewall
configure_firewall() {
    if command -v ufw &> /dev/null; then
        print_status "Configuring firewall..."
        
        # Allow SSH, HTTP, HTTPS
        ufw allow ssh
        ufw allow http
        ufw allow https
        
        # Enable firewall if not already enabled
        ufw --force enable
        
        print_status "Firewall configured"
    else
        print_warning "UFW not found, skipping firewall configuration"
    fi
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create monitoring script
    cat > $INSTALL_DIR/monitor.sh << 'EOF'
#!/bin/bash
# Bot monitoring script

LOG_FILE="/var/log/deriv-telegram-bot/monitor.log"
SERVICE_NAME="deriv-telegram-bot"

# Check if service is running
if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "$(date): Service $SERVICE_NAME is not running, attempting restart" >> $LOG_FILE
    systemctl restart $SERVICE_NAME
    
    # Send notification (customize as needed)
    echo "Bot service restarted at $(date)" | logger -t bot-monitor
fi

# Check disk space
DISK_USAGE=$(df /opt | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "$(date): High disk usage: $DISK_USAGE%" >> $LOG_FILE
    echo "High disk usage: $DISK_USAGE%" | logger -t bot-monitor
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
if (( $(echo "$MEMORY_USAGE > 90" | bc -l) )); then
    echo "$(date): High memory usage: $MEMORY_USAGE%" >> $LOG_FILE
    echo "High memory usage: $MEMORY_USAGE%" | logger -t bot-monitor
fi
EOF

    chmod +x $INSTALL_DIR/monitor.sh
    chown $SERVICE_USER:$SERVICE_USER $INSTALL_DIR/monitor.sh
    
    # Add to cron
    echo "*/5 * * * * $SERVICE_USER $INSTALL_DIR/monitor.sh" >> /etc/crontab
    
    print_status "Monitoring configured"
}

# Start services
start_services() {
    print_status "Starting services..."
    
    # Start and check service
    systemctl start $APP_NAME
    sleep 5
    
    if systemctl is-active --quiet $APP_NAME; then
        print_status "Service started successfully"
    else
        print_error "Service failed to start"
        print_error "Check logs: journalctl -u $APP_NAME -f"
        exit 1
    fi
}

# Print final instructions
print_instructions() {
    echo ""
    echo "=============================================="
    echo "🎉 DEPLOYMENT COMPLETE!"
    echo "=============================================="
    echo ""
    echo "📋 SERVICE MANAGEMENT:"
    echo "• Start:   systemctl start $APP_NAME"
    echo "• Stop:    systemctl stop $APP_NAME"
    echo "• Restart: systemctl restart $APP_NAME"
    echo "• Status:  systemctl status $APP_NAME"
    echo "• Logs:    journalctl -u $APP_NAME -f"
    echo ""
    echo "📁 FILE LOCATIONS:"
    echo "• App:     $INSTALL_DIR"
    echo "• Config:  $INSTALL_DIR/.env"
    echo "• Logs:    /var/log/$APP_NAME/"
    echo "• Service: $SERVICE_FILE"
    echo ""
    echo "⚙️ CONFIGURATION:"
    echo "• Edit $INSTALL_DIR/.env with your tokens"
    echo "• Restart service after configuration changes"
    echo "• Monitor logs for any issues"
    echo ""
    echo "🔧 MONITORING:"
    echo "• Service health: systemctl status $APP_NAME"
    echo "• Application logs: tail -f /var/log/$APP_NAME/bot.log"
    echo "• System logs: journalctl -u $APP_NAME"
    echo ""
    echo "🔒 SECURITY:"
    echo "• Service runs as user: $SERVICE_USER"
    echo "• Firewall configured for HTTP/HTTPS/SSH"
    echo "• Log rotation configured"
    echo ""
    print_warning "IMPORTANT: Configure your tokens in $INSTALL_DIR/.env"
    print_warning "Then restart: systemctl restart $APP_NAME"
}

# Main deployment function
main() {
    echo "Starting production deployment..."
    
    check_root
    create_service_user
    create_install_dir
    install_system_deps
    deploy_app "$@"
    configure_environment
    create_systemd_service
    configure_logging
    configure_firewall
    setup_monitoring
    start_services
    print_instructions
}

# Handle command line arguments
case "$1" in
    --help|-h)
        echo "Usage: $0 [--with-mt5]"
        echo "  --with-mt5    Install MT5 CFD trading dependencies"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
