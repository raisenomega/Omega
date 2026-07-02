import { useState, useEffect } from "react";
import { Canvas } from "@react-three/fiber";
import { Scene } from "./hero-scene/Scene";

// Guard WebGL: sin soporte → null (nada de crash · el texto z-10 renderiza igual · sirve también
// al prerender de F4, donde no hay GPU). Este componente entra SIEMPRE por React.lazy → su chunk
// (three/fiber/drei) nunca toca el bundle inicial de la app.
function webglAvailable(): boolean {
  try {
    const c = document.createElement("canvas");
    return !!(window.WebGLRenderingContext && (c.getContext("webgl") || c.getContext("experimental-webgl")));
  } catch {
    return false;
  }
}

export function HeroScene() {
  const [ok, setOk] = useState(true);
  useEffect(() => {
    if (!webglAvailable()) setOk(false);
  }, []);
  if (!ok) return null;

  return (
    <Canvas
      camera={{ position: [0, 0, 6], fov: 110 }}
      dpr={[1, 1.5]}
      style={{ background: "hsl(225 15% 5%)", width: "100%", height: "100%" }}
      gl={{ antialias: true, alpha: false }}
    >
      <Scene />
    </Canvas>
  );
}
