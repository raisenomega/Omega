import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useMyPlanStatus } from "./useMyPlanStatus";
import { apiGet } from "@/lib/api-client";

export interface ClientOption {
  id: string;
  name: string;
}

interface ClientApiResponse {
  data?: Array<{ id: string; name: string }>;
}

export function useMyClients() {
  const { isClient, clientId, loading: planLoading } = useMyPlanStatus();

  return useQuery<ClientOption[]>({
    queryKey: ["my_clients", isClient ? `client:${clientId ?? ""}` : "admin"],
    queryFn: async () => {
      if (isClient && clientId) {
        // DEBT-CL-016: backend GET /clients/{id} retorna 500 (ClientProfile model
        // desincronizado de DB · plan 'adopcion' no en enum · campos required null).
        // Fallback temporal a Supabase directo (RLS filtra por user_id). Restaurar
        // a apiGet cuando se sanee el model backend.
        const { data, error } = await supabase
          .from("clients").select("id, name").eq("id", clientId).maybeSingle();
        if (error) throw new Error(`client_lookup_failed:${error.message}`);
        if (!data) throw new Error("client_not_found");
        return [{ id: data.id, name: data.name }];
      }
      const json = await apiGet<ClientApiResponse>(`/clients/`);
      return (json.data ?? []).map((c) => ({ id: c.id, name: c.name }));
    },
    enabled: !planLoading,
  });
}
