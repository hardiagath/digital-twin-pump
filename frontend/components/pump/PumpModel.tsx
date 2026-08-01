"use client";
import { useEffect } from "react";
import { useGLTF } from "@react-three/drei";
import * as THREE from "three";

const MODEL_PATH = "/models/pump.glb";

const FALLBACK_COLOR = new THREE.Color("#8a8f93");

export default function PumpModel() {
  const { scene } = useGLTF(MODEL_PATH);

  useEffect(() => {
    scene.traverse((child) => {
      if (!(child instanceof THREE.Mesh)) return;

      const materials = Array.isArray(child.material)
        ? child.material
        : [child.material];

      materials.forEach((mat) => {
        const stdMat = mat as THREE.MeshStandardMaterial;
        if (!stdMat || !stdMat.color) return;

        const hasTexture = !!stdMat.map;
        const isDefaultWhite = stdMat.color.getHex() === 0xffffff;

        if (!hasTexture && isDefaultWhite) {
          stdMat.color.set(FALLBACK_COLOR);
        }
      });
    });
  }, [scene]);

  return <primitive object={scene} />;
}

useGLTF.preload(MODEL_PATH);