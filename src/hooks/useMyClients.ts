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

interface ClientSingleResponse {
  id: string;
  name: string;
}

export function useMyClients() {
  const { isClient, clientId, loading: planLoading } = useMyPlanStatus();

  return useQuery<ClientOption[]>({
    queryKey: ["my_clients", isClient ? `client:${clientId ?? ""}` : "admin"],
    queryFn: async () => {
      if (isClient && clientId) {
        const data = await apiGet<ClientSingleResponse>(`/clients/${clientId}`);
        return [{ id: data.id, name: data.name }];
      }
      const json = await apiGet<ClientApiResponse>(`/clients/`);
      return (json.data ?? []).map((c) => ({ id: c.id, name: c.name }));
    },
    enabled: !planLoading,
  });
}
