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

    def _serialize_measurements(self, measurements):
        """Convert Measurement objects to dictionaries"""
        return [{
            'name': m.name,
            'value': m.value,
            'type': m.type,
            'unit': m.unit,
            'timestamp': m.timestamp,
            'device_id': m.device_id
        } for m in measurements]

class UploaderQueue:
    """Client-side collector and uploader"""
    def __init__(self, server_url: str, collection_interval: int = 10):
        self.server_url = server_url
        self.system_collector = SystemCollector()
        self.crypto_collector = CryptoCollector()
        self.collection_interval = collection_interval
        self.last_upload_time = 0

    def _serialize_measurements(self, measurements):
        """Convert Measurement objects to dictionaries"""
        serialized = []
        for m in measurements:
            if hasattr(m, '_asdict'):  # Handle namedtuple
                data = m._asdict()
            elif isinstance(m, dict):  # Already a dict
                data = m
            else:  # Custom Measurement class
                data = {
                    'name': str(m.name),
                    'value': float(m.value),
                    'type': str(m.type),
                    'unit': str(m.unit),
                    'timestamp': m.timestamp.timestamp() if hasattr(m.timestamp, 'timestamp') else m.timestamp,
                    'device_id': str(m.device_id) if hasattr(m, 'device_id') else None
                }
            serialized.append(data)
        return serialized

    def collect_and_upload(self) -> None:
        """Collect metrics and upload to server"""
        try:
            # Collect and upload system metrics
            system_metrics = self.system_collector.collect_metrics()
            if system_metrics:
                serialized_metrics = self._serialize_measurements(system_metrics)
                logger.debug(f"Serialized system metrics: {serialized_metrics}")
                self._upload_metrics('system', serialized_metrics)
                logger.info("System metrics collected and uploaded")

            # Changed collect_metrics to collect_all_pairs for crypto
            crypto_metrics = self.crypto_collector.collect_all_pairs()
            if crypto_metrics:
                serialized_metrics = self._serialize_measurements(crypto_metrics)
                logger.debug(f"Serialized crypto metrics: {serialized_metrics}")
                self._upload_metrics('crypto', serialized_metrics)
                logger.info("Crypto metrics collected and uploaded")

        except Exception as e:
            logger.error(f"Error in collection/upload cycle: {str(e)}")
            logger.error(traceback.format_exc())

    def _upload_metrics(self, metric_type: str, data: list) -> bool:
        """Upload metrics to server"""
        try:
            url = f"{self.server_url}/api/metrics/{metric_type}"
            logger.debug(f"Uploading to {url} with data: {data}")
            response = requests.post(
                url, 
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload {metric_type} metrics: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Server response: {e.response.text}")
            return False

    def run(self) -> None:
        """Run continuous collection and upload cycle"""
        logger.info(f"Starting metrics collection. Server: {self.server_url}")
        while True:
            self.collect_and_upload()
            time.sleep(self.collection_interval)
