import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useMyPlanStatus } from "./useMyPlanStatus";

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

async function authHeaders(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();
  return { Authorization: `Bearer ${session?.access_token ?? ""}` };
}

function apiBase(): string {
  return import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
}

export function useMyClients() {
  const { isClient, clientId, loading: planLoading } = useMyPlanStatus();

  return useQuery<ClientOption[]>({
    queryKey: ["my_clients", isClient ? `client:${clientId ?? ""}` : "admin"],
    queryFn: async () => {
      if (isClient && clientId) {
        const res = await fetch(`${apiBase()}/clients/${clientId}`, { headers: await authHeaders() });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = (await res.json()) as ClientSingleResponse;
        return [{ id: data.id, name: data.name }];
      }
      const res = await fetch(`${apiBase()}/clients/`, { headers: await authHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as ClientApiResponse;
      return (json.data ?? []).map((c) => ({ id: c.id, name: c.name }));
    },
    enabled: !planLoading,
  });
}
