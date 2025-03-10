import requests
from typing import List
from .dto import MeasurementDTO

class MetricsAPI:
    def __init__(self, server_url: str, api_metrics_endpoint: str, timeout: int):
        self.server_url = server_url
        self.api_metrics_endpoint = api_metrics_endpoint
        self.timeout = timeout

    def post_metrics(self, data_snapshots: List[MeasurementDTO]) -> None:
        url = f"{self.server_url}/{self.api_metrics_endpoint}"
        serialized_data = [snapshot.serialize() for snapshot in data_snapshots]
        response = requests.post(
            url,
            json=serialized_data,
            headers={'Content-Type': 'application/json'},
            timeout=self.timeout
        )
        response.raise_for_status()
