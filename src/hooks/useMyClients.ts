import { useQuery } from "@tanstack/react-query";
import { useMyPlanStatus } from "./useMyPlanStatus";
import { apiGet } from "@/lib/api-client";

export interface ClientOption {
  id: string;
  name: string;
}

interface ClientApiResponse {
  data?: Array<{ id: string; name: string }>;
}

interface ClientProfileResponse {
  data?: { id: string; name?: string | null } | null;
}

export function useMyClients() {
  const { isClient, clientId, loading: planLoading } = useMyPlanStatus();

  return useQuery<ClientOption[]>({
    queryKey: ["my_clients", isClient ? `client:${clientId ?? ""}` : "admin"],
    queryFn: async () => {
      if (isClient && clientId) {
        // DEBT-CL-016 cerrada (23 may 2026): backend ClientProfile saneado
        // (PlanOption +adopcion · 6 fields → Optional). Restaurado apiGet.
        const r = await apiGet<ClientProfileResponse>(`/clients/${clientId}`);
        if (!r.data) throw new Error("client_not_found");
        return [{ id: r.data.id, name: r.data.name ?? "Sin nombre" }];
      }
      const json = await apiGet<ClientApiResponse>(`/clients/`);
      return (json.data ?? []).map((c) => ({ id: c.id, name: c.name }));
    },
    enabled: !planLoading,
  });
}
