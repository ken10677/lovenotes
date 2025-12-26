#!/usr/bin/env python3
"""
Love Notes Display
Displays messages from message.txt on a fullscreen black background.
Includes subtle position drift to prevent screen burn-in.
"""

import pygame
import os
import sys
import time
import random
from pathlib import Path

# Configuration
MESSAGE_FILE = Path(__file__).parent / "message.txt"
FONT_SIZE = 72
DRIFT_INTERVAL = 180  # seconds between position changes (3 minutes)
MAX_DRIFT = 30  # maximum pixels to drift from center
CHECK_INTERVAL = 1  # seconds between file checks

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class LoveNotesDisplay:
    def __init__(self):
        pygame.init()

        # Get display info and set up fullscreen
        display_info = pygame.display.Info()
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h

        # Create fullscreen display
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.FULLSCREEN | pygame.NOFRAME
        )
        pygame.display.set_caption("Love Notes")
        pygame.mouse.set_visible(False)

        # Initialize font
        pygame.font.init()
        self.font = pygame.font.Font(None, FONT_SIZE)

        # State
        self.message = ""
        self.last_modified = 0
        self.drift_x = 0
        self.drift_y = 0
        self.last_drift_time = time.time()

        # Load initial message
        self.load_message()

    def load_message(self):
        """Load message from file if it has changed."""
        try:
            if MESSAGE_FILE.exists():
                mtime = MESSAGE_FILE.stat().st_mtime
                if mtime != self.last_modified:
                    self.message = MESSAGE_FILE.read_text(encoding='utf-8').strip()
                    self.last_modified = mtime
                    return True
        except Exception as e:
            print(f"Error reading message file: {e}", file=sys.stderr)
        return False

    def update_drift(self):
        """Update text position drift for screensaver effect."""
        current_time = time.time()
        if current_time - self.last_drift_time >= DRIFT_INTERVAL:
            self.drift_x = random.randint(-MAX_DRIFT, MAX_DRIFT)
            self.drift_y = random.randint(-MAX_DRIFT, MAX_DRIFT)
            self.last_drift_time = current_time

    def wrap_text(self, text, max_width):
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font.render(test_line, True, WHITE)

            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else ['']

    def render(self):
        """Render the current message to screen."""
        self.screen.fill(BLACK)

        if not self.message:
            return

        # Wrap text with padding
        max_width = self.screen_width - 100
        lines = self.wrap_text(self.message, max_width)

        # Calculate total height
        line_height = self.font.get_linesize()
        total_height = len(lines) * line_height

        # Calculate starting Y position (centered with drift)
        center_x = self.screen_width // 2 + self.drift_x
        start_y = (self.screen_height - total_height) // 2 + self.drift_y

        # Render each line
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(
                center=(center_x, start_y + i * line_height + line_height // 2)
            )
            self.screen.blit(text_surface, text_rect)

        pygame.display.flip()

    def run(self):
        """Main loop."""
        clock = pygame.time.Clock()
        last_check = 0

        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_q:
                        return

            # Check for file changes periodically
            current_time = time.time()
            if current_time - last_check >= CHECK_INTERVAL:
                self.load_message()
                last_check = current_time

            # Update screensaver drift
            self.update_drift()

            # Render
            self.render()

            # Cap at 30 FPS to save CPU
            clock.tick(30)

    def cleanup(self):
        """Clean up pygame."""
        pygame.quit()


def main():
    display = LoveNotesDisplay()
    try:
        display.run()
    except KeyboardInterrupt:
        pass
    finally:
        display.cleanup()


if __name__ == "__main__":
    main()
