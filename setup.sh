#!/bin/bash
# Love Notes Setup Script for Orange Pi Zero 2
# Run this script once after cloning the repository

set -e

echo "==================================="
echo "  Love Notes Setup Script"
echo "==================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please run this script as a regular user (not root)"
    echo "The script will use sudo when needed"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "[1/6] Updating package lists..."
sudo apt-get update

echo ""
echo "[2/6] Installing system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-pygame \
    python3-venv \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev

echo ""
echo "[3/6] Creating default files..."

# Create message.txt if it doesn't exist
if [ ! -f "$SCRIPT_DIR/message.txt" ]; then
    echo "I love you!" > "$SCRIPT_DIR/message.txt"
    echo "Created default message.txt"
fi

# Create config.json if it doesn't exist
if [ ! -f "$SCRIPT_DIR/config.json" ]; then
    cat > "$SCRIPT_DIR/config.json" << 'EOF'
{
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "email_address": "your-email@gmail.com",
    "email_password": "your-app-password",
    "allowed_sender": "sender@example.com",
    "poll_interval": 60,
    "mark_as_read": true
}
EOF
    echo "Created default config.json - PLEASE EDIT THIS FILE!"
fi

echo ""
echo "[4/6] Setting up systemd services..."

# Update service files with correct paths
INSTALL_PATH="/home/$(whoami)/lovenotes"

# Copy and configure display service
sudo cp "$SCRIPT_DIR/lovenotes-display.service" /etc/systemd/system/
sudo sed -i "s|/home/pi/lovenotes|$INSTALL_PATH|g" /etc/systemd/system/lovenotes-display.service
sudo sed -i "s|User=pi|User=$(whoami)|g" /etc/systemd/system/lovenotes-display.service

# Copy and configure email service
sudo cp "$SCRIPT_DIR/lovenotes-email.service" /etc/systemd/system/
sudo sed -i "s|/home/pi/lovenotes|$INSTALL_PATH|g" /etc/systemd/system/lovenotes-email.service
sudo sed -i "s|User=pi|User=$(whoami)|g" /etc/systemd/system/lovenotes-email.service

echo ""
echo "[5/6] Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable lovenotes-display.service
sudo systemctl enable lovenotes-email.service

echo ""
echo "[6/6] Configuring display settings..."

# Disable screen blanking (optional)
if command -v xset &> /dev/null; then
    echo "Disabling screen blanking..."
    xset s off 2>/dev/null || true
    xset -dpms 2>/dev/null || true
    xset s noblank 2>/dev/null || true
fi

# Add to ~/.xinitrc if it exists
if [ -f ~/.xinitrc ]; then
    if ! grep -q "xset s off" ~/.xinitrc; then
        echo "xset s off" >> ~/.xinitrc
        echo "xset -dpms" >> ~/.xinitrc
        echo "xset s noblank" >> ~/.xinitrc
    fi
fi

echo ""
echo "==================================="
echo "  Setup Complete!"
echo "==================================="
echo ""
echo "IMPORTANT: Before starting the services, edit config.json with your email settings:"
echo "  nano $SCRIPT_DIR/config.json"
echo ""
echo "For Gmail, you'll need to:"
echo "  1. Enable 2-Factor Authentication"
echo "  2. Create an App Password at https://myaccount.google.com/apppasswords"
echo "  3. Use the App Password (not your regular password) in config.json"
echo ""
echo "To start the services now:"
echo "  sudo systemctl start lovenotes-display"
echo "  sudo systemctl start lovenotes-email"
echo ""
echo "To check service status:"
echo "  sudo systemctl status lovenotes-display"
echo "  sudo systemctl status lovenotes-email"
echo ""
echo "To view logs:"
echo "  journalctl -u lovenotes-display -f"
echo "  journalctl -u lovenotes-email -f"
echo ""
