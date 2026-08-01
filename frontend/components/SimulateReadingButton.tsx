"use client";
import { useState } from "react";
import { Zap, Loader2 } from "lucide-react";
import { classifyReading } from "@/lib/api";

interface Props {
  equipmentId: number;
  onSimulated: () => void;
}

const NORMAL = {
  temperature: { mean: 75,   std: 3 },
  vibration:   { mean: 2.5,  std: 0.3 },
  pressure:    { mean: 4.5,  std: 0.2 },
  rpm:         { mean: 1480, std: 20 },
  flow_rate:   { mean: 120,  std: 5 },
};

const gaussian = (mean: number, std: number) => {
  // Box-Muller
  const u = 1 - Math.random();
  const v = Math.random();
  const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  return mean + z * std;
};

function generateReading(equipmentId: number, fault: boolean) {
  const r = {
    equipment_id: equipmentId,
    temperature: gaussian(NORMAL.temperature.mean, NORMAL.temperature.std),
    vibration:   gaussian(NORMAL.vibration.mean, NORMAL.vibration.std),
    pressure:    gaussian(NORMAL.pressure.mean, NORMAL.pressure.std),
    rpm:         gaussian(NORMAL.rpm.mean, NORMAL.rpm.std),
    flow_rate:   gaussian(NORMAL.flow_rate.mean, NORMAL.flow_rate.std),
  };

  if (fault) {
   
    const kind = Math.floor(Math.random() * 4);
    if (kind === 0) {
      r.temperature += 20 + Math.random() * 15; // overheating -> bearing
      r.vibration += 3 + Math.random() * 3;
    } else if (kind === 1) {
      r.pressure -= 1 + Math.random(); // seal leak
    } else if (kind === 2) {
      r.rpm -= 150 + Math.random() * 100; // motor fault
    } else {
      r.flow_rate -= 30 + Math.random() * 20; // impeller fault
    }
  }

  return {
    ...r,
    temperature: Math.round(r.temperature * 100) / 100,
    vibration:   Math.round(r.vibration * 100) / 100,
    pressure:    Math.round(r.pressure * 100) / 100,
    rpm:         Math.round(r.rpm * 100) / 100,
    flow_rate:   Math.round(r.flow_rate * 100) / 100,
  };
}

export default function SimulateReadingButton({ equipmentId, onSimulated }: Props) {
  const [loading, setLoading] = useState<"normal" | "fault" | null>(null);
  const [lastResult, setLastResult] = useState<string | null>(null);

  const simulate = async (fault: boolean) => {
    setLoading(fault ? "fault" : "normal");
    setLastResult(null);
    try {
      const payload = generateReading(equipmentId, fault);
      const result = await classifyReading(payload);
      setLastResult(
        `${result.risk.final_risk.toUpperCase()} · ${result.pump_part} · score ${result.anomaly_score.toFixed(2)}`
      );
      onSimulated();
    } catch (e) {
      console.error("Simulate reading failed", e);
      setLastResult("Failed to submit reading -- check backend logs");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="flex items-center gap-3 flex-wrap">
      <button
        onClick={() => simulate(false)}
        disabled={loading !== null}
        className="flex items-center gap-1.5 text-sm rounded-full px-3.5 py-2 border border-border text-muted-foreground hover:text-foreground hover:bg-surface-hover transition-colors disabled:opacity-50"
      >
        {loading === "normal" ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
        Simulate normal reading
      </button>
      <button
        onClick={() => simulate(true)}
        disabled={loading !== null}
        className="flex items-center gap-1.5 text-sm rounded-full px-3.5 py-2 border border-risk-critical/40 text-risk-critical hover:bg-risk-critical/10 transition-colors disabled:opacity-50"
      >
        {loading === "fault" ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
        Simulate fault
      </button>
      {lastResult && <span className="text-xs text-muted-foreground">{lastResult}</span>}
    </div>
  );
}
