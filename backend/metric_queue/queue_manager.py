import time
import requests
from typing import Dict, Any
from utils.logger import get_logger
from collectors.system_collector import SystemCollector
from collectors.crypto_collector import CryptoCollector

logger = get_logger('QueueManager')

class UploaderQueue:
    def __init__(self, server_url: str, collection_interval: int = 10):
        self.server_url = server_url
        self.system_collector = SystemCollector()
        self.crypto_collector = CryptoCollector()
        self.collection_interval = collection_interval
        self.last_upload_time = 0

    def collect_and_upload(self) -> None:
        """Collect metrics and upload to server"""
        try:
            # Collect system metrics from local machine
            system_metrics = self.system_collector.collect_metrics()
            if system_metrics:
                self._upload_metrics('system', system_metrics)
                logger.info("System metrics collected and uploaded")

            # Collect crypto data from API
            crypto_metrics = self.crypto_collector.collect_all_pairs()
            if crypto_metrics:
                self._upload_metrics('crypto', crypto_metrics)
                logger.info("Crypto metrics collected and uploaded")

            self.last_upload_time = time.time()

        except Exception as e:
            logger.error(f"Error in collection/upload cycle: {str(e)}")

    def _upload_metrics(self, metric_type: str, data: dict) -> bool:
        """Upload metrics to PythonAnywhere server"""
        try:
            url = f"{self.server_url}/api/metrics/{metric_type}"
            response = requests.post(url, json=data, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to upload {metric_type} metrics: {str(e)}")
            return False

    def run(self) -> None:
        """Run continuous collection and upload cycle"""
        logger.info(f"Starting metrics collection. Server: {self.server_url}")
        while True:
            self.collect_and_upload()
            time.sleep(self.collection_interval)
