from datetime import datetime, timezone
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

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    metric_measurements = relationship("MetricMeasurement", back_populates="source")

class MetricMeasurement(Base):
    __tablename__ = 'metric_measurements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    type_id = Column(Integer, ForeignKey('metric_types.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    device_id = Column(String(100), nullable=True)
    
    type = relationship("MetricType", back_populates="metric_measurements")
    unit = relationship("Unit", back_populates="metric_measurements")
    source = relationship("Source", back_populates="metric_measurements")

    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'type': self.type.name,
            'unit': self.unit.unit_name,
            'timestamp': self.timestamp.astimezone(timezone.utc).isoformat(),
            'source': self.source.name,
            'device_id': self.device_id
        }
