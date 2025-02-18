import threading
import time
from typing import Dict, Any
from collections import deque
from utils.logger import get_logger
from collectors.system_collector import SystemCollector
from collectors.crypto_collector import CryptoCollector

logger = get_logger('QueueManager')

class UploaderQueue:
    def __init__(self, collection_interval: int = 5):
        self.collection_interval = collection_interval
        self.running = False
        self.thread = None
        self.system_collector = SystemCollector()
        self.crypto_collector = CryptoCollector()
        self.latest_metrics: Dict[str, Any] = {
            'system_metrics': [],
            'crypto_metrics': {}
        }
        self.metrics_queue = deque(maxlen=1000)

    def start(self):
        """Starts the data collection loop in a separate thread."""
        self.running = True
        self.thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.thread.start()
        logger.info("Uploader queue started.")

    def stop(self):
        """Stops the data collection loop safely."""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Uploader queue stopped.")

    def _collect_and_enqueue(self, data_type: str, data: list, pair: str = None):
        """Adds collected data to the queue with a timestamp."""
        self.metrics_queue.append({
            'type': data_type,
            'data': data,
            'pair': pair,
            'timestamp': time.time()
        })

    def _collection_loop(self):
        """Continuously collects metrics and adds them to the queue."""
        while self.running:
            start_time = time.time()
            try:
                self._collect_and_enqueue('system_metrics', self.system_collector.collect_metrics())

                for pair in self.crypto_collector.valid_pairs:
                    crypto_data = self.crypto_collector.collect_crypto_data(pair)
                    if crypto_data:
                        self._collect_and_enqueue('crypto_metrics', crypto_data, pair)

                logger.info(f"Collected metrics, queue size: {len(self.metrics_queue)}")

            except Exception as e:
                logger.error(f"Error in collection loop: {str(e)}")

            elapsed_time = time.time() - start_time
            time.sleep(10)

    def get_latest_metrics(self):
        """Retrieves the latest system and crypto metrics from the queue."""
        latest_system = None
        latest_crypto = {}

        for entry in reversed(self.metrics_queue):
            if entry['type'] == 'system_metrics' and not latest_system:
                latest_system = entry['data']
            elif entry['type'] == 'crypto_metrics':
                latest_crypto.setdefault(entry['pair'], entry['data'])

            if latest_system and len(latest_crypto) == len(self.crypto_collector.valid_pairs):
                break

        return {'system_metrics': latest_system or {}, 'crypto_metrics': latest_crypto}
