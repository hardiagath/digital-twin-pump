"use client";
import { useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import type { Mesh } from "three";
import { HotspotPosition } from "@/lib/types";
import { RiskLevel, riskColor, RISK_HEX } from "@/lib/utils";
import clsx from "clsx";

export default function Hotspot({
  hotspot,
  risk,
}: {
  hotspot: HotspotPosition;
  risk: RiskLevel;
}) {
  const meshRef = useRef<Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const color = RISK_HEX[risk];

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const pulse = risk === "normal" ? 1 : 1 + Math.sin(clock.elapsedTime * 4) * 0.22;
    meshRef.current.scale.setScalar(pulse);
  });

  return (
    <group position={hotspot.position}>
      <mesh
        ref={meshRef}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
        }}
        onPointerOut={() => setHovered(false)}
      >
        <sphereGeometry args={[1.1, 16, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={hovered ? 1.5 : 0.85}
        />
      </mesh>

      {hovered && (
        <Html distanceFactor={40} center>
          <div className="px-2.5 py-1.5 rounded-xl bg-surface border border-border text-xs whitespace-nowrap shadow-lg pointer-events-none">
            <span className="font-semibold">{hotspot.label}</span>
            <span className={clsx("ml-1.5 capitalize", riskColor(risk))}>{risk}</span>
          </div>
        </Html>
      )}
    </group>
  );
}
