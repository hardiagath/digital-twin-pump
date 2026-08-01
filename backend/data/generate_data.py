import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(DATA_DIR, "pump_sensor_data.csv")

np.random.seed(42)
n = 2000
timestamps = [datetime.now() - timedelta(minutes=i) for i in range(n)]

# Normal operating ranges for a centrifugal pump
temperature = np.random.normal(75, 3, n)
vibration = np.random.normal(2.5, 0.3, n)
pressure = np.random.normal(4.5, 0.2, n)
rpm = np.random.normal(1480, 20, n)
flow_rate = np.random.normal(120, 5, n)

# Inject anomalies at random points (simulate real faults)
fault_indices = np.random.choice(n, size=80, replace=False)
temperature[fault_indices] += np.random.uniform(15, 30, 80)    # overheating
vibration[fault_indices] += np.random.uniform(2, 5, 80)        # bearing fault
pressure[fault_indices] -= np.random.uniform(1, 2, 80)         # seal leak
rpm[fault_indices] -= np.random.uniform(100, 200, 80)          # motor issue
flow_rate[fault_indices] -= np.random.uniform(20, 40, 80)      # impeller fault

df = pd.DataFrame({
    "timestamp": timestamps,
    "equipment_id": 1,
    "temperature": np.round(temperature, 2),
    "vibration": np.round(vibration, 2),
    "pressure": np.round(pressure, 2),
    "rpm": np.round(rpm, 2),
    "flow_rate": np.round(flow_rate, 2)
})

df.to_csv(OUT_PATH, index=False)
print(f"Dataset created: {len(df)} rows, {len(fault_indices)} anomalies injected")