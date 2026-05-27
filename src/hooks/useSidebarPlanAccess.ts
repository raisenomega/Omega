// Rediseño sidebar · acceso por plan para las secciones Principal/Avanzado.
// Combina useClientPlanStatus (planCode · ya respeta el demo VISTA toggle) con el
// created_at del cliente para la lógica de prueba de 7 días. Frontend-only.
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useMyPlanStatus } from "./useMyPlanStatus";
import { useClientPlanStatus } from "./useClientPlanStatus";

const TRIAL_DAYS = 7;

export interface SidebarPlanAccess {
  loading: boolean;
  hasBasic: boolean; // plan básico o superior → badge BÁSICO encendido
  hasPro: boolean;   // pro/enterprise O en prueba 7d → badge PRO encendido + Avanzado desbloqueado
  inTrial: boolean;  // primeros 7 días desde created_at del cliente
}

export function useSidebarPlanAccess(): SidebarPlanAccess {
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
    enabled: !!clientId,
  });

  const createdAt = createdQuery.data ?? null;
  const inTrial = createdAt
    ? (Date.now() - new Date(createdAt).getTime()) / 86400000 < TRIAL_DAYS
    : false;

  const code = plan.planCode;
  const hasBasic = code === "basic" || code === "pro" || code === "enterprise" || inTrial;
  const hasPro = code === "pro" || code === "enterprise" || inTrial;

  return {
    loading: plan.loading || createdQuery.isLoading,
    hasBasic,
    hasPro,
    inTrial,
  };
}
