// DEBT-097 · Modo Supervisado · cola de aprobación por negocio.
// ARIA generó estos drafts y PARÓ · el cliente aprueba/rechaza · cero auto-publicación.
// Datos reales vía useSupervisedQueue (backend filtra draft+supervisado+ownership).
// DEBT-ARIA-UX: cabecera única · el switch (useSupervisadoSetting) vive aquí, a la derecha del
// título (antes era una tarjeta aparte duplicada). SIN gate propio: el tab padre gatea por plan
// del cliente (useClientPlanStatus). Tarjetas en grid 5×5 (layout · datos ya llegan ≤100).

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Loader2, ClipboardCheck, Check, X } from "lucide-react";
import { useSupervisedQueue } from "@/hooks/useSupervisedQueue";
import { useSupervisadoSetting } from "@/hooks/useSupervisadoSetting";
import type { SupervisedDraft } from "@/hooks/useSupervisedQueue";

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleDateString("es-ES", { day: "2-digit", month: "short" });
}

function DraftRow({ d, onApprove, onReject, busy }: {
  d: SupervisedDraft; onApprove: () => void; onReject: () => void; busy: boolean;
}) {
  return (
    <div className="rounded-lg border border-border/40 bg-muted/10 p-3 space-y-2">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] text-muted-foreground">
          {d.agent_code ?? "ARIA"} · {d.content_type ?? "post"} · {fmtDate(d.created_at)}
        </span>
        {d.confidence !== null && (
          <Badge variant="secondary" className="text-[10px]">conf {d.confidence}</Badge>
        )}
      </div>
      <p className="text-sm whitespace-pre-wrap line-clamp-4">{d.generated_text ?? "(sin texto)"}</p>
      <div className="flex gap-2 pt-1">
        <Button size="sm" className="gap-1 h-7" disabled={busy} onClick={onApprove}>
          <Check className="h-3.5 w-3.5" /> Aprobar
        </Button>
        <Button size="sm" variant="outline" className="gap-1 h-7" disabled={busy} onClick={onReject}>
          <X className="h-3.5 w-3.5" /> Rechazar
        </Button>
      </div>
    </div>
  );
}

export function ClientSupervisedQueue({ clientId }: { clientId: string }) {
  const { items, isLoading, isError, approve, reject } = useSupervisedQueue(clientId);
  const { enabled, toggle } = useSupervisadoSetting(clientId);
  const busy = approve.isPending || reject.isPending;

  return (
    <Card className="border-border/50 bg-card/60">
      <CardHeader className="space-y-1">
        <CardTitle className="flex items-center gap-2 text-sm font-medium">
          <span className="flex items-center gap-2"><ClipboardCheck className="h-4 w-4" /> Modo Supervisado</span>
          <Switch checked={enabled} disabled={toggle.isPending}
            onCheckedChange={(v) => toggle.mutate(v)} aria-label="Revisar antes de publicar" />
          {items.length > 0 && (
            <Badge variant="secondary" className="ml-auto text-xs">
              {items.length} pendiente{items.length !== 1 ? "s" : ""}
            </Badge>
          )}
        </CardTitle>
        <p className="text-[11px] text-muted-foreground">
          Con el modo activo, ARIA prepara el contenido y PARA: lo revisás y aprobás antes de que se publique.
        </p>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin text-primary" /></div>
        ) : isError ? (
          <p className="text-xs text-destructive text-center py-8">Error al cargar la cola. Recarga la página.</p>
        ) : items.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-8">
            No hay borradores pendientes de aprobación. Cuando ARIA prepare contenido, aparecerá aquí para que lo revises antes de publicar.
          </p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {items.map((d) => (
              <DraftRow key={d.id} d={d} busy={busy}
                onApprove={() => approve.mutate(d.id)} onReject={() => reject.mutate(d.id)} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
