import psutil
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any

@dataclass
class Measurement:
    """Single measurement structure for any type of metric"""
    name: str       # What we're measuring (cpu_load, BTC_price, etc)
    value: float    # The actual value
    type: str       # Category (system, crypto)
    unit: str       # Measurement unit (%, USD, MB)
    timestamp: str  # When it was measured
    source: str     # Where it came from (device1, coinbase)

    def to_dict(self):
        """Convert measurement to dictionary format."""
        return {
            'name': self.name,
            'value': self.value,
            'type': self.type,
            'unit': self.unit,
            'timestamp': self.timestamp,
            'source': self.source
        }
