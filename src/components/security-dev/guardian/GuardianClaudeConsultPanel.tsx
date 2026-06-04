import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { consultEntity } from "@/lib/guardian/consult";
import type { OpenGuardianDetail } from "@/types/guardian";

const CONF: Record<string, string> = {
  alta: "bg-green-500/15 text-green-500 border-green-500/40",
  media: "bg-amber-500/15 text-amber-500 border-amber-500/40",
  baja: "bg-red-500/15 text-red-500 border-red-500/40",
};

// Sub-E · Claude Consultor embebido · analiza y SUGIERE (no ejecuta · el owner decide).
export function GuardianClaudeConsultPanel({ detail }: { detail: OpenGuardianDetail }) {
  const [q, setQ] = useState("");
  const m = useMutation({ mutationFn: (question?: string) => consultEntity(detail, question) });
  useEffect(() => { m.mutate(undefined); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  const r = m.data;

  return (
    <div className="space-y-2 rounded border border-border/40 bg-muted/20 p-2 text-xs">
      <p className="font-medium">Claude Consultor de Seguridad</p>
      {m.isPending ? (
        <span className="flex items-center gap-2 text-muted-foreground"><Loader2 className="h-3 w-3 animate-spin" /> analizando…</span>
      ) : m.isError ? (
        <p className="text-red-500">No se pudo consultar al modelo · reintentá.</p>
      ) : r ? (
        <div className="space-y-1">
          <p className="text-muted-foreground">{r.analysis}</p>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="border-primary/40 text-primary">acción: {r.recommended_action}</Badge>
            <Badge variant="outline" className={CONF[r.confidence_level] ?? CONF.baja}>confianza {r.confidence_level}</Badge>
          </div>
          <p className="text-[10px] text-muted-foreground">{r.reasoning}</p>
          {r.alternative && <p className="text-[10px] text-muted-foreground">alternativa: {r.alternative}</p>}
          <p className="text-[10px] text-muted-foreground">El consultor solo sugiere · ejecutá vos desde "Tomar acción".</p>
        </div>
      ) : null}
      <Textarea value={q} onChange={(e) => setQ(e.target.value)} placeholder="Pregunta de seguimiento (opcional)" className="text-xs" />
      <Button size="sm" disabled={m.isPending || !q.trim()} onClick={() => m.mutate(q)}>Preguntar</Button>
    </div>
  );
}
