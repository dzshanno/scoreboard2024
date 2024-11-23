# Hockey Scoreboard - Complete Code Structure

## Project Structure
```
scoreboard/
├── main.py
├── modules/
│   ├── display.py
│   ├── power.py
│   ├── system_status.py
│   ├── logger.py
│   └── webserver.py
├── config/
│   ├── settings.py
│   └── wifi_config.py
├── templates/
│   ├── index.html
│   ├── logs.html
│   └── diagnostics.html
└── scripts/
    ├── install.sh
    └── start.sh
```

## `/main.py`
```python
#!/usr/bin/env python3

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from modules.display import ScoreBoard
from modules.webserver import create_app
from modules.logger import logger, LogType
from config.settings import LOG_FILE, DEBUG_MODE, HOST, PORT

def setup_logging():
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1024 * 1024,
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

def main():
    setup_logging()
    logger.log(LogType.SYSTEM, "application_start")
    
    try:
        scoreboard = ScoreBoard()
        app = create_app(scoreboard)
        
        app.run(
            host=HOST,
            port=PORT,
            debug=DEBUG_MODE
        )
        
    except Exception as e:
        logger.log(LogType.ERROR, "startup_failed", {"error": str(e)})
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## `/modules/display.py`
```python
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont
import threading
from datetime import datetime
from modules.logger import logger, LogType

class LargeDigits:
    # [Previous digit patterns code]

class ScoreBoard:
    def __init__(self):
        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.cols = 64
        self.options.chain_length = 4
        self.options.parallel = 1
        self.options.hardware_mapping = 'adafruit-hat'
        self.options.gpio_slowdown = 2
        
        self.matrix = RGBMatrix(options=self.options)
        self.double_buffer = self.matrix.CreateFrameCanvas()
        
        self.scores = {"home": 0, "away": 0}
        self.game_time = 0
        self.display_mode = 'timer'
        self.scroll_text = ""
        self.show_time = False
        self.display_enabled = True
        self.brightness = 100
        self.colors = {
            'home': (0, 255, 0),
            'away': (0, 255, 0),
            'timer': (255, 255, 0),
            'text': (0, 255, 255)
        }
        
        self.large_digits = LargeDigits()
        self.running = True
        self.display_thread = threading.Thread(target=self._update_display)
        self.display_thread.start()

    # [Rest of ScoreBoard methods]
```

## `/modules/power.py`
```python
from adafruit_ads1x15.ads1015 import ADS1015
import board
import busio
from modules.logger import logger, LogType

class PowerMonitor:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS1015(self.i2c)
        self.voltage_divider_ratio = 2
        
    # [Power monitoring methods]

class PowerManager:
    def __init__(self):
        self.power_monitor = PowerMonitor()
        self.power_sources = {
            'mains': False,
            'battery_1': False,
            'battery_2': False
        }
        
    # [Power management methods]
```

## `/modules/logger.py`
```python
from enum import Enum
import sqlite3
from datetime import datetime
import threading
from pathlib import Path
import json

class LogType(Enum):
    GAME = "game"
    SYSTEM = "system"
    ERROR = "error"
    POWER = "power"
    NETWORK = "network"

class LoggerDB:
    # [Previous logger code]

logger = LoggerDB()
```

## `/modules/system_status.py`
```python
import psutil
import platform
from datetime import datetime
import subprocess
from modules.logger import logger, LogType

class SystemInfo:
    def __init__(self):
        self.start_time = datetime.now()
        
    # [System monitoring methods]
```

## `/config/settings.py`
```python
import os

DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
HOST = '0.0.0.0'
PORT = 80
LOG_FILE = 'data/scoreboard.log'

DISPLAY_CONFIG = {
    'rows': 32,
    'cols': 64,
    'chain_length': 4,
    'parallel': 1,
    'hardware_mapping': 'adafruit-hat'
}

NETWORK_CONFIG = {
    'ssid': 'Hockey-Scoreboard',
    'port': 80,
    'host': '0.0.0.0'
}

SYSTEM_THRESHOLDS = {
    'temperature_warning': 70,
    'low_battery': 20,
    'low_voltage': 4.7
}
```

## `/config/wifi_config.py`
```python
class WifiConfig:
    AP_CONFIG = {
        'ssid': 'Hockey-Scoreboard',
        'country_code': 'GB',
        'hw_mode': 'g',
        'channel': 7,
        'auth_algs': 1,
        'wpa': 2,
        'wpa_key_mgmt': 'WPA-PSK',
        'rsn_pairwise': 'CCMP'
    }
    
    # [WiFi configuration methods]
```

## `/scripts/install.sh`
```bash
#!/bin/bash
set -e

echo "Installing Hockey Scoreboard..."

# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    git \
    hostapd \
    dnsmasq

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set up systemd service
sudo tee /etc/systemd/system/scoreboard.service << EOF
[Unit]
Description=Hockey Scoreboard
After=network.target

[Service]
ExecStart=$(pwd)/venv/bin/python $(pwd)/main.py
WorkingDirectory=$(pwd)
User=$USER
Group=$USER
Restart=always

[Install]
WantedBy=multi-default.target
EOF

# Enable and start service
sudo systemctl enable scoreboard
sudo systemctl start scoreboard

echo "Installation complete!"
```

## `requirements.txt`
```
Flask==2.0.1
rpi-rgb-led-matrix==0.0.1
pillow==8.3.1
adafruit-circuitpython-ads1x15==2.2.12
psutil==5.8.0
pijuice==1.8
```

## Example API Usage
```python
# Score update
curl -X POST http://192.168.4.1/api/score \
  -H "Content-Type: application/json" \
  -d '{"team":"home","value":1}'

# Get system status
curl http://192.168.4.1/api/system/info

# Get filtered logs
curl "http://192.168.4.1/api/logs?start_date=2024-01-01&type=game&limit=100"
```

Would you like me to add:
1. Additional configuration options?
2. More API endpoints?
3. Detailed comments/documentation?
4. Testing procedures?