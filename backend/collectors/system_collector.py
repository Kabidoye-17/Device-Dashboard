import psutil
from utils.timestamp import get_timestamp
from utils.logger import get_logger
from collectors.base_collector import BaseCollector

logger = get_logger('SystemCollector')

class SystemCollector(BaseCollector):
    """Collects system metrics including CPU, RAM, and network usage."""

    def __init__(self, device_id: str = 'default'):
        super().__init__()
        self.device_id = device_id
        self.latest_metrics = {}

    def collect_metrics(self):
        """Gathers system performance metrics."""
        try:
            timestamp = get_timestamp()
            network = psutil.net_io_counters()

            metrics = {
                'collector': 'system',
                'device_id': self.device_id,
                'cpu_load': round(psutil.cpu_percent(interval=1), 2),
                'ram_usage': round(psutil.virtual_memory().percent, 2),
                'network_sent': round(network.bytes_sent / (1024 * 1024), 2),
                'timestamp': timestamp
            }

            self.latest_metrics = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}

    def get_latest_metrics(self):
        """Gets the latest collected system metrics."""
        return self.latest_metrics if self.latest_metrics else self.collect_metrics()
