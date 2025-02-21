import requests
from utils.timestamp import get_timestamp
from utils.logger import get_logger
from collectors.base_collector import BaseCollector

logger = get_logger('CryptoCollector')

class CryptoCollector(BaseCollector):
    """Collects cryptocurrency metrics from Coinbase API."""

    def __init__(self, currency_pairs=None):
        super().__init__()
        self.currency_pairs = currency_pairs or ['BTC-USD', 'ETH-USD']
        self.base_url = 'https://api.exchange.coinbase.com/products'
        self.latest_metrics = []

    def _fetch_single_pair(self, pair):
        """Fetch metrics for a single currency pair."""
        try:
            url = f'{self.base_url}/{pair}/ticker'
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            return {
                'collector': 'crypto',
                'currency_pair': pair,
                'price': round(float(data['price']), 2),
                'bid': round(float(data['bid']), 2),
                'ask': round(float(data['ask']), 2),
                'timestamp': get_timestamp(),
                'device_id': 'exchange.coinbase.com'
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
