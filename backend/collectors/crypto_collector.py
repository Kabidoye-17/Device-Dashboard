import requests
from decimal import Decimal
from utils.timestamp import get_timestamp
from models.measurement import Measurement
from utils.logger import get_logger

logger = get_logger('CryptoCollector')

class CryptoCollector:
    """Collects cryptocurrency metrics from Coinbase API."""

    def __init__(self):
        self.valid_pairs = {'BTC-USD', 'ETH-USD'}
        self.latest_data = {}

    def _fetch_crypto_data(self, currency_pair):
        """Fetches data from Coinbase API."""
        url = f'https://api.exchange.coinbase.com/products/{currency_pair}/ticker'
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {currency_pair} data: {str(e)}")
            return None

    def collect_crypto_data(self, currency_pair):
        """Collects and stores price, bid, and ask for a currency pair."""
        if currency_pair not in self.valid_pairs:
            logger.warning(f"Invalid pair requested: {currency_pair}")
            return []

        data = self._fetch_crypto_data(currency_pair)
        if not data:
            return []

        timestamp = get_timestamp()

        measurements = [
            Measurement(f'{currency_pair}_price', float(Decimal(str(data['price']))), 'crypto', 'USD', timestamp, 'coinbase'),
            Measurement(f'{currency_pair}_bid', float(Decimal(str(data['bid']))), 'crypto', 'USD', timestamp, 'coinbase'),
            Measurement(f'{currency_pair}_ask', float(Decimal(str(data['ask']))), 'crypto', 'USD', timestamp, 'coinbase')
        ]

        self.latest_data[currency_pair] = [m.to_dict() for m in measurements]
        return self.latest_data[currency_pair]

    def get_latest_crypto_data(self, currency_pair):
        """Retrieves latest stored data or triggers a new collection."""
        return self.latest_data.get(currency_pair) or self.collect_crypto_data(currency_pair)

    def collect_all_pairs(self):
        """Collects data for all valid pairs."""
        return {pair: self.collect_crypto_data(pair) for pair in self.valid_pairs}
