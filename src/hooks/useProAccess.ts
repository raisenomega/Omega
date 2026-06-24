// Acceso por plan para el sidebar Y los gates de página (consistencia sidebar↔ruta).
// Combina useClientPlanStatus (planCode · client_plans.plan canónica) con el created_at del
// negocio para la prueba de 7 días. Gatea por el negocio ACTIVO (activeBusinessId · mismo
// patrón que Dashboard), no por el 1er cliente. Frontend-only.
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
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
  const { activeBusinessId } = useActiveBusiness();
  const { clientId: myClientId } = useMyPlanStatus();
  const clientId = activeBusinessId ?? myClientId;  // negocio ACTIVO (no el 1ero · limit 1)
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
    clientId,
    hasBasic,
    hasPro,
    inTrial,
  };
}
