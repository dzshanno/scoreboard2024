# File: scripts/update.sh

#!/bin/bash
set -e

echo "Updating Hockey Scoreboard..."

# Activate virtual environment
source venv/bin/activate

# Pull latest code
git pull

# Update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart scoreboard

echo "Update complete!"