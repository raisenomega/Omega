import { useEffect, useState } from "react";
import { useAuth } from "./useAuth";
import type { PlanCode } from "@/lib/plan-limits";

// Demo Mode · SOLO para la cuenta de demo cliente@omega.com (invisible para el resto).
// Permite simular el plan gate como 'pro' o 'basic' sin tocar el plan real de DB.
// Frontend-only · localStorage · cero impacto en clientes reales (condición email exacta).
const KEY = "omega_demo_mode";
const EVENT = "omega-demo-mode-change";  // sincroniza instancias del hook (toggle ↔ plan status)
const DEMO_EMAIL = "cliente@omega.com";

export type DemoMode = Extract<PlanCode, "pro" | "basic">;

function readMode(): DemoMode {
  return localStorage.getItem(KEY) === "pro" ? "pro" : "basic";  // default 'basic' (estado real del test account)
}

export function useDemoMode() {
  const { user } = useAuth();
  const isDemoAccount = user?.email === DEMO_EMAIL;
  const [demoMode, setMode] = useState<DemoMode>(readMode);

  useEffect(() => {
    const sync = () => setMode(readMode());
    window.addEventListener(EVENT, sync);
    window.addEventListener("storage", sync);  // cross-tab
    return () => {
      window.removeEventListener(EVENT, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  const setDemoMode = (m: DemoMode) => {
    localStorage.setItem(KEY, m);
    window.dispatchEvent(new Event(EVENT));
  };

  return { demoMode, setDemoMode, isDemoAccount };
}
