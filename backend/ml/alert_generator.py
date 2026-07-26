import os
import sys
from itertools import groupby

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.database import SessionLocal
from app.models.models import SensorReading, Alert, Equipment
from app.services.risk_service import get_part_message, get_equipment_status

CONSECUTIVE_THRESHOLD = 3
MAX_TIME_GAP_SECONDS  = 120


def generate_alerts():
    db = SessionLocal()
    try:
        readings = (
            db.query(SensorReading)
            .filter(SensorReading.risk_level.in_(["warning", "critical"]))
            .order_by(SensorReading.equipment_id, SensorReading.timestamp)
            .all()
        )

        if not readings:
            print("No anomalous readings found.")
            return

        print(f"Processing {len(readings)} anomalous readings...")
        alerts_created = 0

        grouped = groupby(readings, key=lambda r: r.equipment_id)

        for equipment_id, group in grouped:
            group_list  = list(group)
            consecutive = 1

            for i in range(1, len(group_list)):
                current  = group_list[i]
                previous = group_list[i - 1]

                time_diff = (
                    current.timestamp - previous.timestamp
                ).total_seconds()

                if time_diff <= MAX_TIME_GAP_SECONDS:
                    consecutive += 1
                else:
                    consecutive = 1

                if consecutive == CONSECUTIVE_THRESHOLD:
                    pump_part = current.pump_part or "unknown"

                    existing = (
                        db.query(Alert)
                        .filter(
                            Alert.equipment_id == equipment_id,
                            Alert.pump_part    == pump_part,
                            Alert.is_resolved  == False,
                        )
                        .first()
                    )
                    if existing:
                        continue

                    alert = Alert(
                        equipment_id=equipment_id,
                        pump_part=pump_part,
                        risk_level=current.risk_level,
                        message=get_part_message(pump_part),
                    )
                    db.add(alert)
                    alerts_created += 1

            # Update equipment status based on all its alerts
            all_alerts = (
                db.query(Alert)
                .filter(
                    Alert.equipment_id == equipment_id,
                    Alert.is_resolved  == False,
                )
                .all()
            )
            risk_levels = [a.risk_level for a in all_alerts]
            equipment   = (
                db.query(Equipment)
                .filter(Equipment.id == equipment_id)
                .first()
            )
            if equipment:
                equipment.status = get_equipment_status(risk_levels)

        db.commit()

        total_alerts = db.query(Alert).count()
        print(f"Alerts created : {alerts_created}")
        print(f"Total in DB    : {total_alerts}")

        from sqlalchemy import func
        dist = (
            db.query(Alert.pump_part, Alert.risk_level, func.count())
            .group_by(Alert.pump_part, Alert.risk_level)
            .all()
        )
        print("\nAlert distribution:")
        for part, level, count in dist:
            print(f"  {part:<12} {level:<10} → {count}")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 45)
    generate_alerts()
    print("=" * 45)