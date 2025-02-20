import time
import requests
from typing import Dict, Any
from utils.logger import get_logger
from collectors.system_collector import SystemCollector
from collectors.crypto_collector import CryptoCollector
import traceback

logger = get_logger('QueueManager')

class MetricsStore:
    """Server-side metrics storage"""
    def __init__(self):
        self.latest_metrics: Dict[str, Any] = {
            'system_metrics': [],
            'crypto_metrics': {}
        }
        self.last_update_time = 0

    def update_system_metrics(self, metrics: list) -> None:
        """Update system metrics with validation"""
        try:
            if not isinstance(metrics, list):
                raise ValueError(f"Expected list of metrics, got {type(metrics)}")
            
            # Validate metric format
            for metric in metrics:
                if not all(k in metric for k in ['name', 'value', 'timestamp']):
                    raise ValueError(f"Invalid metric format: {metric}")
            
            self.latest_metrics['system_metrics'] = metrics
            self.last_update_time = time.time()
            logger.debug(f"Updated system metrics: {metrics}")
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def update_crypto_metrics(self, metrics: dict) -> None:
        self.latest_metrics['crypto_metrics'] = metrics
        self.last_update_time = time.time()
        logger.debug("Updated crypto metrics")

    def get_latest_metrics(self) -> Dict[str, Any]:
        if time.time() - self.last_update_time > 30:
            logger.warning("Metrics are stale (>30s old")
        return self.latest_metrics

class UploaderQueue:
    """Client-side collector and uploader"""
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
            url = f"{self.server_url}/metrics/{metric_type}"
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
