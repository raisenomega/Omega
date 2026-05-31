import { useEffect, useState } from "react";
import { useAuth } from "./useAuth";
import type { PlanCode } from "@/lib/plan-limits";

// Demo Mode · SOLO para la cuenta de demo cliente@omega.com (invisible para el resto).
// Permite simular el plan gate como 'pro' o 'basic' sin tocar el plan real de DB.
// Frontend-only · localStorage · cero impacto en clientes reales (condición email exacta).
const KEY = "omega_demo_mode";
const EVENT = "omega-demo-mode-change";  // sincroniza instancias del hook (toggle ↔ plan status)
// Switcher V1: reseller@omega.com sumado para acceso Enterprise de testing multi-negocio
// (override frontend · DEBT-RESELLER-PLAN-NATIVO · el rol reseller no tiene plan nativo aún).
const DEMO_EMAILS = new Set(["cliente@omega.com", "reseller@omega.com"]);

export type DemoMode = Extract<PlanCode, "basic" | "pro" | "enterprise">;

function readMode(): DemoMode {
  const v = localStorage.getItem(KEY);
  if (v === "pro") return "pro";
  if (v === "basic") return "basic";
  return "enterprise";  // default · cuenta test owner perpetuo · acceso total sin paywall
}

export function useDemoMode() {
  const { user } = useAuth();
  const isDemoAccount = !!user?.email && DEMO_EMAILS.has(user.email);
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
