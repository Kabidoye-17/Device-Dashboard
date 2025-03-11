import time
import threading
import requests
import traceback
from utils.logger import get_logger
from config.config import load_config
import webbrowser

logger = get_logger('siteReciever')

def open_trading_site(url: str) -> bool:
    """Opens the given URL in the default web browser"""
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        logger.error(f"Failed to open site {url}: {str(e)}")
        return False

class SitePoller:
    """Polls the server for a site to open"""
    def __init__(self):
        config = load_config()
        self.server_url = config.server.url
        self.timeout = config.server.timeout
        self.poll_interval =config.server.polling_interval
        self.polling_endpoint = config.server.polling_endpoint
        self.running = True
        self.session = requests.Session()

    def poll_for_site_url(self) -> None:
        """Continuously polls the server for a site to open, one at a time"""
        while self.running:
            try:
                response = self.session.get(
                    f"{self.server_url}{self.polling_endpoint}",
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()

                if data.get("status") == "success" and data.get("site"):
                    site = data["site"]
                    logger.info(f"Received instruction to open site: {site}")
                    result = open_trading_site(site)
                    logger.info(f"Open site result: {result}")

                else:
                    logger.info("No site to open at the moment.")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error polling for sites: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error in poll_for_sites: {str(e)}")
                logger.error(traceback.format_exc())

            time.sleep(self.poll_interval)

    def run(self) -> None:
        """Starts the site polling loop in a separate thread"""
        logger.info(f"Starting site polling. Server: {self.server_url}")

        polling_thread = threading.Thread(target=self.poll_for_site_url, daemon=True)
        polling_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            logger.info("Shutting down ReceiveSite...")
