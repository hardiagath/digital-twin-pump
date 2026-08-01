"use client";
import { useCallback, useEffect, useState } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import TimeRangeSelector from "@/components/trends/TimeRangeSelector";
import SensorTrendChart from "@/components/trends/SensorTrendChart";
import AnomalyTrendChart from "@/components/trends/AnomalyTrendChart";
import RiskDistributionChart from "@/components/trends/RiskDistributionChart";
import StatCard from "@/components/StatCard";
import {
  getSensorTrends,
  getAnomalyTrend,
  getSensorStats,
} from "@/lib/api";
import {
  SensorTrendsResponse,
  AnomalyTrendResponse,
  SensorStatsResponse,
} from "@/lib/types";

const EQUIPMENT_ID = 1;

const STAT_FIELDS: { key: keyof SensorStatsResponse["stats"]; label: string; unit: string }[] = [
  { key: "temperature", label: "Temperature", unit: "°C" },
  { key: "vibration",   label: "Vibration",   unit: "mm/s" },
  { key: "pressure",    label: "Pressure",    unit: "bar" },
  { key: "rpm",         label: "RPM",         unit: "rpm" },
  { key: "flow_rate",   label: "Flow Rate",   unit: "m³/h" },
];

export default function TrendsPage() {
  const [hours, setHours] = useState(24);
  const [trends, setTrends] = useState<SensorTrendsResponse | null>(null);
  const [anomaly, setAnomaly] = useState<AnomalyTrendResponse | null>(null);
  const [stats, setStats] = useState<SensorStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [t, a, s] = await Promise.all([
        getSensorTrends(EQUIPMENT_ID, hours),
        getAnomalyTrend(EQUIPMENT_ID, hours),
        getSensorStats(EQUIPMENT_ID, hours),
      ]);
      setTrends(t);
      setAnomaly(a);
      setStats(s);
    } catch (e) {
      console.error("Failed to fetch trend data", e);
    } finally {
      setLoading(false);
    }
  }, [hours]);

  useEffect(() => {
    (async () => {
      await fetchAll();
    })();
    const interval = setInterval(fetchAll, 30000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  return (
    <ProtectedRoute>
      <main className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h1 className="text-2xl font-medium tracking-tight">Trends</h1>
            <p className="text-sm text-muted-foreground mt-0.5">
              Sensor history, anomaly score, and risk distribution
            </p>
          </div>
          <TimeRangeSelector value={hours} onChange={setHours} />
        </div>

        {loading && !trends ? (
          <p className="text-sm text-muted-foreground animate-pulse">Loading trends...</p>
        ) : (
          <>
            {stats && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {STAT_FIELDS.map((f) => {
                  const s = stats.stats[f.key];
                  return (
                    <StatCard
                      key={f.key}
                      title={f.label}
                      value={s ? s.avg : "--"}
                      unit={f.unit}
                      subtitle={s ? `min ${s.min} · max ${s.max}` : "No data"}
                    />
                  );
                })}
              </div>
            )}

            {trends && trends.data.length > 0 ? (
              <SensorTrendChart data={trends.data} />
            ) : (
              <div className="card p-6 text-center text-muted-foreground text-sm">
                No sensor data in this time window yet.
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2">
                {anomaly && <AnomalyTrendChart data={anomaly.data} />}
              </div>
              <div>
                {anomaly && <RiskDistributionChart distribution={anomaly.distribution} />}
              </div>
            </div>
          </>
        )}
      </main>
    </ProtectedRoute>
  );
}
