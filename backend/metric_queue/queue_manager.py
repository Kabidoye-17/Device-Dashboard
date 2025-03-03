import time
import threading
import requests
import json
from collections import deque
from typing import Dict, Any, List
from utils.logger import get_logger
from collectors.collector_registry import CollectorRegistry
from collectors.system_collector import SystemCollector
from collectors.crypto_collector import CryptoCollector
from models.measurement import Measurement
from config.config import load_config
import traceback

logger = get_logger('QueueManager')

class UploaderQueue:
    """Client-side collector and uploader"""
    def __init__(self):
        # Load config and initialize components
        config = load_config()
        self.transform_rules = config.transform_rules
        self.server_url = config.server.url
        self.api_metrics_endpoint = config.server.api_metrics_endpoint
        self.crypto = config.collector_types.crypto
        self.system = config.collector_types.system
        self.collection_interval = config.server.collection_interval
        self.upload_interval = config.server.upload_interval
        self.timeout = config.server.timeout
        self.max_queue_size = config.server.max_queue_size
        self.registry = CollectorRegistry()
        
        # Register collectors
        self.registry.register(self.system, SystemCollector())
        self.registry.register(self.crypto, CryptoCollector())

        self.queue = deque(maxlen=self.max_queue_size)
        self.running = True

    def format_metrics(self, raw_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format raw metrics using transform rules based on collector type"""
        formatted_metrics = []
        
        for metric in raw_metrics:
            try:
                collector_type = metric.get('collector_type')
                if not collector_type:
                    logger.warning(f"Missing collector type in metric: {metric}")
                    continue

                # Get the corresponding transform rules for this collector type
                rules = getattr(self.transform_rules, collector_type, None)
                if not rules:
                    logger.warning(f"No transform rules found for collector: {collector_type}")
                    continue

                # Format each metric field according to its rules
                for field, rule in rules.__dict__.items():
                    if field in metric:
                        try:
                            name = rule.name
                            # Handle special formatting for crypto pairs
                            if collector_type == self.crypto and '{pair}' in name:
                                name = name.format(pair=metric['currency_pair'])
                            
                            measurement = Measurement(
                                device_id=metric['device_id'],
                                device_name=metric['device_name'],
                                name=name,
                                value=float(metric[field]),
                                type=collector_type,
                                unit=rule.unit,
                                timestamp=metric['timestamp'],
                            )
                            formatted_metrics.append(measurement.serialize())
                        except Exception as e:
                            logger.error(f"Error formatting field {field}: {str(e)}")

            except Exception as e:
                logger.error(f"Error processing metric {metric}: {str(e)}")
                
        return formatted_metrics

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

            time.sleep(self.collection_interval)

    def upload_from_queue(self) -> None:
        """Continuously uploads metrics from the queue at upload_interval"""
        while self.running:
            if not self.queue:
                logger.info("No metrics to upload.")
            else:
                try:
                    data_to_upload = list(self.queue)[:9]

                    url = f"{self.server_url}/{self.api_metrics_endpoint}"
                    logger.debug(f"Uploading to {url} with {len(data_to_upload)} metrics")

                    response = requests.post(
                        url,
                        json=data_to_upload,
                        headers={'Content-Type': 'application/json'},
                        timeout=self.timeout
                    )
                    response.raise_for_status()

                    # Remove uploaded metrics from queue
                    for _ in range(len(data_to_upload)):
                        self.queue.popleft()

                    logger.info(f"Successfully uploaded {len(data_to_upload)} metrics (Queue size: {len(self.queue)})")

                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to upload metrics: {str(e)}")
                    if hasattr(e.response, 'text'):
                        logger.error(f"Server response: {e.response.text}")

            time.sleep(self.upload_interval)

    def run(self) -> None:
        """Starts collection and upload loops in separate threads"""
        logger.info(f"Starting metrics collection and upload. Server: {self.server_url}")

        collector_thread = threading.Thread(target=self.collect_and_enqueue, daemon=True)
        uploader_thread = threading.Thread(target=self.upload_from_queue, daemon=True)

        collector_thread.start()
        uploader_thread.start()

        try:
            while True:
                time.sleep(1)  # Keep the main thread alive
        except KeyboardInterrupt:
            self.running = False
            logger.info("Shutting down QueueManager...")

