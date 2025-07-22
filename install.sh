#!/bin/bash

# PhishDefender Installation Script
echo "Starting PhishDefender installation..."

# Install dependencies
sudo apt update && sudo apt install -y python3 python3-pip python3-venv mitmproxy

# Create a virtual environment in /opt/phishdefender
sudo mkdir -p /opt/phishdefender
python3 -m venv /opt/phishdefender/venv

# Activate virtual environment and install Python packages
source /opt/phishdefender/venv/bin/activate
pip install requests rich

# Copy main script
sudo cp phishdefender.py /opt/phishdefender/

# Create necessary directories and files
sudo mkdir -p /var/log/phishdefender
sudo touch /var/log/phishdefender/phishdefender.log

# Copy service file
sudo cp service/phishdefender.service /etc/systemd/system/

# Reload systemd and enable the service
sudo systemctl daemon-reload
sudo systemctl enable phishdefender

# Create a wrapper script to run PhishDefender with the virtual environment
echo '#!/bin/bash' | sudo tee /usr/local/bin/phishdefender > /dev/null
echo 'source /opt/phishdefender/venv/bin/activate && python3 /opt/phishdefender/phishdefender.py' | sudo tee -a /usr/local/bin/phishdefender > /dev/null
sudo chmod +x /usr/local/bin/phishdefender

echo "Installation complete! You can start PhishDefender with:"
echo "sudo phishdefender"

# Install mitmproxy inside the virtual environment
source /opt/phishdefender/venv/bin/activate
pip install mitmproxy
deactivate
