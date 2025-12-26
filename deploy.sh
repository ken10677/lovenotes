#!/bin/bash
# Love Notes Deploy Script
# Run this after git pull to restart services with updated code

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==================================="
echo "  Love Notes Deploy"
echo "==================================="

echo ""
echo "Restarting services..."

# Reload systemd in case service files changed
sudo systemctl daemon-reload

# Restart both services
echo "Restarting lovenotes-display..."
sudo systemctl restart lovenotes-display || echo "Display service not running, starting..."
sudo systemctl start lovenotes-display 2>/dev/null || true

echo "Restarting lovenotes-email..."
sudo systemctl restart lovenotes-email || echo "Email service not running, starting..."
sudo systemctl start lovenotes-email 2>/dev/null || true

echo ""
echo "Checking service status..."
echo ""
echo "Display service:"
sudo systemctl status lovenotes-display --no-pager -l | head -10

echo ""
echo "Email service:"
sudo systemctl status lovenotes-email --no-pager -l | head -10

echo ""
echo "==================================="
echo "  Deploy Complete!"
echo "==================================="
