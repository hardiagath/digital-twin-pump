from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.trend_service import (
    get_hourly_averages,
    get_anomaly_trend,
    get_sensor_stats,
)

router = APIRouter(prefix="/trends", tags=["Trends"])


@router.get("/{equipment_id}/sensors")
def sensor_trends(
    equipment_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """
    Hourly averaged sensor readings for the last N hours.
    Default 24h, max 7 days (168h).
    """
    data = get_hourly_averages(equipment_id, hours, db)
    return {
        "equipment_id": equipment_id,
        "hours":        hours,
        "data_points":  len(data),
        "data":         data,
    }


@router.get("/{equipment_id}/anomaly")
def anomaly_trend(
    equipment_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """
    Anomaly score history with risk level distribution.
    """
    result = get_anomaly_trend(equipment_id, hours, db)
    return {
        "equipment_id": equipment_id,
        "hours":        hours,
        **result,
    }


@router.get("/{equipment_id}/stats")
def sensor_stats(
    equipment_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """
    Min, max, avg per sensor for the given time window.
    """
    stats = get_sensor_stats(equipment_id, hours, db)
    return {
        "equipment_id": equipment_id,
        "hours":        hours,
        "stats":        stats,
    }