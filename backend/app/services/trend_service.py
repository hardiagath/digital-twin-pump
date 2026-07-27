from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.models import SensorReading, Alert
from datetime import datetime, timedelta


SENSOR_FIELDS = ["temperature", "vibration", "pressure", "rpm", "flow_rate"]


def get_hourly_averages(equipment_id: int, hours: int, db: Session) -> list:
    """
    Return hourly average sensor values for the last N hours.
    Used by frontend trend charts.
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    readings = (
        db.query(SensorReading)
        .filter(
            SensorReading.equipment_id == equipment_id,
            SensorReading.timestamp    >= since,
        )
        .order_by(SensorReading.timestamp)
        .all()
    )

    if not readings:
        return []

    # Group by hour manually — works across all DB engines
    buckets = {}
    for r in readings:
        hour_key = r.timestamp.strftime("%Y-%m-%d %H:00")
        if hour_key not in buckets:
            buckets[hour_key] = {f: [] for f in SENSOR_FIELDS}
            buckets[hour_key]["anomaly_score"] = []
        for f in SENSOR_FIELDS:
            buckets[hour_key][f].append(getattr(r, f))
        buckets[hour_key]["anomaly_score"].append(r.anomaly_score)

    result = []
    for hour, values in sorted(buckets.items()):
        entry = {"timestamp": hour}
        for f in SENSOR_FIELDS:
            entry[f] = round(sum(values[f]) / len(values[f]), 3)
        entry["anomaly_score"] = round(
            sum(values["anomaly_score"]) / len(values["anomaly_score"]), 3
        )
        result.append(entry)

    return result


def get_anomaly_trend(equipment_id: int, hours: int, db: Session) -> dict:
    """
    Return anomaly score trend with risk level distribution.
    Used by anomaly score history chart.
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    readings = (
        db.query(SensorReading)
        .filter(
            SensorReading.equipment_id == equipment_id,
            SensorReading.timestamp    >= since,
        )
        .order_by(SensorReading.timestamp)
        .all()
    )

    if not readings:
        return {"data": [], "distribution": {}}

    data = [
        {
            "timestamp":     r.timestamp.strftime("%Y-%m-%d %H:%M"),
            "anomaly_score": r.anomaly_score,
            "risk_level":    r.risk_level,
            "pump_part":     r.pump_part,
        }
        for r in readings
    ]

    distribution = {"normal": 0, "warning": 0, "critical": 0}
    for r in readings:
        distribution[r.risk_level] = distribution.get(r.risk_level, 0) + 1

    return {
        "data":         data,
        "distribution": distribution,
        "total":        len(readings),
    }


def get_sensor_stats(equipment_id: int, hours: int, db: Session) -> dict:
    """
    Return min, max, avg per sensor for the given time window.
    Used by dashboard summary cards.
    """
    since = datetime.utcnow() - timedelta(hours=hours)

    readings = (
        db.query(SensorReading)
        .filter(
            SensorReading.equipment_id == equipment_id,
            SensorReading.timestamp    >= since,
        )
        .all()
    )

    if not readings:
        return {}

    result = {}
    for field in SENSOR_FIELDS:
        values = [getattr(r, field) for r in readings if getattr(r, field) is not None]
        if values:
            result[field] = {
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "avg": round(sum(values) / len(values), 2),
            }

    return result