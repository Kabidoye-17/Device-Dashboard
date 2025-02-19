from typing import Dict, Any
from utils.logger import get_logger
from collectors.system_collector import SystemCollector
from collectors.crypto_collector import CryptoCollector
import time

logger = get_logger('QueueManager')

class UploaderQueue:
    def __init__(self):
        self.system_collector = SystemCollector()
        self.crypto_collector = CryptoCollector()
        self.latest_metrics: Dict[str, Any] = {
            'system_metrics': [],
            'crypto_metrics': {}
        }
        self.last_collection_time = 0
        self.force_collection_interval = 10  # seconds

    def _collect_all(self) -> Dict[str, Any]:
        """Force collection of all metrics"""
        try:
            # Collect system metrics
            system_metrics = self.system_collector.collect_metrics()
            if system_metrics:
                self.latest_metrics['system_metrics'] = system_metrics
                logger.debug(f"Collected system metrics: {system_metrics}")

            # Collect crypto metrics
            crypto_metrics = {}
            for pair in self.crypto_collector.valid_pairs:
                crypto_data = self.crypto_collector.collect_crypto_data(pair)
                if crypto_data:
                    crypto_metrics[pair] = crypto_data
                    logger.debug(f"Collected {pair} data: {crypto_data}")
            
            self.latest_metrics['crypto_metrics'] = crypto_metrics
            self.last_collection_time = time.time()
            logger.info("Metrics collection completed")

        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")

        return self.latest_metrics

    def get_latest_metrics(self) -> Dict[str, Any]:
        """Get latest metrics, forcing collection if too old"""
        current_time = time.time()
        if current_time - self.last_collection_time >= self.force_collection_interval:
            logger.debug("Forcing collection due to stale data")
            return self._collect_all()
        
        logger.debug("Returning cached metrics")
        return self.latest_metrics
