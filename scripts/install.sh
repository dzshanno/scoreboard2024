# File: scripts/install.sh

#!/bin/bash
set -e

echo "Installing Hockey Scoreboard..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    git \
    hostapd \
    dnsmasq \
    i2c-tools \
    python3-smbus \
    libopenjp2-7 \
    libtiff5

# Enable I2C
if ! grep -q "i2c-dev" /etc/modules; then
    echo "i2c-dev" | sudo tee -a /etc/modules
fi
sudo raspi-config nonint do_i2c 0

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt

# Create data directory
mkdir -p data/logs

# Configure WiFi access point
sudo cp config/hostapd.conf /etc/hostapd/
sudo cp config/dnsmasq.conf /etc/

# Set up systemd service
sudo tee /etc/systemd/system/scoreboard.service << EOF
[Unit]
Description=Hockey Scoreboard
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
sudo chmod 644 /etc/systemd/system/scoreboard.service

# Enable services
sudo systemctl daemon-reload
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
sudo systemctl enable scoreboard

# Generate WiFi password
python3 - << EOF
from config.wifi_config import WifiConfig
WifiConfig.save_hostapd_config()
EOF

# Start services
sudo systemctl start hostapd
sudo systemctl start dnsmasq
sudo systemctl start scoreboard

echo "Installation complete!"
echo "Check status with: sudo systemctl status scoreboard"