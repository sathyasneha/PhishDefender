# PhishDefender

PhishDefender is a Kali Linux CLI tool that monitors web traffic, checks URLs against a phishing database, and blocks malicious links.

## Installation

```bash
chmod +x install.sh
./install.sh
```

## Usage

```bash
sudo systemctl start phishdefender  # Start monitoring
sudo systemctl stop phishdefender   # Stop monitoring
```

## Logs

Check logs in `logs/phishdefender.log`
