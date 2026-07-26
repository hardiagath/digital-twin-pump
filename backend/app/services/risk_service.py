from typing import Optional

# Thresholds per sensor for each risk level
SENSOR_THRESHOLDS = {
    "temperature": {"warning": 85.0,  "critical": 95.0},
    "vibration":   {"warning": 4.0,   "critical": 6.0},
    "pressure":    {"warning": 3.5,   "critical": 2.5},
    "rpm":         {"warning": 1300.0, "critical": 1200.0},
    "flow_rate":   {"warning": 90.0,  "critical": 70.0},
}

# Sensors where LOWER value = worse 
INVERSE_SENSORS = {"pressure", "rpm", "flow_rate"}

PART_MESSAGES = {
    "bearing":  "Abnormal temperature/vibration detected. Possible bearing wear or lubrication failure.",
    "seal":     "Pressure drop detected. Possible seal degradation or leakage.",
    "motor":    "RPM deviation detected. Possible motor fault or electrical issue.",
    "impeller": "Flow rate drop detected. Possible impeller wear, blockage, or cavitation.",
    "unknown":  "Multiple sensor anomalies detected. Full inspection recommended.",
}


def classify_sensor(sensor: str, value: float) -> str:
    """Return risk level for a single sensor value."""
    thresholds = SENSOR_THRESHOLDS.get(sensor)
    if not thresholds:
        return "normal"

    if sensor in INVERSE_SENSORS:
        if value <= thresholds["critical"]:
            return "critical"
        elif value <= thresholds["warning"]:
            return "warning"
    else:
        if value >= thresholds["critical"]:
            return "critical"
        elif value >= thresholds["warning"]:
            return "warning"

    return "normal"


def classify_overall(
    ml_risk: str,
    sensor_readings: dict,
) -> dict:
    """
    Combine ML anomaly score risk with per-sensor threshold checks.
    Returns final risk level and per-sensor breakdown.
    """
    sensor_risks = {
        sensor: classify_sensor(sensor, value)
        for sensor, value in sensor_readings.items()
        if sensor in SENSOR_THRESHOLDS
    }

    priority = {"critical": 2, "warning": 1, "normal": 0}
    worst_sensor_risk = max(
        sensor_risks.values(),
        key=lambda r: priority[r],
        default="normal"
    )

    # Final risk = highest between ML prediction and sensor thresholds
    final_risk = (
        ml_risk
        if priority[ml_risk] >= priority[worst_sensor_risk]
        else worst_sensor_risk
    )

    return {
        "final_risk":    final_risk,
        "ml_risk":       ml_risk,
        "sensor_risks":  sensor_risks,
    }


def get_part_message(pump_part: str) -> str:
    return PART_MESSAGES.get(pump_part, PART_MESSAGES["unknown"])


def get_equipment_status(risk_levels: list) -> str:
    """Derive overall equipment status from a list of risk levels."""
    if "critical" in risk_levels:
        return "critical"
    elif "warning" in risk_levels:
        return "warning"
    return "normal"