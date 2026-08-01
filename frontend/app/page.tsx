"use client";
import { useEffect, useState, useCallback } from "react";
import {
  getEquipment,
  getLatestReading,
  getAlertsSummary,
  getActiveAlerts,
  getSensorSummary,
} from "@/lib/api";
import { Equipment, SensorReading, Alert, AlertsSummary, SensorSummary } from "@/lib/types";
import { riskColor, RiskLevel } from "@/lib/utils";
import ProtectedRoute from "@/components/ProtectedRoute";
import StatCard from "@/components/StatCard";
import StatusBadge from "@/components/StatusBadge";
import AlertCard from "@/components/AlertCard";
import SimulateReadingButton from "@/components/SimulateReadingButton";
import { Activity, Bell } from "lucide-react";
import Link from "next/link";

const EQUIPMENT_ID = 1;

function DashboardContent() {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [latest, setLatest] = useState<SensorReading | null>(null);
  const [summary, setSummary] = useState<AlertsSummary | null>(null);
  const [activeAlerts, setActiveAlerts] = useState<Alert[]>([]);
  const [sensorSummary, setSensorSummary] = useState<SensorSummary | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    try {
      const [eq, lat, sum, alerts, sens] = await Promise.all([
        getEquipment(),
        getLatestReading(EQUIPMENT_ID),
        getAlertsSummary(),
        getActiveAlerts(EQUIPMENT_ID),
        getSensorSummary(EQUIPMENT_ID),
      ]);
      setEquipment(eq);
      setLatest(lat);
      setSummary(sum);
      setActiveAlerts(alerts);
      setSensorSummary(sens);
    } catch (e) {
      console.error("Failed to fetch dashboard data", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    (async () => {
      await fetchAll();
    })();
    const interval = setInterval(fetchAll, 10000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-muted-foreground animate-pulse">Loading dashboard...</p>
      </div>
    );
  }

  const pump = equipment[0];
  void sensorSummary; // reserved for a future averages panel

  return (
    <main className="max-w-7xl mx-auto px-4 py-8 space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-medium tracking-tight">Overview</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Centrifugal Pump — Naphtha Cracker Plant
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">Auto-refresh 10s</span>
          <span className="w-2 h-2 rounded-full bg-risk-normal animate-pulse" />
        </div>
      </div>

      {/* Equipment Status */}
      {pump && (
        <div className="card p-5 flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-4">
            <div className="bg-accent/15 rounded-2xl p-3">
              <Activity className="text-accent" size={22} />
            </div>
            <div>
              <p className="font-semibold">{pump.name}</p>
              <p className="text-sm text-muted-foreground">{pump.location}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <StatusBadge level={pump.status as RiskLevel} />
            <Link
              href="/pump"
              className="text-sm text-accent hover:opacity-80 transition-opacity"
            >
              View 3D →
            </Link>
          </div>
        </div>
      )}

      {/* Simulate reading */}
      <SimulateReadingButton equipmentId={EQUIPMENT_ID} onSimulated={fetchAll} />

      {/* Alert Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard title="Total Alerts" value={summary.total} />
          <StatCard title="Active Alerts" value={summary.active} />
          <StatCard
            title="Critical"
            value={summary.critical}
            risk={summary.critical > 0 ? "critical" : undefined}
          />
          <StatCard
            title="Warning"
            value={summary.warning}
            risk={summary.warning > 0 ? "warning" : undefined}
          />
        </div>
      )}

      {/* Latest Sensor Readings */}
      {latest && (
        <div>
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
            Latest Sensor Readings
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <StatCard
              title="Temperature"
              value={latest.temperature}
              unit="°C"
              risk={latest.risk_level as RiskLevel}
            />
            <StatCard
              title="Vibration"
              value={latest.vibration}
              unit="mm/s"
              risk={latest.risk_level as RiskLevel}
            />
            <StatCard
              title="Pressure"
              value={latest.pressure}
              unit="bar"
              risk={latest.risk_level as RiskLevel}
            />
            <StatCard
              title="RPM"
              value={latest.rpm}
              unit="rpm"
              risk={latest.risk_level as RiskLevel}
            />
            <StatCard
              title="Flow Rate"
              value={latest.flow_rate}
              unit="m³/h"
              risk={latest.risk_level as RiskLevel}
            />
          </div>
        </div>
      )}

      {/* Anomaly Score */}
      {latest && (
        <div className="card p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
              Current Anomaly Score
            </h2>
            <StatusBadge level={latest.risk_level as RiskLevel} />
          </div>
          <div className="flex items-center gap-4">
            <div className="flex-1 bg-surface-hover rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${
                  latest.risk_level === "critical"
                    ? "bg-risk-critical"
                    : latest.risk_level === "warning"
                    ? "bg-risk-warning"
                    : "bg-risk-normal"
                }`}
                style={{ width: `${Math.min(latest.anomaly_score * 100, 100)}%` }}
              />
            </div>
            <span className={`text-xl font-medium ${riskColor(latest.risk_level as RiskLevel)}`}>
              {(latest.anomaly_score * 100).toFixed(1)}%
            </span>
          </div>
          {latest.pump_part && (
            <p className="text-xs text-muted-foreground mt-2">
              Most affected part:{" "}
              <span className="capitalize text-foreground">{latest.pump_part}</span>
            </p>
          )}
        </div>
      )}

      {/* Active Alerts */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
            <Bell size={14} />
            Active Alerts ({activeAlerts.length})
          </h2>
          <Link
            href="/pump"
            className="text-xs text-accent hover:opacity-80 transition-opacity"
          >
            View on 3D pump →
          </Link>
        </div>

        {activeAlerts.length === 0 ? (
          <div className="card p-6 text-center text-muted-foreground">
            No active alerts — pump operating normally
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {activeAlerts.map((alert) => (
              <AlertCard key={alert.id} alert={alert} onResolved={fetchAll} />
            ))}
          </div>
        )}
      </div>

    </main>
  );
}

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
