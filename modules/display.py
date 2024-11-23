# File: modules/display.py

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont
import threading
from datetime import datetime
from modules.logger import logger, LogType

class LargeDigits:
    def __init__(self):
        self.digits = {
            '0': [
                "  XXXXXX  ",
                " XXXXXXXX ",
                "XXXXXXXXXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXX    XXX",
                "XXXXXXXXXX",
                " XXXXXXXX ",
                "  XXXXXX  "
            ],
            '1': [
                "    XXX   ",
                "   XXXX   ",
                "  XXXXX   ",
                " XXXXXX   ",
                "XXXXXXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "    XXX   ",
                "XXXXXXXXX ",
                "XXXXXXXXX ",
                "XXXXXXXXX "
            ],
            # Add patterns for 2-9 similarly
        }
        
        self.small_one = [
            "  XX  ",
            " XXX  ",
            "XXXX  ",
            "  XX  ",
            "  XX  ",
            "  XX  ",
            "XXXXXX",
            "XXXXXX"
        ]

    def draw_digit(self, draw, digit, x_offset, y_offset, color, pixel_size=2):
        """Draw a single large digit at specified position"""
        pattern = self.digits[str(digit)]
        
        for y, row in enumerate(pattern):
            for x, cell in enumerate(row):
                if cell == 'X':
                    draw.rectangle(
                        [
                            x_offset + (x * pixel_size),
                            y_offset + (y * pixel_size),
                            x_offset + (x * pixel_size) + pixel_size - 1,
                            y_offset + (y * pixel_size) + pixel_size - 1
                        ],
                        fill=color
                    )

    def draw_small_one(self, draw, color):
        """Draw small "1" in top-right corner"""
        pixel_size = 1
        x_offset = 24
        y_offset = 0
        
        for y, row in enumerate(self.small_one):
            for x, cell in enumerate(row):
                if cell == 'X':
                    draw.rectangle(
                        [
                            x_offset + (x * pixel_size),
                            y_offset + (y * pixel_size),
                            x_offset + (x * pixel_size) + pixel_size - 1,
                            y_offset + (y * pixel_size) + pixel_size - 1
                        ],
                        fill=color
                    )

class ScoreBoard:
    def __init__(self):
        # Initialize display options
        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.cols = 64
        self.options.chain_length = 4
        self.options.parallel = 1
        self.options.hardware_mapping = 'adafruit-hat'
        self.options.gpio_slowdown = 2
        self.options.pwm_bits = 11
        self.options.pwm_lsb_nanoseconds = 130
        
        # Initialize matrix
        self.matrix = RGBMatrix(options=self.options)
        self.double_buffer = self.matrix.CreateFrameCanvas()
        
        # Game state
        self.scores = {"home": 0, "away": 0}
        self.game_time = 0
        self.display_mode = 'timer'
        self.scroll_text = ""
        self.show_time = False
        self.display_enabled = True
        self.brightness = 100
        self.timer_paused = False
        self.two_min_warning = False
        self.warning_triggered = False
        
        # Display settings
        self.colors = {
            'home': (0, 255, 0),
            'away': (0, 255, 0),
            'timer': (255, 255, 0),
            'text': (0, 255, 255)
        }
        
        # Initialize components
        self.large_digits = LargeDigits()
        
        # Start display thread
        self.running = True
        self.display_thread = threading.Thread(target=self._update_display)
        self.display_thread.start()
        
        # Log initialization
        logger.log(LogType.SYSTEM, "scoreboard_init")

    def set_score(self, team, value, user=None):
        """Set score for specified team"""
        if team in self.scores:
            old_value = self.scores[team]
            self.scores[team] = max(0, min(19, value))
            logger.log(
                LogType.GAME,
                "score_update",
                {
                    "team": team,
                    "old_value": old_value,
                    "new_value": self.scores[team]
                },
                user
            )

    def set_game_time(self, minutes):
        """Set game timer"""
        self.game_time = max(0, minutes * 60)
        self.warning_triggered = False
        logger.log(
            LogType.GAME,
            "timer_set",
            {"minutes": minutes}
        )

    def check_two_min_warning(self):
        """Check for 2-minute warning condition"""
        if not self.warning_triggered and self.game_time <= 120 and self.game_time > 119:
            self.warning_triggered = True
            self.timer_paused = True
            self.two_min_warning = True
            logger.log(LogType.GAME, "two_minute_warning")
            return True
        return False

    def resume_timer(self):
        """Resume timer after warning"""
        self.timer_paused = False
        self.two_min_warning = False
        logger.log(LogType.GAME, "timer_resumed")

    def set_display_mode(self, mode):
        """Switch between timer and text display"""
        if mode in ['timer', 'text']:
            self.display_mode = mode
            logger.log(
                LogType.SYSTEM,
                "display_mode_changed",
                {"mode": mode}
            )

    def set_brightness(self, level):
        """Set display brightness"""
        self.brightness = max(10, min(100, level))
        self.matrix.brightness = self.brightness
        logger.log(
            LogType.SYSTEM,
            "brightness_changed",
            {"level": level}
        )

    def set_color(self, element, color):
        """Set RGB color for specific display element"""
        if element in self.colors:
            self.colors[element] = color
            logger.log(
                LogType.SYSTEM,
                "color_changed",
                {"element": element, "color": color}
            )

    def set_display_power(self, state):
        """Turn display on/off"""
        self.display_enabled = state
        logger.log(
            LogType.SYSTEM,
            "display_power",
            {"state": "on" if state else "off"}
        )

    def draw_large_number(self, number, color=(255, 255, 255)):
        """Create image with large digit for display"""
        image = Image.new('RGB', (32, 64))
        draw = ImageDraw.Draw(image)
        
        ones = number % 10
        tens = number // 10
        
        self.large_digits.draw_digit(draw, ones, 0, 8, color, pixel_size=2)
        if tens == 1:
            self.large_digits.draw_small_one(draw, color)
        
        return image

    def _update_display(self):
        """Main display update loop"""
        scroll_position = 0
        
        while self.running:
            canvas = self.double_buffer
            image = Image.new('RGB', (256, 32))
            draw = ImageDraw.Draw(image)
            
            if self.display_enabled:
                if self.display_mode == 'timer':
                    # Draw timer
                    if self.game_time > 0 and not self.timer_paused:
                        self.game_time -= 0.1
                        self.check_two_min_warning()
                    
                    mins, secs = divmod(self.game_time, 60)
                    timer_text = f"{int(mins):02d}:{int(secs):02d}"
                    # Draw timer implementation
                
                elif self.display_mode == 'text':
                    if self.show_time:
                        # Show current time
                        time_text = datetime.now().strftime("%H:%M")
                        # Draw time implementation
                    else:
                        # Scroll text
                        # Scrolling text implementation
                        scroll_position = (scroll_position + 1) % len(self.scroll_text)
                
                # Draw scores
                # Score drawing implementation
            
            # Always draw status indicator
            self.draw_status_indicator(image)
            
            canvas.SetImage(image)
            canvas = self.matrix.SwapOnVSync(canvas)
            
            time.sleep(0.1)

    def cleanup(self):
        """Clean up resources"""
        self.running = False
        self.display_thread.join()
        self.matrix.Clear()
