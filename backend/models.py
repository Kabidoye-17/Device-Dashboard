import psutil
import os
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SystemMetrics:
    """
    SystemMetrics class to track system performance:
    - cpu_load: Percentage of CPU usage (0-100%)
    - ram_usage: Percentage of RAM usage (0-100%)
    - network_sent: Total data sent since system boot (MB)
    - timestamp: When metrics were collected
    """
    cpu_load: float
    ram_usage: float
    network_sent: float
    timestamp: str

    @staticmethod
    def get_current_metrics():
        network = psutil.net_io_counters()
        return SystemMetrics(
            cpu_load=psutil.cpu_percent(interval=1),
            ram_usage=psutil.virtual_memory().percent,
            network_sent=round(network.bytes_sent / (1024 * 1024), 2),  # Convert bytes to MB
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
