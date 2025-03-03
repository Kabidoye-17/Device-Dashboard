from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class MetricType(Base):
    __tablename__ = 'metric_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    metric_measurements = relationship("MetricMeasurement", back_populates="type")

class Unit(Base):
    __tablename__ = 'units'
    
    id = Column(Integer, primary_key=True)
    unit_name = Column(String(20), unique=True, nullable=False)
    metric_measurements = relationship("MetricMeasurement", back_populates="unit")

class Device(Base):
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, nullable=False, index=True)
    device_name = Column(String(100), unique=True, nullable=False, index=True)
    
    metric_measurements = relationship(
        "MetricMeasurement", back_populates="device", cascade="all, delete-orphan"
    )

class MetricMeasurement(Base):
    __tablename__ = 'metric_measurements'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(100), ForeignKey('devices.device_id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    type_id = Column(Integer, ForeignKey('metric_types.id'), nullable=False, index=True)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=False, index=True)
    timestamp_utc = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    utc_offset = Column(Integer, nullable=False)    

    type = relationship("MetricType", back_populates="metric_measurements")
    unit = relationship("Unit", back_populates="metric_measurements")
    device = relationship("Device", back_populates="metric_measurements")

    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device.device_name,
            'name': self.name,
            'value': self.value,
            'type': self.type.name,
            'unit': self.unit.unit_name,
            'timestamp_utc': self.timestamp_utc,
            'utc_offset': self.utc_offset
        }
