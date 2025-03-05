from dataclasses import dataclass
from datetime import datetime

@dataclass
class Measurement:
    """Single measurement structure for any type of metric"""
    device_id: str
    device_name: str
    name: str       
    value: float   
    type: str       
    unit: str       
    timestamp_utc: datetime  
    utc_offset: int

    def serialize(self) -> dict:
        """Serialize measurement for JSON transmission"""
        return {
            'device_id': str(self.device_id),
            'device_name': str(self.device_name),
            'name': str(self.name),
            'value': float(self.value),
            'type': str(self.type),
            'unit': str(self.unit),
            'timestamp_utc': self.timestamp_utc.isoformat(),
            'utc_offset': self.utc_offset
        }
