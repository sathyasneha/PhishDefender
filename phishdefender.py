import mitmproxy.http
from mitmproxy import ctx
import requests
import json
import subprocess
import time
from colorama import Fore, Style, init

# Initialize colorama for colored logs
init(autoreset=True)

# Load settings
CONFIG_FILE = "config/settings.json"
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

API_KEY = config.get("api_key", "YOUR_API_KEY")
CHECK_URL = config.get("check_url", "https://phishing-database.com/check")
LOG_FILE = "logs/phishdefender.log"

def log_message(message, color=Fore.WHITE):
    """Log messages to file and CLI with colors"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    with open(LOG_FILE, "a") as log:
        log.write(log_entry + "\n")
    print(color + log_entry + Style.RESET_ALL)

def check_url(url):
    """Check if a URL is malicious using a phishing database"""
    payload = {"url": url}
    try:
        response = requests.post(CHECK_URL, json=payload)
        if response.status_code == 200 and response.json().get("malicious", False):
            return True
        return False
    except Exception as e:
        log_message(f"Error checking URL: {e}", Fore.RED)
        return False

def request(flow: mitmproxy.http.HTTPFlow):
    """Intercept HTTP requests and check for malicious URLs."""
    url = flow.request.pretty_url
    if check_url(url):
        log_message(f"[BLOCKED] Malicious URL detected: {url}", Fore.RED)
        flow.response = mitmproxy.http.Response.make(
            403,
            b"Blocked by PhishDefender",
            {"Content-Type": "text/plain"}
        )
        subprocess.run(["pkill", "-f", url])  # Terminate browser tab
    else:
        log_message(f"[SAFE] {url}", Fore.GREEN)

if __name__ == "__main__":
    log_message("PhishDefender running in background...", Fore.BLUE)
    while True:
        time.sleep(10)
