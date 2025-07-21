#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
sudo apt update && sudo apt install -y python3 python3-pip mitmproxy
pip3 install -r requirements.txt

# Create necessary directories
echo "Setting up directories..."
mkdir -p logs config database

# Create default config file if not exists
CONFIG_FILE="config/settings.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default settings.json..."
    cat <<EOL > $CONFIG_FILE
{
    "api_key": "YOUR_API_KEY",
    "check_url": "https://phishing-database.com/check"
}
EOL
fi

# Set up systemd service
echo "Setting up PhishDefender as a system service..."
sudo cp service/phishdefender.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable phishdefender

# Installation complete
echo "Installation complete! Run 'sudo systemctl start phishdefender' to begin monitoring."
