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
    timestamp: datetime  # When it was measured
    source: str     # Where it came from (device1, coinbase)
    device_id: Optional[str] = None

    def to_dict(self):
        """Convert measurement to dictionary format."""
        return self.serialize()

    def serialize(self) -> dict:
        """Serialize measurement for JSON transmission"""
        # Convert timestamp to ISO format string if it's a datetime object
        if isinstance(self.timestamp, datetime):
            timestamp = self.timestamp.isoformat()
        elif hasattr(self.timestamp, 'timestamp'):  # Handle other timestamp objects
            timestamp = self.timestamp.timestamp()
        else:  # Already a string or number
            timestamp = self.timestamp

        return {
            'name': str(self.name),
            'value': float(self.value),
            'type': str(self.type),
            'unit': str(self.unit),
            'timestamp': timestamp,
            'source': str(self.source),
            'device_id': str(self.device_id) if self.device_id else None
        }
