import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: { "Content-Type": "application/json" },
});

// ── Equipment ──
export const getEquipment = () =>
  api.get("/equipment/").then((r) => r.data);

export const getEquipmentStatus = (id: number) =>
  api.get(`/equipment/${id}/status`).then((r) => r.data);

// ── Sensors ──
export const getLatestReading = (id: number) =>
  api.get(`/sensors/${id}/latest`).then((r) => r.data);

export const getSensorHistory = (id: number, limit = 100) =>
  api.get(`/sensors/${id}/history?limit=${limit}`).then((r) => r.data);

export const getSensorSummary = (id: number) =>
  api.get(`/sensors/${id}/summary`).then((r) => r.data);

export const classifyReading = (payload: object) =>
  api.post("/sensors/classify", payload).then((r) => r.data);

// ── Alerts ──
export const getAlertsSummary = () =>
  api.get("/alerts/summary").then((r) => r.data);

export const getActiveAlerts = (id: number) =>
  api.get(`/alerts/${id}/active`).then((r) => r.data);

export const getAlertsByPart = (id: number) =>
  api.get(`/alerts/${id}/by-part`).then((r) => r.data);

export const resolveAlert = (alertId: number) =>
  api.patch(`/alerts/${alertId}/resolve`).then((r) => r.data);

// ── Recommendations ──
export const getRecommendation = (alertId: number) =>
  api.get(`/recommendations/alert/${alertId}`).then((r) => r.data);

// ── Trends ──
export const getSensorTrends = (id: number, hours = 24) =>
  api.get(`/trends/${id}/sensors?hours=${hours}`).then((r) => r.data);

export const getAnomalyTrend = (id: number, hours = 24) =>
  api.get(`/trends/${id}/anomaly?hours=${hours}`).then((r) => r.data);

export const getSensorStats = (id: number, hours = 24) =>
  api.get(`/trends/${id}/stats?hours=${hours}`).then((r) => r.data);