"use client";
import { useCallback, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { SlidersHorizontal } from "lucide-react";
import ProtectedRoute from "@/components/ProtectedRoute";
import HotspotCalibrator from "@/components/pump/HotspotCalibrator";
import StatusBadge from "@/components/StatusBadge";
import { getAlertsByPart } from "@/lib/api";
import { AlertsByPart, HotspotPosition, PumpPart } from "@/lib/types";
import { RiskLevel } from "@/lib/utils";
import { DEFAULT_HOTSPOTS } from "@/lib/hotspots";

const PumpViewer = dynamic(() => import("@/components/pump/PumpViewer"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[520px] rounded-3xl border border-border flex items-center justify-center">
      <p className="text-sm text-muted-foreground animate-pulse">Loading 3D viewer...</p>
    </div>
  ),
});

const EQUIPMENT_ID = 1;
const PART_ORDER: PumpPart[] = ["motor", "bearing", "seal", "impeller"];

export default function PumpPage() {
  const [byPart, setByPart]     = useState<AlertsByPart | null>(null);
  const [hotspots, setHotspots] = useState<HotspotPosition[]>(DEFAULT_HOTSPOTS);
  const [calibrating, setCalibrating] = useState(false);
  const [activePart, setActivePart]   = useState<PumpPart>("motor");

  const fetchStatus = useCallback(async () => {
    try {
      const data = await getAlertsByPart(EQUIPMENT_ID);
      setByPart(data);
    } catch (e) {
      console.error("Failed to fetch part status", e);
    }
  }, []);

  useEffect(() => {
    (async () => {
      await fetchStatus();
    })();
    const interval = setInterval(fetchStatus, 10000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const partStatus: Partial<Record<PumpPart, RiskLevel>> = {};
  if (byPart) {
    for (const part of PART_ORDER) {
      partStatus[part] = (byPart.parts[part]?.status as RiskLevel) ?? "normal";
    }
  }

  const handleCalibrateClick = (point: [number, number, number]) => {
    setHotspots((prev) =>
      prev.map((h) => (h.part === activePart ? { ...h, position: point } : h))
    );
  };

  return (
    <ProtectedRoute>
      <main className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-medium tracking-tight">3D Pump Viewer</h1>
            <p className="text-sm text-muted-foreground mt-0.5">
              Drag to rotate, scroll to zoom. Hover a marker for live status.
            </p>
          </div>
          <button
            onClick={() => setCalibrating((c) => !c)}
            className={`flex items-center gap-2 text-sm rounded-full px-4 py-2 border transition-colors ${
              calibrating
                ? "border-accent bg-accent/10 text-foreground"
                : "border-border text-muted-foreground hover:text-foreground"
            }`}
          >
            <SlidersHorizontal size={14} />
            {calibrating ? "Exit calibration" : "Calibrate hotspots"}
          </button>
        </div>

        {calibrating && (
          <HotspotCalibrator
            hotspots={hotspots}
            activePart={activePart}
            onSelectPart={setActivePart}
            onReset={() => setHotspots(DEFAULT_HOTSPOTS)}
          />
        )}

        <PumpViewer
          hotspots={hotspots}
          partStatus={partStatus}
          calibrating={calibrating}
          onCalibrateClick={handleCalibrateClick}
        />

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {PART_ORDER.map((part) => {
            const info = byPart?.parts[part];
            return (
              <div key={part} className="card p-4 flex flex-col gap-1.5">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold capitalize">{part}</p>
                  <StatusBadge level={(info?.status as RiskLevel) ?? "normal"} />
                </div>
                <p className="text-xs text-muted-foreground">
                  {info?.message ?? "Operating normally"}
                </p>
              </div>
            );
          })}
        </div>
      </main>
    </ProtectedRoute>
  );
}
