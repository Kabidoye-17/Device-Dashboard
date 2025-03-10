import threading
import time
from metric_queue.queue_manager import UploaderQueue
from metric_queue.site_poller import SitePoller
from utils.logger import get_logger  # Import logger

logger = get_logger('RunApp')  # Initialize logger

def run_app() -> None:
    """Initializes and runs the collector, uploader, and site poller threads"""
    uploader_queue = UploaderQueue()
    site_poller = SitePoller()

    collector_thread = threading.Thread(target=uploader_queue.collect_and_enqueue, daemon=True)
    uploader_thread = threading.Thread(target=uploader_queue.upload_from_queue, daemon=True)
    site_polling_thread = threading.Thread(target=site_poller.run, daemon=True)

    collector_thread.start()
    uploader_thread.start()
    site_polling_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        uploader_queue.running = False
        site_poller.running = False
        logger.info("Shutting down application...")  # Use logger instead of print

if __name__ == "__main__":
    run_app()
