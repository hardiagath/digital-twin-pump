import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

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
    return (
        db.query(SensorReading)
        .filter(SensorReading.equipment_id == equipment_id)
        .order_by(desc(SensorReading.timestamp))
        .limit(limit)
        .all()
    )


@router.post("/score")
def score_single_reading(payload: SensorReadingCreate, db: Session = Depends(get_db)):
    from ml.anomaly_detector import score_reading as ml_score

    data   = payload.dict()
    result = ml_score(data)

    reading = SensorReading(
        **data,
        anomaly_score=result["anomaly_score"],
        risk_level=result["risk_level"],
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)

    return {
        "reading_id":    reading.id,
        "anomaly_score": result["anomaly_score"],
        "risk_level":    result["risk_level"],
        "pump_part":     result["pump_part"],
        "z_scores":      result["z_scores"],
    }


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

    def stats(values):
        return {
            "avg": round(sum(values) / len(values), 2),
            "max": round(max(values), 2),
            "min": round(min(values), 2),
        }

    return {
        "equipment_id": equipment_id,
        "sample_size":  len(readings),
        "temperature":  stats([r.temperature for r in readings]),
        "vibration":    stats([r.vibration   for r in readings]),
        "pressure":     stats([r.pressure    for r in readings]),
        "rpm":          stats([r.rpm         for r in readings]),
        "flow_rate":    stats([r.flow_rate   for r in readings]),
    }