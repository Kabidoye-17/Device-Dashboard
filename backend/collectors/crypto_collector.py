import requests
from decimal import Decimal
from utils.timestamp import get_timestamp
from models.measurement import Measurement
from utils.logger import get_logger
from typing import List

logger = get_logger('CryptoCollector')

class CryptoCollector:
    """Collects cryptocurrency metrics from Coinbase API."""

    def __init__(self):
        self.valid_pairs = {'BTC-USD', 'ETH-USD'}
        self.latest_data = {}
        self.source = 'coinbase_api'

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

    def collect_all_pairs(self) -> List[Measurement]:
        """Collect price data for all valid pairs"""
        all_measurements = []
        timestamp = get_timestamp()
        
        for pair in self.valid_pairs:
            try:
                data = self._fetch_crypto_data(pair)
                if not data:
                    continue

                # Create measurements with precise decimal handling
                measurements = [
                    Measurement(
                        name=f'{pair.lower()}_price',
                        value=float(Decimal(str(data['price']))),
                        type='crypto',
                        unit='USD',
                        timestamp=timestamp,
                        source=self.source
                    ),
                    Measurement(
                        name=f'{pair.lower()}_bid',
                        value=float(Decimal(str(data['bid']))),
                        type='crypto',
                        unit='USD',
                        timestamp=timestamp,
                        source=self.source
                    ),
                    Measurement(
                        name=f'{pair.lower()}_ask',
                        value=float(Decimal(str(data['ask']))),
                        type='crypto',
                        unit='USD',
                        timestamp=timestamp,
                        source=self.source
                    )
                ]
                
                all_measurements.extend(measurements)
                # Store for later retrieval
                self.latest_data[pair] = [m.to_dict() for m in measurements]
                
                logger.debug(f"Collected metrics for {pair}: Price={data['price']}, Bid={data['bid']}, Ask={data['ask']}")
            except Exception as e:
                logger.error(f"Error collecting {pair}: {str(e)}")
                continue
                
        return all_measurements

    def get_latest_data(self, currency_pair):
        """Retrieves latest stored data for a currency pair"""
        if currency_pair not in self.valid_pairs:
            logger.warning(f"Invalid pair requested: {currency_pair}")
            return None
        return self.latest_data.get(currency_pair)
