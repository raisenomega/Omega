import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import type { Points, BufferAttribute } from "three";

// Campo de estrellas en "warp" (14k puntos avanzando en z). Portado del molde · sin cambios de efecto.
export function WarpStars() {
  const pointsRef = useRef<Points>(null);
  const count = 14000;
  const speed = 0.12;
  const depth = 120;

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 80;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 80;
      arr[i * 3 + 2] = (Math.random() - 0.5) * depth * 2;
    }
    return arr;
  }, []);

  useFrame(() => {
    if (!pointsRef.current) return;
    const p = pointsRef.current.geometry.attributes.position as BufferAttribute;
    for (let i = 0; i < count; i++) {
      let z = p.getZ(i) + speed;
      if (z > depth) z = -depth;
      p.setZ(i, z);
    }
    p.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" array={positions} count={count} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.035} color="#ffffff" transparent opacity={0.85} sizeAttenuation />
    </points>
  );
}
