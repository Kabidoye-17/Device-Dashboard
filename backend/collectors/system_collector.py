import socket
import psutil
from models.DTO import SystemMetricDTO
from config.config import load_config
from utils.logger import get_logger
from collectors.base_collector import BaseCollector
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
        logger.info("Starting to collect system metrics.")
        try:
            network = psutil.net_io_counters()

            metrics = SystemMetricDTO(
                collector_type=self.collector_type,
                device_id=self.device_id,
                device_name=self.device_name,
                cpu_load=psutil.cpu_percent(),
                ram_usage=psutil.virtual_memory().percent,
                network_sent=network.bytes_sent
            ).serialize()

            self.latest_metrics = metrics
            logger.info(f"Collected system metrics: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}

    def get_latest_metrics(self):
        """Gets the latest collected system metrics."""
        logger.info("Fetching the latest collected system metrics.")
        latest_metrics = self.latest_metrics if self.latest_metrics else self.collect_metrics()
        logger.info(f"Latest system metrics: {latest_metrics}")
        return latest_metrics


