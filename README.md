# Love Notes Display

A simple love-note display system for Orange Pi Zero 2 with a 7" HDMI screen. Send emails to update the displayed message remotely.

## Features

- **Fullscreen Display**: White text centered on black background
- **Email Integration**: Update the message by sending an email
- **Screensaver**: Subtle text position drift prevents screen burn-in
- **Auto-start**: Services start automatically on boot
- **Easy Updates**: Git pull + deploy script to update

## Hardware Requirements

- Orange Pi Zero 2 (or similar SBC)
- 7" HDMI display
- MicroSD card with Armbian or similar Linux distro
- Network connection (WiFi or Ethernet)

## Quick Start

### 1. Clone the Repository

```bash
cd ~
git clone <your-repo-url> lovenotes
cd lovenotes
```

### 2. Run Setup

```bash
chmod +x setup.sh deploy.sh
./setup.sh
```

### 3. Configure Email

Edit `config.json` with your email settings:

```bash
nano config.json
```

```json
{
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "email_address": "your-email@gmail.com",
    "email_password": "your-app-password",
    "allowed_sender": "partner@example.com",
    "poll_interval": 60,
    "mark_as_read": true
}
```

### 4. Start Services

```bash
sudo systemctl start lovenotes-display
sudo systemctl start lovenotes-email
```

## Gmail Setup

If using Gmail, you need to create an App Password:

1. Go to your Google Account settings
2. Enable 2-Factor Authentication if not already enabled
3. Go to Security > App passwords (https://myaccount.google.com/apppasswords)
4. Create a new app password for "Mail"
5. Use this 16-character password in `config.json`

## Configuration

### config.json

| Field | Description |
|-------|-------------|
| `imap_server` | IMAP server address |
| `imap_port` | IMAP port (usually 993 for SSL) |
| `email_address` | Your email address to check |
| `email_password` | App password (not your regular password) |
| `allowed_sender` | Only process emails from this address |
| `poll_interval` | Seconds between email checks |
| `mark_as_read` | Mark processed emails as read |

### message.txt

You can also update the display manually by editing `message.txt`:

```bash
echo "New message here" > ~/lovenotes/message.txt
```

The display updates automatically when the file changes.

## Usage

### Sending a Love Note

1. Compose an email to the configured `email_address`
2. Use the message you want to display as the **subject line**
3. Send from the `allowed_sender` address
4. The display updates within `poll_interval` seconds

### Manual Message Update

```bash
echo "I love you more than coffee!" > ~/lovenotes/message.txt
```

## Service Management

```bash
# Check status
sudo systemctl status lovenotes-display
sudo systemctl status lovenotes-email

# View logs
journalctl -u lovenotes-display -f
journalctl -u lovenotes-email -f

# Restart services
sudo systemctl restart lovenotes-display
sudo systemctl restart lovenotes-email

# Stop services
sudo systemctl stop lovenotes-display
sudo systemctl stop lovenotes-email
```

## Updating

After making changes or pulling updates:

```bash
cd ~/lovenotes
git pull
./deploy.sh
```

## Display Controls

- Press `ESC` or `Q` to exit the display (if running manually)
- The display auto-restarts if it crashes

## Customization

### Font Size

Edit `display.py` and change `FONT_SIZE`:

```python
FONT_SIZE = 72  # Increase for larger text
```

### Drift Settings

```python
DRIFT_INTERVAL = 180  # Seconds between position changes
MAX_DRIFT = 30        # Maximum pixels to drift
```

### Poll Interval

Edit `config.json`:

```json
"poll_interval": 30  # Check every 30 seconds
```

## Troubleshooting

### Display not showing

```bash
# Check if X is running
echo $DISPLAY

# Try setting display manually
export DISPLAY=:0
python3 display.py
```

### Email not working

```bash
# Check logs
journalctl -u lovenotes-email -f

# Test manually
python3 email_poller.py
```

### Permission issues

```bash
# Ensure scripts are executable
chmod +x setup.sh deploy.sh

# Check file ownership
ls -la ~/lovenotes/
```

## File Structure

```
lovenotes/
├── display.py              # Main display application
├── email_poller.py         # Email checking service
├── config.json             # Email configuration (create from template)
├── message.txt             # Current message to display
├── lovenotes-display.service   # Systemd service for display
├── lovenotes-email.service     # Systemd service for email
├── setup.sh                # Initial setup script
├── deploy.sh               # Update/restart script
└── README.md               # This file
```

## License

MIT License - Use freely for your loved ones!
