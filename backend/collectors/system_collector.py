import psutil
from utils.timestamp import get_timestamp
from models.measurement import Measurement
from utils.logger import get_logger

logger = get_logger('SystemCollector')

class SystemCollector:
    """Collects system metrics including CPU, RAM, and network usage."""

    def __init__(self, device_id: str = 'default'):
        self.device_id = device_id
        self.latest_metrics = []

    def collect_metrics(self):
        """Gathers system performance metrics."""
        try:
            timestamp = get_timestamp()
            network = psutil.net_io_counters()

            measurements = [
                Measurement('cpu_load', psutil.cpu_percent(interval=1), 'system', '%', timestamp, self.device_id),
                Measurement('ram_usage', psutil.virtual_memory().percent, 'system', '%', timestamp, self.device_id),
                Measurement('network_sent', round(network.bytes_sent / (1024 * 1024), 2), 'system', 'MB', timestamp, self.device_id)
            ]

            self.latest_metrics = measurements
            return measurements
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return []

    def get_latest_metrics(self):
        """Gets the latest collected system metrics."""
        return self.latest_metrics if self.latest_metrics else self.collect_metrics()
