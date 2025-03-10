from dataclasses import dataclass
from datetime import datetime

@dataclass
class MeasurementDTO:
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
            'timestamp_utc': self.timestamp_utc,
            'utc_offset': self.utc_offset
        }

@dataclass
class CryptoMetricDTO:
    collector_type: str
    device_id: str
    device_name: str
    currency_pair: str
    price: float
    bid: float
    ask: float

    def serialize(self) -> dict:
        """Serialize crypto metric for JSON transmission"""     
        return {
            'collector_type': str(self.collector_type),
            'device_id': str(self.device_id),
            'device_name': str(self.device_name),
            'currency_pair': str(self.currency_pair),
            'price': float(self.price),
            'bid': float(self.bid),
            'ask': float(self.ask)
        }
    
@dataclass
class SystemMetricDTO:
    collector_type: str
    device_id: str
    device_name: str
    cpu_load: float
    ram_usage: float
    network_sent: float

    def serialize(self) -> dict:        
        return {
            'collector_type': str(self.collector_type),
            'device_id': str(self.device_id),
            'device_name': str(self.device_name),
            'cpu_load': float(self.cpu_load),
            'ram_usage': float(self.ram_usage),
            'network_sent': float(self.network_sent)
        }