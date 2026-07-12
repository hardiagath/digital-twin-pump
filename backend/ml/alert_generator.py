import os
import sys
from itertools import groupby

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.database import SessionLocal
from app.models.models import SensorReading, Alert, Equipment

# Trigger alert only after N consecutive anomalous readings
CONSECUTIVE_THRESHOLD = 3
MAX_TIME_GAP_SECONDS  = 120   # 2 min gap = not consecutive

PART_MESSAGES = {
    "bearing":  "Abnormal temperature and vibration detected. Possible bearing wear or lubrication failure.",
    "seal":     "Pressure drop detected. Possible seal degradation or leakage.",
    "motor":    "RPM deviation detected. Possible motor fault or electrical issue.",
    "impeller": "Flow rate drop detected. Possible impeller wear, blockage, or cavitation.",
    "unknown":  "Multiple sensor anomalies detected. Full inspection recommended.",
}


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
            group_list   = list(group)
            consecutive  = 1

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
                    pump_part = getattr(current, "pump_part", None) or "unknown"

                    # Skip if unresolved alert already exists for this part
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
                        message=PART_MESSAGES.get(pump_part, PART_MESSAGES["unknown"]),
                    )
                    db.add(alert)
                    alerts_created += 1

                    # Update equipment status
                    equipment = (
                        db.query(Equipment)
                        .filter(Equipment.id == equipment_id)
                        .first()
                    )
                    if equipment:
                        if current.risk_level == "critical":
                            equipment.status = "critical"
                        elif equipment.status == "normal":
                            equipment.status = "warning"

        db.commit()
        print(f"Alerts created: {alerts_created}")

        # Print summary
        alerts = db.query(Alert).all()
        print(f"Total alerts in DB: {len(alerts)}")

    except Exception as e:
        db.rollback()
        print(f"Error during alert generation: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 40)
    print("Generating alerts...")
    generate_alerts()
    print("=" * 40)