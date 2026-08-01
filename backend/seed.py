"""
Seed script for the Digital Twin Pump project.

Creates required data, trains the anomaly detection model,
generates alerts, and optionally generates AI recommendations.
"""
import argparse
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from app.database import SessionLocal, engine, Base
from app.models.models import Equipment, SensorReading, Alert, Recommendation


EQUIPMENT_SEED = dict(
    id=1,
    name="Centrifugal Pump — CP-101",
    type="Centrifugal Pump",
    location="Naphtha Cracker Plant",
    status="normal",
)


def reset_data(db):
    print("Resetting existing data...")
    db.query(Recommendation).delete()
    db.query(Alert).delete()
    db.query(SensorReading).delete()
    db.query(Equipment).delete()
    db.commit()


def ensure_equipment(db):
    existing = db.query(Equipment).filter(Equipment.id == EQUIPMENT_SEED["id"]).first()
    if existing:
        print(f"Equipment #{existing.id} already exists — skipping insert.")
        return
    db.add(Equipment(**EQUIPMENT_SEED))
    db.commit()
    print(f"Inserted equipment: {EQUIPMENT_SEED['name']}")


def run_step(description: str, script_relpath: str):
    print(f"\n--- {description} ---")
    script_path = os.path.join(BASE_DIR, script_relpath)
    result = subprocess.run([sys.executable, script_path], cwd=BASE_DIR)
    if result.returncode != 0:
        raise SystemExit(f"Step failed: {description}")


def generate_recommendations(db):
    from app.services.recommendation_service import fetch_or_create_recommendation

    alerts = db.query(Alert).filter(Alert.is_resolved == False).all()
    print(f"\n--- Generating recommendations for {len(alerts)} unresolved alerts ---")
    for alert in alerts:
        try:
            fetch_or_create_recommendation(alert.id, db)
            print(f"  Alert {alert.id} ({alert.pump_part}): recommendation generated")
        except Exception as e:
            print(f"  Alert {alert.id}: failed — {e}")


def main():
    parser = argparse.ArgumentParser(description="Seed the digital twin demo database")
    parser.add_argument("--reset", action="store_true", help="Delete existing data first")
    parser.add_argument(
        "--with-recommendations",
        action="store_true",
        help="Also call Gemini to generate recommendations for unresolved alerts",
    )
    args = parser.parse_args()

    print("Creating tables (if needed)...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if args.reset:
            reset_data(db)
        ensure_equipment(db)
    finally:
        db.close()

    run_step("Generating synthetic sensor data", "data/generate_data.py")
    run_step("Ingesting sensor data into DB", "data/ingest_data.py")
    run_step("Training model + scoring all readings", "ml/anomaly_detector.py")
    run_step("Generating alerts from scored readings", "ml/alert_generator.py")

    if args.with_recommendations:
        db = SessionLocal()
        try:
            generate_recommendations(db)
        finally:
            db.close()

    print("\nSeed complete. Start the API with: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
