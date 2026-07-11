from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.models import SensorReading
from app.schemas.schemas import SensorReadingResponse, SensorReadingCreate
from typing import List

router = APIRouter(prefix="/sensors", tags=["Sensors"])

@router.get("/{equipment_id}/latest", response_model=SensorReadingResponse)
def get_latest_reading(equipment_id: int, db: Session = Depends(get_db)):
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.equipment_id == equipment_id)
        .order_by(desc(SensorReading.timestamp))
        .first()
    )
    return reading

@router.get("/{equipment_id}/history", response_model=List[SensorReadingResponse])
def get_sensor_history(
    equipment_id: int,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db)
):
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.equipment_id == equipment_id)
        .order_by(desc(SensorReading.timestamp))
        .limit(limit)
        .all()
    )
    return readings

@router.post("/reading", response_model=SensorReadingResponse)
def add_sensor_reading(payload: SensorReadingCreate, db: Session = Depends(get_db)):
    reading = SensorReading(**payload.dict())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading

@router.get("/{equipment_id}/summary")
def get_sensor_summary(equipment_id: int, db: Session = Depends(get_db)):
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.equipment_id == equipment_id)
        .order_by(desc(SensorReading.timestamp))
        .limit(100)
        .all()
    )

    if not readings:
        return {"message": "No data found"}

    temps = [r.temperature for r in readings]
    vibs = [r.vibration for r in readings]
    pressures = [r.pressure for r in readings]
    rpms = [r.rpm for r in readings]
    flows = [r.flow_rate for r in readings]

    return {
        "equipment_id": equipment_id,
        "sample_size": len(readings),
        "temperature": {"avg": round(sum(temps)/len(temps), 2), "max": max(temps), "min": min(temps)},
        "vibration": {"avg": round(sum(vibs)/len(vibs), 2), "max": max(vibs), "min": min(vibs)},
        "pressure": {"avg": round(sum(pressures)/len(pressures), 2), "max": max(pressures), "min": min(pressures)},
        "rpm": {"avg": round(sum(rpms)/len(rpms), 2), "max": max(rpms), "min": min(rpms)},
        "flow_rate": {"avg": round(sum(flows)/len(flows), 2), "max": max(flows), "min": min(flows)},
    }