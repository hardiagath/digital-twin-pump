import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.models import SensorReading

# Feature columns for training 
FEATURES = ["temperature", "vibration", "pressure", "rpm", "flow_rate"]
MODEL_PATH = "backend/ml/isolation_forest.pkl"
SCALER_PATH = "backend/ml/scaler.pkl"


# Pump part mapping based on which sensor is most anomalous 
def identify_pump_part(row: dict, z_scores: dict) -> str:
    mapping = {
        "temperature": "bearing",
        "vibration":   "bearing",
        "pressure":    "seal",
        "rpm":         "motor",
        "flow_rate":   "impeller"
    }
    worst = max(z_scores, key=lambda k: abs(z_scores[k]))
    return mapping.get(worst, "unknown")


# Risk level
def get_risk_level(score: float) -> str:
    if score >= 0.6:
        return "critical"
    elif score >= 0.3:
        return "warning"
    return "normal"


# Train model
def train():
    df = pd.read_csv("backend/data/pump_sensor_data.csv")
    X = df[FEATURES]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,   # ~5% of data expected to be anomalous
        random_state=42
    )
    model.fit(X_scaled)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print("Model and scaler saved successfully")


# Score a single reading 
def score_reading(reading: dict) -> dict:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    # Normal sensor ranges for Z-score comparison
    normal_ranges = {
        "temperature": (75, 3),
        "vibration":   (2.5, 0.3),
        "pressure":    (4.5, 0.2),
        "rpm":         (1480, 20),
        "flow_rate":   (120, 5)
    }

    values = np.array([[reading[f] for f in FEATURES]])
    scaled = scaler.transform(values)

    raw_score = model.decision_function(scaled)[0]

    # Normalize to 0–1 higher = more anomalous
    anomaly_score = round(float(1 - (raw_score + 0.5)), 3)
    anomaly_score = max(0.0, min(1.0, anomaly_score))

    # Z-scores per feature to find worst offending sensor
    z_scores = {
        f: abs((reading[f] - normal_ranges[f][0]) / normal_ranges[f][1])
        for f in FEATURES
    }

    pump_part = identify_pump_part(reading, z_scores)
    risk_level = get_risk_level(anomaly_score)

    return {
        "anomaly_score": anomaly_score,
        "risk_level": risk_level,
        "pump_part": pump_part,
        "z_scores": z_scores
    }


# Score all unscored DB readings
def score_all_readings():
    db = SessionLocal()
    try:
        readings = (
            db.query(SensorReading)
            .filter(SensorReading.anomaly_score == 0)
            .all()
        )
        print(f"Scoring {len(readings)} readings...")

        for reading in readings:
            data = {
                "temperature": reading.temperature,
                "vibration":   reading.vibration,
                "pressure":    reading.pressure,
                "rpm":         reading.rpm,
                "flow_rate":   reading.flow_rate
            }
            result = score_reading(data)
            reading.anomaly_score = result["anomaly_score"]
            reading.risk_level    = result["risk_level"]

        db.commit()
        print("All readings scored and updated in DB")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Step 1: Training model...")
    train()
    print("Step 2: Scoring all readings...")
    score_all_readings()