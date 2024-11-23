# File: config/settings.py

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Debug mode
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

# Network settings
HOST = "0.0.0.0"
PORT = 80

# File paths
LOG_FILE = LOG_DIR / "scoreboard.log"
DB_FILE = DATA_DIR / "scoreboard.db"
MESSAGE_PRESETS_FILE = DATA_DIR / "message_presets.json"

# Display configuration
DISPLAY_CONFIG = {
    "rows": 32,
    "cols": 64,
    "chain_length": 4,
    "parallel": 1,
    "hardware_mapping": "adafruit-hat",
    "gpio_slowdown": 2,
    "pwm_bits": 11,
    "pwm_lsb_nanoseconds": 130,
}

# Network configuration
NETWORK_CONFIG = {"ssid": "Hockey-Scoreboard", "port": 80, "host": "0.0.0.0"}

# System thresholds
SYSTEM_THRESHOLDS = {
    "temperature_warning": 70,  # Celsius
    "low_battery": 20,  # Percent
    "low_voltage": 4.7,  # Volts
    "auto_dim_temp": 65,  # Temperature at which to auto-dim
    "min_brightness": 30,  # Minimum brightness percentage
}

# Default colors (RGB)
DEFAULT_COLORS = {
    "home": (0, 255, 0),  # Green
    "away": (0, 255, 0),  # Green
    "timer": (255, 255, 0),  # Yellow
    "text": (0, 255, 255),  # Cyan
}

# Game settings
GAME_SETTINGS = {
    "default_period_length": 35,  # minutes
    "warning_time": 120,  # seconds (2 minutes)
    "max_score": 19,
}
