// DEBT-097 / DEBT-ARIA-UX · estado del toggle Modo Supervisado por cliente.
// Persiste client_context.requires_publish_approval vía backend (/content/supervisado/settings ·
// service_role). El front NO toca client_context por Supabase directo (no está en types · patrón
// del repo). Fallback honesto: default true. SIN gate propio: el componente que lo usa vive en un
// tab ya gateado por plan del CLIENTE (useClientPlanStatus) — no del usuario logueado.
// Lógica reubicada (verbatim) desde el ex-ClientSupervisadoToggle.tsx para fundir el switch
// en la cabecera de la cola sin perder persistencia/toast.

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPatch } from "@/lib/api-client";
import { useToast } from "./use-toast";

export function useSupervisadoSetting(clientId: string) {
  const qc = useQueryClient();
  const { toast } = useToast();
  const key = ["supervisado_toggle", clientId];

  const { data: enabled = true } = useQuery({
    queryKey: key,
    queryFn: async () => {
      const r = await apiGet<{ enabled: boolean }>(`/content/supervisado/settings?client_id=${clientId}`);
      return r.enabled; // backend ya aplica fallback honesto (default true)
    },
    enabled: !!clientId,
  });

  const toggle = useMutation({
    mutationFn: (next: boolean) =>
      apiPatch(`/content/supervisado/settings`, { client_id: clientId, enabled: next }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: key }); toast({ title: "Preferencia guardada" }); },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  return { enabled, toggle };
}
