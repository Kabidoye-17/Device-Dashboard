import time
import requests
from collections import deque
from typing import Dict, Any, List
from utils.timestamp import get_utc_timestamp, get_utc_offset
from utils.logger import get_logger
from .collectors.collector_registry import CollectorRegistry
from .collectors.system_collector import SystemCollector
from .collectors.crypto_collector import CryptoCollector
from config.config import load_config
import traceback
from .metrics_sdk.metric_formatter import MetricFormatter
from .metrics_sdk.metrics_api import MetricsAPI

logger = get_logger('QueueManager')

class UploaderQueue:
    """Client-side collector and uploader"""
    def __init__(self):
        # Load config and initialize components
        config = load_config()

        self.server_url = config.server.url
        self.api_metrics_endpoint = config.server.api_metrics_endpoint
        self.crypto = config.collector_types.crypto
        self.system = config.collector_types.system
        self.collect_upload_interval = config.server.collect_upload_interval
        self.batch_size = config.server.batch_size
        self.timeout = config.server.timeout
        self.max_queue_size = config.server.max_queue_size
        self.registry = CollectorRegistry()
        
        # Register collectors
        self.registry.register(self.system, SystemCollector())
        self.registry.register(self.crypto, CryptoCollector())

        self.queue = deque(maxlen=self.max_queue_size)
        self.running = True
        self.metric_formatter = MetricFormatter()  
        self.metrics_api = MetricsAPI(self.server_url, self.api_metrics_endpoint, self.timeout)  # New instance

    def format_metrics(self, raw_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format raw metrics using transform rules based on collector type"""
        return self.metric_formatter.format(raw_metrics)  

    def collect_and_enqueue(self) -> None:
        """Continuously collects metrics and adds them to the queue at collection_interval"""
        while self.running:
            try:
                raw_metrics = self.registry.collect_all()
                formatted_metrics = self.format_metrics(raw_metrics)

                for metric in formatted_metrics:
                    if len(self.queue) >= self.max_queue_size:
                        logger.warning("Queue is full, dropping oldest metric.")
                    self.queue.append(metric)

                logger.info(f"Collected and queued {len(formatted_metrics)} metrics (Queue size: {len(self.queue)})")

            except Exception as e:
                logger.error(f"Error in collection cycle: {str(e)}")
                logger.error(traceback.format_exc())

            time.sleep(self.collect_upload_interval)

    def upload_from_queue(self) -> None:
        """Continuously uploads metrics from the queue at upload_interval"""
        while self.running:
            if len(self.queue) < self.batch_size:
                logger.info(f"Queue size ({len(self.queue)}) is less than {self.batch_size}, waiting for a full batch.")
            else:
                try:
                    data_to_upload = list(self.queue)[:self.batch_size]

                    logger.debug(f"Uploading to {self.server_url}/{self.api_metrics_endpoint} with {len(data_to_upload)} metrics")

                    self.metrics_api.post_metrics(data_to_upload)

                    # Remove uploaded metrics from queue
                    for _ in range(len(data_to_upload)):
                        self.queue.popleft()

                    logger.info(f"Successfully uploaded {len(data_to_upload)} metrics (Queue size: {len(self.queue)})")

                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to upload metrics: {str(e)}")
                    if hasattr(e.response, 'text'):
                        logger.error(f"Server response: {e.response.text}")

            time.sleep(self.collect_upload_interval)

