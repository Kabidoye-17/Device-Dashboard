from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class MeasurementType(Base):
    __tablename__ = 'measurement_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    measurements = relationship("Measurement", back_populates="type")

class Unit(Base):
    __tablename__ = 'units'
    
    id = Column(Integer, primary_key=True)
    unit_name = Column(String(20), unique=True, nullable=False)
    measurements = relationship("Measurement", back_populates="unit")

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    measurements = relationship("Measurement", back_populates="source")

class Measurement(Base):
    __tablename__ = 'measurements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    type_id = Column(Integer, ForeignKey('measurement_types.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('units.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    
    type = relationship("MeasurementType", back_populates="measurements")
    unit = relationship("Unit", back_populates="measurements")
    source = relationship("Source", back_populates="measurements")
