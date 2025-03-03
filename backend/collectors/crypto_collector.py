import requests
from utils.timestamp import get_local_time_with_offset
from utils.logger import get_logger
from collectors.base_collector import BaseCollector
from config.config import load_config

logger = get_logger('CryptoCollector')
config = load_config()

class CryptoCollector(BaseCollector):
    """Collects cryptocurrency metrics from Coinbase API."""

    def __init__(self):
        super().__init__()
        self.currency_pairs = config.crypto_collector.currency_pairs
        self.base_url = config.crypto_collector.base_url
        self.collector_type = config.collector_types.crypto
        self.device_id = config.crypto_collector.device_id
        self.ticker_endpoint = config.crypto_collector.ticker_endpoint
        self.device_name = config.crypto_collector.device_name
        self.latest_metrics = []

    def _fetch_single_pair(self, pair):
        """Fetch metrics for a single currency pair."""
        try:
            
            url = f'{self.base_url}/{pair}/{self.ticker_endpoint}'
            session = requests.Session()
            response = session.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            return {
                'collector_type': self.collector_type,
                'device_id': self.device_id,
                'device_name': self.device_name,
                'currency_pair': pair,
                'price': round(float(data['price']), 2),
                'bid': round(float(data['bid']), 2),
                'ask': round(float(data['ask']), 2),
                'timestamp': get_local_time_with_offset(),
            }
        except Exception as e:
            logger.error(f"Error fetching {pair}: {str(e)}")
            return None

    def collect_metrics(self):
        """Collects current crypto metrics for all pairs."""
        metrics = []
        for pair in self.currency_pairs:
            pair_data = self._fetch_single_pair(pair)
            if pair_data:
                metrics.append(pair_data)

        self.latest_metrics = metrics
        return metrics

    def get_latest_metrics(self):
        """Gets the latest collected crypto metrics."""
        return self.latest_metrics if self.latest_metrics else self.collect_metrics()
