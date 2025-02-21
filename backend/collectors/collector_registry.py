from typing import Dict, List, Any
from collectors.base_collector import BaseCollector
from utils.logger import get_logger

logger = get_logger('CollectorRegistry')

class CollectorRegistry:
    """Registry for managing metric collectors."""
    
    def __init__(self):
        self.collectors: Dict[str, BaseCollector] = {}

    def register(self, name: str, collector: BaseCollector) -> None:
        """Register a new collector."""
        if not isinstance(collector, BaseCollector):
            raise ValueError(f"Collector must inherit from BaseCollector: {collector}")
        
        self.collectors[name] = collector
        logger.info(f"Registered collector: {name}")

    def unregister(self, name: str) -> None:
        """Remove a collector from registry."""
        if name in self.collectors:
            del self.collectors[name]
            logger.info(f"Unregistered collector: {name}")

    def get_collector(self, name: str) -> BaseCollector:
        """Get a specific collector."""
        return self.collectors.get(name)

    def get_all_collectors(self) -> Dict[str, BaseCollector]:
        """Get all registered collectors."""
        return self.collectors

    def collect_all(self) -> List[Dict[str, Any]]:
        """Collect metrics from all registered collectors."""
        raw_metrics = []
        for name, collector in self.collectors.items():
            try:
                metrics = collector.collect_metrics()
                if isinstance(metrics, dict):
                    metrics = [metrics]  # Convert single dict to list
                raw_metrics.extend(metrics)
            except Exception as e:
                logger.error(f"Error collecting from {name}: {str(e)}")
        return raw_metrics
