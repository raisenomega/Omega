import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import type { Points, BufferAttribute } from "three";

// Partículas cometa doradas (2.8k · dorado OMEGA #EEA62B). Portado del molde · efecto idéntico.
export function CometParticles() {
  const pointsRef = useRef<Points>(null);
  const count = 2800;

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 60;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 60;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 100;
    }
    return arr;
  }, []);

  useFrame(() => {
    if (!pointsRef.current) return;
    const p = pointsRef.current.geometry.attributes.position as BufferAttribute;
    for (let i = 0; i < count; i++) {
      let z = p.getZ(i) + 0.25;
      if (z > 50) z = -50;
      p.setZ(i, z);
    }
    p.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" array={positions} count={count} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.02} color="#EEA62B" transparent opacity={0.6} sizeAttenuation />
    </points>
  );
}
