import { useQuery, useMutation } from "@tanstack/react-query";
import { apiGet, apiPost } from "@/lib/api-client";

// GA4 property picker (Vía A) · lista las propiedades GA4 reales del cliente conectado y persiste la
// elegida (external_account_id que _google_insights usa para GA4). clientId de la RUTA. Cero mock.
export interface GA4Property { property_id: string; display_name: string; }

export function useGoogleProperties(clientId: string, enabled: boolean) {
  return useQuery<{ properties: GA4Property[] }, Error>({
    queryKey: ["oauth", "google", "properties", clientId],
    queryFn: () => apiGet(`/oauth/google/properties?client_id=${encodeURIComponent(clientId)}`),
    enabled: enabled && !!clientId,
    staleTime: 60_000,
  });
}

export function useSetGoogleProperty(clientId: string) {
  return useMutation<{ ok: boolean; property_id: string }, Error, string>({
    mutationFn: (propertyId) =>
      apiPost(`/oauth/google/property?client_id=${encodeURIComponent(clientId)}`, { property_id: propertyId }),
  });
}
