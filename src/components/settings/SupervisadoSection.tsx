// DEBT-097 · toggle Modo Supervisado · persiste client_context.requires_publish_approval
// vía backend (/content/supervisado/settings · service_role). El front NO toca
// client_context por Supabase directo (no está en types · patrón del repo).
// Gated PRO/Enterprise (useProAccess). Fallback honesto: default true (supervisado on).

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { ShieldCheck, Lock } from "lucide-react";
import { apiGet, apiPatch } from "@/lib/api-client";
import { useProAccess } from "@/hooks/useProAccess";
import { useToast } from "@/hooks/use-toast";

export function SupervisadoSection({ clientId }: { clientId: string | null }) {
  const { hasPro } = useProAccess();
  const qc = useQueryClient();
  const { toast } = useToast();
  const key = ["supervisado_toggle", clientId];

  const { data: enabled = true } = useQuery({
    queryKey: key,
    queryFn: async () => {
      const r = await apiGet<{ enabled: boolean }>(`/content/supervisado/settings?client_id=${clientId}`);
      return r.enabled; // backend ya aplica fallback honesto (default true)
    },
    enabled: !!clientId && hasPro,
  });

  const toggle = useMutation({
    mutationFn: (next: boolean) =>
      apiPatch(`/content/supervisado/settings`, { client_id: clientId, enabled: next }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: key }); toast({ title: "Preferencia guardada" }); },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <ShieldCheck className="h-4 w-4" /> Modo Supervisado
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {!hasPro ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Lock className="h-4 w-4" /> Disponible en plan PRO y Enterprise.
          </div>
        ) : (
          <>
            <label className="flex items-center justify-between text-sm cursor-pointer">
              <span>Revisar antes de publicar</span>
              <Switch checked={enabled} disabled={toggle.isPending || !clientId}
                onCheckedChange={(v) => toggle.mutate(v)} />
            </label>
            <p className="text-[11px] text-muted-foreground">
              Con el modo activo, ARIA prepara el contenido y PARA: lo revisás y aprobás antes de que se publique.
            </p>
          </>
        )}
      </CardContent>
    </Card>
  );
}
