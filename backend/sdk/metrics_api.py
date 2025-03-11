import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List
from .dto import MeasurementDTO

class MetricsAPI:
    def __init__(self, server_url: str, api_metrics_endpoint: str, timeout: int):
        self.server_url = server_url
        self.api_metrics_endpoint = api_metrics_endpoint
        self.timeout = timeout
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    def post_metrics(self, data_snapshots: List[MeasurementDTO]) -> None:
        """
        Sends a list of MeasurementDTO objects to the server as a POST request.

        This method serializes the provided MeasurementDTO objects and sends them
        to the specified API endpoint using a POST request. It includes a retry
        strategy to handle transient errors and ensures the request is retried
        up to 3 times for specific HTTP status codes.

        Args:
            data_snapshots (List[MeasurementDTO]): A list of MeasurementDTO objects to be sent to the server.

        Raises:
            requests.exceptions.HTTPError: If the response contains an HTTP error status code.
        """
        url = f"{self.server_url}/{self.api_metrics_endpoint}"
        serialized_data = [snapshot.serialize() for snapshot in data_snapshots]
        
        with self.session as session:
            response = session.post(
                url,
                json=serialized_data,
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )
            response.raise_for_status()
