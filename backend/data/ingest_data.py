import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.models import SensorReading

def ingest():
    df = pd.read_csv("backend/data/pump_sensor_data.csv")
    db = SessionLocal()

    try:
        records = []
        for _, row in df.iterrows():
            record = SensorReading(
                equipment_id=row["equipment_id"],
                temperature=row["temperature"],
                vibration=row["vibration"],
                pressure=row["pressure"],
                rpm=row["rpm"],
                flow_rate=row["flow_rate"],
                anomaly_score=0,
                risk_level="normal"
            )
            records.append(record)

        db.bulk_save_objects(records)
        db.commit()
        print(f"Successfully ingested {len(records)} records")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ingest()