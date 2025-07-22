#!/usr/bin/env python3

import time
import logging
import json
import requests
import asyncio
from rich.console import Console
from rich.table import Table
from rich.live import Live
from mitmproxy import http
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.options import Options

# Load settings
with open("config/settings.json", "r") as f:
    config = json.load(f)

LOG_FILE = config["log_file"]
API_KEY = config["api_key"]
API_ENDPOINT = config["api_endpoint"]

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

console = Console()

def banner():
    console.print("[bold cyan]██████╗ ██╗  ██╗██╗███████╗██╗  ██╗███████╗██████╗ [/bold cyan]")
    console.print("[bold cyan]██╔══██╗██║  ██║██║██╔════╝██║  ██║██╔════╝██╔══██╗[/bold cyan]")
    console.print("[bold cyan]██████╔╝███████║██║███████╗███████║█████╗  ██████╔╝[/bold cyan]")
    console.print("[bold cyan]██╔═══╝ ██╔══██║██║╚════██║██╔══██║██╔══╝  ██╔══██╗[/bold cyan]")
    console.print("[bold cyan]██║     ██║  ██║██║███████║██║  ██║███████╗██║  ██║[/bold cyan]")
    console.print("[bold cyan]╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝[/bold cyan]\n")
    console.print("[bold yellow]      [ PhishDefender - Real-Time Phishing Detection ][/bold yellow]\n")

def create_dashboard():
    """Create the monitoring dashboard."""
    table = Table(title="PhishDefender - Real-Time URL Monitoring", style="bold cyan")
    table.add_column("Timestamp", style="dim", width=20)
    table.add_column("Scanned URL", style="magenta", width=50)
    table.add_column("Status", style="bold yellow", width=20)
    return table

def check_url_with_api(url):
    """Check URL using CheckPhish API."""
    headers = {"Content-Type": "application/json"}
    data = {"apiKey": API_KEY, "urlInfo": {"url": url}}

    try:
        response = requests.post(f"{API_ENDPOINT}/v1/url", json=data, headers=headers)
        response_data = response.json()

        # Debugging: Log API response
        logging.info(f"API Response for {url}: {json.dumps(response_data, indent=4)}")
        console.print(f"[bold cyan]API Response for {url}: {json.dumps(response_data, indent=4)}[/bold cyan]")

        # Extract status dynamically based on response structure
        if "disposition" in response_data:
            return response_data["disposition"].upper()
        elif "status" in response_data:
            return response_data["status"].upper()
        elif "data" in response_data and "classification" in response_data["data"]:
            return response_data["data"]["classification"].upper()
        else:
            return "UNKNOWN"
    except requests.RequestException as e:
        logging.error(f"API Request Failed: {e}")
        return "ERROR"
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON response from API")
        return "ERROR"

def update_dashboard(table, url, status):
    """Update the dashboard with scanned URLs."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    table.add_row(timestamp, url, status)
    logging.info(f"Scanned: {url} | Status: {status}")

class PhishDefenderAddon:
    """Mitmproxy Addon for Intercepting Traffic."""
    
    def __init__(self, table):
        self.table = table
        self.live = Live(self.table, refresh_per_second=1)

    def request(self, flow: http.HTTPFlow):
        """Process each HTTP request."""
        url = flow.request.url
        status = check_url_with_api(url)
        update_dashboard(self.table, url, status)
        self.live.update(self.table)  # Update the dashboard dynamically

async def run_mitmproxy():
    """Run mitmproxy with a valid event loop."""
    table = create_dashboard()
    addon = PhishDefenderAddon(table)

    opts = Options(listen_host="127.0.0.1", listen_port=8080)
    m = DumpMaster(opts)
    m.addons.add(addon)

    with addon.live:
        console.print("[bold green]PhishDefender Monitoring Started...[/bold green]")
        try:
            await m.run()  # Start mitmproxy inside asyncio event loop
        except asyncio.CancelledError:
            console.print("[bold red]PhishDefender Stopped[/bold red]")

async def main():
    """Keep the script running indefinitely."""
    task = asyncio.create_task(run_mitmproxy())
    try:
        while True:
            await asyncio.sleep(1)  # Keep script alive
    except KeyboardInterrupt:
        console.print("[bold red]PhishDefender Interrupted. Exiting...[/bold red]")
        task.cancel()

if __name__ == "__main__":
    banner()
    asyncio.run(main())  
