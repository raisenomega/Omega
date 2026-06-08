import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

export interface SocialAccountSummary {
  id: string;
  platform: string;
  account_name: string;
  status: string;
}

interface ListResponse {
  items: SocialAccountSummary[];
  total: number;
}

// DEBT-CL-015: cuentas sociales del cliente filtradas por platform. Backend
// retorna solo status=active y sin tokens (security). Usado por el dropdown
// del form bar cuando el cliente tiene 2+ cuentas para la misma platform.
export function useMyAccounts(clientId: string | undefined, platform: string | undefined) {
  return useQuery<SocialAccountSummary[]>({
    queryKey: ["my_accounts", clientId, platform],
    queryFn: async () => {
      if (!clientId || !platform) return [];
      const r = await apiGet<ListResponse>(`/clients/${clientId}/social-accounts?platform=${platform}`);
      return r.items;
    },
    enabled: !!clientId && !!platform,
    staleTime: 60_000,
  });
}

// Todas las redes conectadas (status=active) del negocio activo, sin filtrar por platform.
// Para el picker de checkboxes del modal supervisado (fan-out): 1 red marcable por cuenta active.
// El backend ya scopea por client_id + ownership y solo devuelve active (guardrail: no expired/revoked).
export function useConnectedNetworks(clientId: string | undefined) {
  return useQuery<SocialAccountSummary[]>({
    queryKey: ["connected_networks", clientId],
    queryFn: async () => {
      if (!clientId) return [];
      const r = await apiGet<ListResponse>(`/clients/${clientId}/social-accounts`);
      return r.items;
    },
    enabled: !!clientId,
    staleTime: 60_000,
  });
}
