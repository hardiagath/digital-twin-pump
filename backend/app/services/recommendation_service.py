import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import Alert, Equipment, SensorReading, Recommendation
from app.services.gemini_service import get_recommendation


def _build_context(alert: Alert, db: Session) -> dict:
    """Gather all context needed for a rich Gemini prompt."""

    equipment = db.query(Equipment).filter(
        Equipment.id == alert.equipment_id
    ).first()

    # Latest 10 readings to determine trend direction
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.equipment_id == alert.equipment_id)
        .order_by(desc(SensorReading.timestamp))
        .limit(10)
        .all()
    )

    def get_trend(values: list) -> str:
        if len(values) < 2:
            return "stable"
        diff = values[0] - values[-1]
        if diff > 0.5:
            return "rising"
        elif diff < -0.5:
            return "falling"
        return "stable"

    # Build per-sensor context with value, z-score, and trend
    NORMAL_RANGES = {
        "temperature": (75.0,  3.0),
        "vibration":   (2.5,   0.3),
        "pressure":    (4.5,   0.2),
        "rpm":         (1480.0, 20.0),
        "flow_rate":   (120.0,  5.0),
    }

    latest  = readings[0] if readings else None
    sensors = {}

    for field, (mean, std) in NORMAL_RANGES.items():
        value  = getattr(latest, field, 0) if latest else 0
        values = [getattr(r, field, 0) for r in readings]
        sensors[field] = {
            "value":   round(value, 2),
            "z_score": round(abs((value - mean) / std), 2),
            "trend":   get_trend(values),
        }

    return {
        "equipment_name": equipment.name if equipment else "Unknown Pump",
        "pump_part":      alert.pump_part or "unknown",
        "risk_level":     alert.risk_level,
        "sensors":        sensors,
    }


def fetch_or_create_recommendation(alert_id: int, db: Session) -> Recommendation:
    """
    Return existing recommendation if already generated,
    otherwise call Gemini and store the result.
    """
    # Return cached recommendation if it exists
    existing = db.query(Recommendation).filter(
        Recommendation.alert_id == alert_id
    ).first()
    if existing:
        return existing

    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise ValueError(f"Alert {alert_id} not found")

    context        = _build_context(alert, db)
    recommendation_text = get_recommendation(context)

    recommendation = Recommendation(
        alert_id=alert_id,
        equipment_id=alert.equipment_id,
        pump_part=alert.pump_part,
        recommendation=recommendation_text,
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)

    return recommendation