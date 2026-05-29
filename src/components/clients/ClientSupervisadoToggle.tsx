// DEBT-097 · toggle Modo Supervisado · persiste client_context.requires_publish_approval
// vía backend (/content/supervisado/settings · service_role). El front NO toca client_context
// por Supabase directo (no está en types · patrón del repo). Fallback honesto: default true.
// Reubicado desde Configuración (DEBT-ARIA-UX): vive junto a su cola en ClientDetail.
// SIN useProAccess: el gating lo hace el tab padre con useClientPlanStatus (plan del CLIENTE,
// no del usuario logueado) → un reseller básico gestionando un cliente PRO no queda bloqueado.

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { ShieldCheck } from "lucide-react";
import { apiGet, apiPatch } from "@/lib/api-client";
import { useToast } from "@/hooks/use-toast";

export function ClientSupervisadoToggle({ clientId }: { clientId: string }) {
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

  return (
    <Card className="border-border/50 bg-card/60">
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <ShieldCheck className="h-4 w-4" /> Modo Supervisado
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <label className="flex items-center justify-between text-sm cursor-pointer">
          <span>Revisar antes de publicar</span>
          <Switch checked={enabled} disabled={toggle.isPending}
            onCheckedChange={(v) => toggle.mutate(v)} />
        </label>
        <p className="text-[11px] text-muted-foreground">
          Con el modo activo, ARIA prepara el contenido y PARA: lo revisás y aprobás antes de que se publique.
        </p>
      </CardContent>
    </Card>
  );
}
