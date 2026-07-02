import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import type { Mesh } from "three";

// Diamante (octaedro wireframe) flotante · dorado OMEGA #EEA62B. Portado del molde.
export function DiamondMesh() {
  const meshRef = useRef<Mesh>(null);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.y = clock.getElapsedTime() * 0.15;
    meshRef.current.rotation.x = Math.sin(clock.getElapsedTime() * 0.1) * 0.2;
  });

  return (
    <Float speed={1.2} rotationIntensity={0.3} floatIntensity={0.8}>
      <mesh ref={meshRef}>
        <octahedronGeometry args={[1.6, 0]} />
        <meshStandardMaterial
          color="#EEA62B"
          emissive="#EEA62B"
          emissiveIntensity={0.2}
          wireframe
          transparent
          opacity={0.6}
        />
      </mesh>
    </Float>
  );
}
