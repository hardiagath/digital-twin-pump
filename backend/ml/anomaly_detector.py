import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# Resolved paths relative to this file
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH  = os.path.join(BASE_DIR, "ml", "isolation_forest.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "ml", "scaler.pkl")
DATA_PATH   = os.path.join(BASE_DIR, "data", "pump_sensor_data.csv")

FEATURES = ["temperature", "vibration", "pressure", "rpm", "flow_rate"]

# Normal operating ranges (mean, std) for Z-score calculation
NORMAL_RANGES = {
    "temperature": (75.0,  3.0),
    "vibration":   (2.5,   0.3),
    "pressure":    (4.5,   0.2),
    "rpm":         (1480.0, 20.0),
    "flow_rate":   (120.0,  5.0),
}

# Sensor → pump part mapping
SENSOR_PART_MAP = {
    "temperature": "bearing",
    "vibration":   "bearing",
    "pressure":    "seal",
    "rpm":         "motor",
    "flow_rate":   "impeller",
}


# Load model and scaler once
_model  = None
_scaler = None

def load_artifacts():
    global _model, _scaler
    if _model is None or _scaler is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Run train() first."
            )
        if not os.path.exists(SCALER_PATH):
            raise FileNotFoundError(
                f"Scaler not found at {SCALER_PATH}. Run train() first."
            )
        _model  = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
    return _model, _scaler


# Most affected pump part
def identify_pump_part(z_scores: dict) -> str:
    worst_sensor = max(z_scores, key=lambda k: z_scores[k])
    return SENSOR_PART_MAP.get(worst_sensor, "unknown")


# Mapping
def get_risk_level(score: float) -> str:
    if score >= 0.6:
        return "critical"
    elif score >= 0.3:
        return "warning"
    return "normal"


# Train and save model
def train():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    missing = [f for f in FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")

    X = df[FEATURES]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )
    model.fit(X_scaled)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    print(f"Model saved  → {MODEL_PATH}")
    print(f"Scaler saved → {SCALER_PATH}")

def score_reading(reading: dict) -> dict:
    model, scaler = load_artifacts()

    X = pd.DataFrame([{f: reading[f] for f in FEATURES}])
    X_scaled = scaler.transform(X)

    raw_score     = model.decision_function(X_scaled)[0]
    anomaly_score = float(np.clip(1 - (raw_score + 0.5), 0.0, 1.0))
    anomaly_score = round(anomaly_score, 3)

    z_scores = {
        f: round(abs((reading[f] - NORMAL_RANGES[f][0]) / NORMAL_RANGES[f][1]), 3)
        for f in FEATURES
    }

    pump_part  = identify_pump_part(z_scores)
    risk_level = get_risk_level(anomaly_score)

    return {
        "anomaly_score": anomaly_score,
        "risk_level":    risk_level,
        "pump_part":     pump_part,
        "z_scores":      z_scores,
    }


# Batch score all unscored DB readings efficiently
def score_all_readings():
    sys.path.append(BASE_DIR)
    from app.database import SessionLocal
    from app.models.models import SensorReading

    model, scaler = load_artifacts()

    db = SessionLocal()
    try:
        readings = (
            db.query(SensorReading)
            .filter(SensorReading.anomaly_score == 0)
            .all()
        )

        if not readings:
            print("No unscored readings found.")
            return

        print(f"Scoring {len(readings)} readings...")

        # Build DataFrame for batch prediction (efficient)
        df = pd.DataFrame([
            {
                "id":          r.id,
                "temperature": r.temperature,
                "vibration":   r.vibration,
                "pressure":    r.pressure,
                "rpm":         r.rpm,
                "flow_rate":   r.flow_rate,
            }
            for r in readings
        ])

        X_scaled    = scaler.transform(df[FEATURES])
        raw_scores  = model.decision_function(X_scaled)
        scores      = np.clip(1 - (raw_scores + 0.5), 0.0, 1.0)

        # Z-scores for pump part identification
        z_score_df = pd.DataFrame({
            f: np.abs((df[f] - NORMAL_RANGES[f][0]) / NORMAL_RANGES[f][1])
            for f in FEATURES
        })
        worst_sensors = z_score_df.idxmax(axis=1)

        # Map results back to DB objects
        id_to_reading = {r.id: r for r in readings}

        for i, row in df.iterrows():
            reading               = id_to_reading[row["id"]]
            reading.anomaly_score = round(float(scores[i]), 3)
            reading.risk_level    = get_risk_level(scores[i])
            reading.pump_part     = SENSOR_PART_MAP.get(worst_sensors[i], "unknown")
            
        db.commit()
        print("All readings scored successfully")

        # Print risk distribution for debugging
        dist = {}
        for r in readings:
            dist[r.risk_level] = dist.get(r.risk_level, 0) + 1
        print("Risk distribution:", dist)

    except Exception as e:
        db.rollback()
        print(f"Error during scoring: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 40)
    print("Step 1: Training Isolation Forest...")
    train()
    print("\nStep 2: Scoring all DB readings...")
    score_all_readings()
    print("=" * 40)
    print("ML pipeline complete.")