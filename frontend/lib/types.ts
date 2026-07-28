export interface Equipment {
  id:         number;
  name:       string;
  type:       string;
  location:   string;
  status:     "normal" | "warning" | "critical";
  created_at: string;
}

export interface SensorReading {
  id:            number;
  equipment_id:  number;
  temperature:   number;
  vibration:     number;
  pressure:      number;
  rpm:           number;
  flow_rate:     number;
  anomaly_score: number;
  risk_level:    "normal" | "warning" | "critical";
  pump_part:     string | null;
  timestamp:     string;
}

export interface Alert {
  id:           number;
  equipment_id: number;
  pump_part:    string;
  risk_level:   "normal" | "warning" | "critical";
  message:      string;
  is_resolved:  boolean;
  created_at:   string;
}

export interface AlertsByPart {
  equipment_id: number;
  parts: {
    [part: string]: {
      status:   "normal" | "warning" | "critical";
      message:  string;
      alert_id: number | null;
    };
  };
}

export interface Recommendation {
  id:             number;
  alert_id:       number;
  equipment_id:   number;
  pump_part:      string;
  recommendation: string;
  generated_at:   string;
}

export interface AlertsSummary {
  total:          number;
  active:         number;
  critical:       number;
  warning:        number;
  active_by_part: { [part: string]: number };
}

export interface SensorSummary {
  equipment_id: number;
  latest_reading: SensorReading;
  average_values: {
    temperature: number;
    vibration: number;
    pressure: number;
    rpm: number;
    flow_rate: number;
  };
}