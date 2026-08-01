"use client";
import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, Bounds, Html } from "@react-three/drei";
import type { ThreeEvent } from "@react-three/fiber";
import PumpModel from "./PumpModel";
import Hotspot from "./Hotspot";
import { HotspotPosition, PumpPart } from "@/lib/types";
import { RiskLevel } from "@/lib/utils";

interface Props {
  hotspots:     HotspotPosition[];
  partStatus:   Partial<Record<PumpPart, RiskLevel>>;
  calibrating?: boolean;
  onCalibrateClick?: (point: [number, number, number]) => void;
}

export default function PumpViewer({
  hotspots,
  partStatus,
  calibrating = false,
  onCalibrateClick,
}: Props) {
  const handleClick = (e: ThreeEvent<MouseEvent>) => {
    if (!calibrating) return;
    e.stopPropagation();
    const p = e.point;
    onCalibrateClick?.([
      Math.round(p.x * 100) / 100,
      Math.round(p.y * 100) / 100,
      Math.round(p.z * 100) / 100,
    ]);
  };

  return (
    <div
      className="w-full h-[520px] rounded-3xl overflow-hidden border border-border"
      style={{ cursor: calibrating ? "crosshair" : "grab" }}
    >
      <Canvas camera={{ position: [90, 70, 90], fov: 45 }} shadows>
        <ambientLight intensity={0.7} />
        <directionalLight position={[60, 90, 40]} intensity={1.3} castShadow />
        <directionalLight position={[-60, 30, -40]} intensity={0.4} />

        <Suspense
          fallback={
            <Html center>
              <p className="text-sm text-muted-foreground whitespace-nowrap">
                Loading pump model...
              </p>
            </Html>
          }
        >
          <Bounds fit clip observe margin={1.3}>
            <group onClick={handleClick}>
              <PumpModel />
            </group>
          </Bounds>

          {hotspots.map((h) => (
            <Hotspot key={h.part} hotspot={h} risk={partStatus[h.part] ?? "normal"} />
          ))}

          <Environment preset="warehouse" />
        </Suspense>

        <OrbitControls
          makeDefault
          enableDamping
          dampingFactor={0.12}
          minDistance={20}
          maxDistance={220}
        />
      </Canvas>
    </div>
  );
}
