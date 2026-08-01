from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EquipmentResponse(BaseModel):
    id: int
    name: str
    type: str
    location: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class SensorReadingResponse(BaseModel):
    id: int
    equipment_id: int
    temperature: float
    vibration: float
    pressure: float
    rpm: float
    flow_rate: float
    anomaly_score: float
    risk_level: str
    pump_part:     Optional[str] = None 
    timestamp: datetime

    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: int
    equipment_id: int
    pump_part: Optional[str]
    risk_level: str
    message: str
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SensorReadingCreate(BaseModel):
    equipment_id: int
    temperature: float
    vibration: float
    pressure: float
    rpm: float
    flow_rate: float

class RecommendationResponse(BaseModel):
    id:             int
    alert_id:       int
    equipment_id:   int
    pump_part:      Optional[str]
    recommendation: str
    generated_at:   datetime

    class Config:
        from_attributes = True


class RecommendationRequest(BaseModel):
    alert_id:     int
    equipment_id: int


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"