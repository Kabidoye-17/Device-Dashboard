from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
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
    
    id = Column(Integer, primary_key=True) 
    device_id = Column(String(100), unique=True, nullable=False)  

    details = relationship("DeviceDetails", uselist=False, back_populates="device", cascade="all, delete-orphan")
    metric_measurements = relationship(
        "MetricMeasurement", back_populates="device", cascade="all, delete-orphan"
    )

class DeviceDetails(Base):
    __tablename__ = 'device_details'
    
    id = Column(Integer, primary_key=True) 
    device_id = Column(String(100), ForeignKey('devices.device_id'), unique=True, nullable=False) 
    device_name = Column(String(100), unique=True, nullable=False)  

    device = relationship("Device", back_populates="details")

class MetricMeasurement(Base):
    __tablename__ = 'metric_measurements'
    __table_args__ = (
        Index("idx_device_id_desc", "device_id", "id"),
    )
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(100), ForeignKey('devices.device_id'), nullable=False) 
    name = Column(String(100), nullable=False)  
    value = Column(Float, nullable=False)  
    type_id = Column(Integer, ForeignKey('metric_types.id'), nullable=False, index=True)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=False, index=True)  
    timestamp_utc = Column(DateTime(timezone=True), nullable=False, server_default=func.now())  
    utc_offset = Column(Integer, nullable=False)  

    type = relationship("MetricType", back_populates="metric_measurements")
    unit = relationship("Unit", back_populates="metric_measurements")
    device = relationship("Device", back_populates="metric_measurements")