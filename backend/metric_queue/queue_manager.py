import time
import requests
from datetime import datetime
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
        self.collection_interval = config.server.collection_interval
        self.timeout = config.server.timeout
        self.registry = CollectorRegistry()
        
        # Register collectors
        self.registry.register('system', SystemCollector())
        self.registry.register('crypto', CryptoCollector())

    def format_metrics(self, raw_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format raw metrics using transform rules based on collector type"""
        formatted_metrics = []
        
        for metric in raw_metrics:
            try:
                collector_type = metric.get('collector')
                if not collector_type:
                    logger.warning(f"Missing collector type in metric: {metric}")
                    continue

                # Get the corresponding transform rules for this collector type
                rules = getattr(self.transform_rules, collector_type, None)
                if not rules:
                    logger.warning(f"No transform rules found for collector: {collector_type}")
                    continue

                # Convert string timestamp to datetime
                timestamp_str = metric['timestamp']
                if isinstance(timestamp_str, str):
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                else:
                    timestamp = datetime.fromtimestamp(timestamp_str)

                # Format each metric field according to its rules
                for field, rule in rules.__dict__.items():
                    if field in metric:
                        try:
                            name = rule.name
                            # Handle special formatting for crypto pairs
                            if collector_type == 'crypto' and '{pair}' in name:
                                name = name.format(pair=metric['currency_pair'])

                            measurement = Measurement(
                                name=name,
                                value=float(metric[field]),
                                unit=rule.unit,
                                timestamp=timestamp,
                                source=rule.source,
                                type=collector_type
                            )
                            formatted_metrics.append(measurement.serialize())
                        except Exception as e:
                            logger.error(f"Error formatting field {field}: {str(e)}")

            except Exception as e:
                logger.error(f"Error processing metric {metric}: {str(e)}")
                
        return formatted_metrics

    def collect_and_upload(self) -> None:
        """Collect metrics and upload to server"""
        try:
            # Collect raw metrics from all collectors
            raw_metrics = self.registry.collect_all()
            
            # Format metrics using transform rules
            formatted_metrics = self.format_metrics(raw_metrics)
            
            # Upload formatted metrics
            if formatted_metrics:
                self._upload_metrics('metrics', formatted_metrics)
                logger.info(f"Uploaded {len(formatted_metrics)} formatted metrics")
                
        except Exception as e:
            logger.error(f"Error in collection/upload cycle: {str(e)}")
            logger.error(traceback.format_exc())

    def _upload_metrics(self, metric_type: str, data: list) -> bool:
        """Upload metrics to server"""
        try:
    
            url = f"{self.server_url}/api/metrics"
            logger.debug(f"Uploading to {url} with data: {data}")
            response = requests.post(
                url, 
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload metrics: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Server response: {e.response.text}")
            return False

    def run(self) -> None:
        """Run continuous collection and upload cycle"""
        logger.info(f"Starting metrics collection. Server: {self.server_url}")
        while True:
            self.collect_and_upload()
            time.sleep(self.collection_interval)
