import socket
import psutil
from utils.timestamp import get_local_time_with_offset
from config.config import load_config
from utils.logger import get_logger
from collectors.base_collector import BaseCollector
import subprocess
import platform
import machineid


logger = get_logger('SystemCollector')
config = load_config()


class SystemCollector(BaseCollector):
    """Collects system metrics including CPU, RAM, and network usage."""

    def __init__(self):
        super().__init__()
        self.device_id = machineid.hashed_id()
        self.device_name = socket.gethostname()
        self.collector_type = config.collector_types.system
        self.latest_metrics = {}

    def collect_metrics(self):
        """Gathers system performance metrics."""
        try:
    
            network = psutil.net_io_counters()

            metrics = {
                'collector_type': self.collector_type,
                'device_id': self.device_id,
                'device_name': self.device_name,
                'cpu_load': round(psutil.cpu_percent(interval=1), 2),
                'ram_usage': round(psutil.virtual_memory().percent, 2),
                'network_sent': round(network.bytes_sent / (1024 * 1024), 2),
                'timestamp': get_local_time_with_offset(),
            }

            self.latest_metrics = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}

    def get_latest_metrics(self):
        """Gets the latest collected system metrics."""
        return self.latest_metrics if self.latest_metrics else self.collect_metrics()
    

   