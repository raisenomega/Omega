import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPatch } from "@/lib/api-client";

// Modo Autónomo (REX · DEBT-098): rex_addon_active = compró el add-on ·
// autonomous_mode_on = consentimiento humano (toggle). El toggle solo se ve si compró.
export interface AutonomousMode {
  rex_addon_active: boolean;
  autonomous_mode_on: boolean;
}

export function useAutonomousMode(clientId: string | null) {
  return useQuery<AutonomousMode>({
    queryKey: ["autonomous_mode", clientId],
    queryFn: () => apiGet<AutonomousMode>(`/calendar-v3/autonomous-mode/${clientId}`),
    enabled: !!clientId,
  });
}

export function useSetAutonomousMode(clientId: string | null) {
  const qc = useQueryClient();
  return useMutation<{ autonomous_mode_on: boolean }, Error, boolean>({
    mutationFn: (enabled) =>
      apiPatch<{ autonomous_mode_on: boolean }>(`/calendar-v3/autonomous-mode`, {
        client_id: clientId,
        enabled,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["autonomous_mode", clientId] });
    },
  });
}
