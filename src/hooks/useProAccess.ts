// Acceso por plan para el sidebar Y los gates de página (consistencia sidebar↔ruta).
// Combina useClientPlanStatus (planCode · ya respeta el demo VISTA toggle) con el
// created_at del cliente para la prueba de 7 días. En demo, el toggle es autoritativo
// (el trial real NO aplica). Frontend-only.
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useDemoMode } from "./useDemoMode";
import { useMyPlanStatus } from "./useMyPlanStatus";
import { useClientPlanStatus } from "./useClientPlanStatus";

const TRIAL_DAYS = 7;

export interface ProAccess {
  loading: boolean;
  clientId: string | null;
  hasBasic: boolean; // plan básico+ O en prueba → badge BÁSICO encendido
  hasPro: boolean;   // pro/enterprise O en prueba 7d → PRO encendido + Avanzado desbloqueado
  inTrial: boolean;
}

export function useProAccess(): ProAccess {
  const demo = useDemoMode();
  const { clientId } = useMyPlanStatus();
  const plan = useClientPlanStatus(clientId ?? "");

  const createdQuery = useQuery({
    queryKey: ["client_created_at", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("clients")
        .select("created_at")
        .eq("id", clientId!)
        .maybeSingle();
      if (error) throw error;
      return data?.created_at ?? null;
    },
    enabled: !!clientId && !demo.isDemoAccount,
  });

  const createdAt = createdQuery.data ?? null;
  const realInTrial = createdAt
    ? (Date.now() - new Date(createdAt).getTime()) / 86400000 < TRIAL_DAYS
    : false;
  // Demo: el toggle VISTA (planCode) manda · el trial real se ignora.
  const inTrial = realInTrial && !demo.isDemoAccount;

  const code = plan.planCode;
  const hasBasic = code === "basic" || code === "pro" || code === "enterprise" || inTrial;
  const hasPro = code === "pro" || code === "enterprise" || inTrial;

  return {
    loading: plan.loading || (createdQuery.isLoading && !demo.isDemoAccount),
    clientId,
    hasBasic,
    hasPro,
    inTrial,
  };
}
