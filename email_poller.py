#!/usr/bin/env python3
"""
Email Poller for Love Notes
Polls an IMAP inbox for new emails from a specific sender.
Writes the subject line to message.txt when a new email arrives.
"""

import imaplib
import email
from email.header import decode_header
import time
import sys
import json
from pathlib import Path

# Configuration file path
CONFIG_FILE = Path(__file__).parent / "config.json"
MESSAGE_FILE = Path(__file__).parent / "message.txt"

# Default configuration
DEFAULT_CONFIG = {
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "email_address": "your-email@gmail.com",
    "email_password": "your-app-password",
    "allowed_sender": "sender@example.com",
    "poll_interval": 60,  # seconds
    "mark_as_read": True
}


def load_config():
    """Load configuration from JSON file."""
    if not CONFIG_FILE.exists():
        # Create default config file
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        print(f"Created default config at {CONFIG_FILE}")
        print("Please edit the config file with your email credentials.")
        sys.exit(1)

    return json.loads(CONFIG_FILE.read_text())


def decode_mime_header(header_value):
    """Decode MIME encoded header to string."""
    if header_value is None:
        return ""

    decoded_parts = decode_header(header_value)
    result = []

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or 'utf-8', errors='replace'))
        else:
            result.append(part)

    return ''.join(result)


def get_sender_email(from_header):
    """Extract email address from From header."""
    # Handle format: "Name <email@example.com>"
    if '<' in from_header and '>' in from_header:
        start = from_header.index('<') + 1
        end = from_header.index('>')
        return from_header[start:end].lower()
    return from_header.lower().strip()


class EmailPoller:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.last_seen_uid = self.load_last_uid()

    def load_last_uid(self):
        """Load the last seen email UID from file."""
        uid_file = Path(__file__).parent / ".last_uid"
        if uid_file.exists():
            try:
                return int(uid_file.read_text().strip())
            except ValueError:
                pass
        return 0

    def save_last_uid(self, uid):
        """Save the last seen email UID to file."""
        uid_file = Path(__file__).parent / ".last_uid"
        uid_file.write_text(str(uid))
        self.last_seen_uid = uid

    def connect(self):
        """Connect to IMAP server."""
        try:
            self.connection = imaplib.IMAP4_SSL(
                self.config["imap_server"],
                self.config["imap_port"]
            )
            self.connection.login(
                self.config["email_address"],
                self.config["email_password"]
            )
            return True
        except Exception as e:
            print(f"Connection error: {e}", file=sys.stderr)
            self.connection = None
            return False

    def disconnect(self):
        """Disconnect from IMAP server."""
        if self.connection:
            try:
                self.connection.logout()
            except:
                pass
            self.connection = None

    def check_for_new_emails(self):
        """Check for new emails from the allowed sender."""
        if not self.connection:
            if not self.connect():
                return None

        try:
            # Select inbox
            self.connection.select("INBOX")

            # Search for unseen emails
            status, messages = self.connection.search(None, "UNSEEN")
            if status != "OK":
                return None

            email_ids = messages[0].split()
            if not email_ids:
                return None

            allowed_sender = self.config["allowed_sender"].lower()

            # Check each unseen email
            for email_id in reversed(email_ids):  # Most recent first
                # Fetch email
                status, msg_data = self.connection.fetch(email_id, "(RFC822 UID)")
                if status != "OK":
                    continue

                # Parse UID from response
                uid = None
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        # Try to extract UID from the response
                        response_str = response_part[0].decode() if isinstance(response_part[0], bytes) else str(response_part[0])
                        if 'UID' in response_str:
                            import re
                            uid_match = re.search(r'UID (\d+)', response_str)
                            if uid_match:
                                uid = int(uid_match.group(1))

                # Parse email
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Check sender
                        from_header = decode_mime_header(msg["From"])
                        sender_email = get_sender_email(from_header)

                        if allowed_sender in sender_email or sender_email in allowed_sender:
                            subject = decode_mime_header(msg["Subject"])

                            # Mark as read if configured
                            if self.config.get("mark_as_read", True):
                                self.connection.store(email_id, '+FLAGS', '\\Seen')

                            # Save UID if we got it
                            if uid:
                                self.save_last_uid(uid)

                            return subject

            return None

        except imaplib.IMAP4.abort:
            print("Connection aborted, reconnecting...", file=sys.stderr)
            self.disconnect()
            return None
        except Exception as e:
            print(f"Error checking emails: {e}", file=sys.stderr)
            return None

    def write_message(self, message):
        """Write message to the message file."""
        try:
            MESSAGE_FILE.write_text(message, encoding='utf-8')
            print(f"Updated message: {message}")
            return True
        except Exception as e:
            print(f"Error writing message: {e}", file=sys.stderr)
            return False

    def run(self):
        """Main polling loop."""
        print(f"Starting email poller...")
        print(f"Checking {self.config['email_address']} for emails from {self.config['allowed_sender']}")
        print(f"Poll interval: {self.config['poll_interval']} seconds")

        while True:
            try:
                subject = self.check_for_new_emails()
                if subject:
                    self.write_message(subject)

                time.sleep(self.config["poll_interval"])

            except KeyboardInterrupt:
                print("\nShutting down...")
                break
            except Exception as e:
                print(f"Unexpected error: {e}", file=sys.stderr)
                time.sleep(self.config["poll_interval"])

        self.disconnect()


def main():
    config = load_config()
    poller = EmailPoller(config)
    poller.run()


if __name__ == "__main__":
    main()
