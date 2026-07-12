from sqlalchemy import Column, Integer, String, Float, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    type = Column(String(50))
    location = Column(String(100))
    status = Column(String(20), default="normal")
    created_at = Column(TIMESTAMP, server_default=func.now())

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    temperature = Column(Float)
    vibration = Column(Float)
    pressure = Column(Float)
    rpm = Column(Float)
    flow_rate = Column(Float)
    anomaly_score = Column(Float, default=0)
    risk_level = Column(String(20), default="normal")
    pump_part = Column(String(50), nullable=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    pump_part = Column(String(50))
    risk_level = Column(String(20))
    message = Column(String(500))
    is_resolved = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())