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
