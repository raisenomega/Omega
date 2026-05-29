// DEBT-102 · "Qué aprendió ARIA" · widget per-cliente · datos reales de
// agent_memory (evaluados) · pendientes aparte (P1) · empty-state honesto.

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Brain, CheckCircle2, XCircle, Clock } from "lucide-react";
import { useClientLearningEvents } from "@/hooks/useClientLearningEvents";
import type { LearningEvent } from "@/hooks/useClientLearningEvents";

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" });
}

function EventRow({ ev }: { ev: LearningEvent }) {
  return (
    <div className="flex items-start gap-2.5 rounded-lg border border-border/40 bg-muted/10 p-3">
      {ev.was_correct ? (
        <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500 mt-0.5" />
      ) : (
        <XCircle className="h-4 w-4 shrink-0 text-destructive mt-0.5" />
      )}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{ev.decision}</p>
        {ev.outcome && <p className="text-xs text-muted-foreground mt-0.5">{ev.outcome}</p>}
        <p className="text-[11px] text-muted-foreground/70 mt-1">
          {ev.agentName} · {fmtDate(ev.evaluated_at)}
        </p>
      </div>
    </div>
  );
}

interface ClientLearningEventsProps {
  clientId: string;
}

export function ClientLearningEvents({ clientId }: ClientLearningEventsProps) {
  const { events, correctCount, pendingCount, accuracy, isLoading, isError } = useClientLearningEvents(clientId);
  const evaluated = events.length;
  return (
    <Card className="border-border/50 bg-card/60">
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-sm font-medium">
          <span className="flex items-center gap-2">
            <Brain className="h-4 w-4" /> Qué aprendió ARIA
          </span>
          {accuracy !== null && (
            <Badge variant="secondary" className="text-xs">
              {correctCount}/{evaluated} acertadas · {accuracy}%
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {pendingCount > 0 && (
          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" /> {pendingCount} en evaluación
          </p>
        )}
        {isLoading ? (
          <div className="flex justify-center py-8"><Loader2 className="h-5 w-5 animate-spin text-primary" /></div>
        ) : isError ? (
          <p className="text-xs text-destructive text-center py-8">Error al cargar. Recarga la página.</p>
        ) : evaluated === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-8">
            ARIA aún no tiene aprendizajes evaluados para este cliente. Los resultados aparecen aquí
            a medida que el sistema confirma qué funcionó.
          </p>
        ) : (
          events.map((ev) => <EventRow key={ev.id} ev={ev} />)
        )}
      </CardContent>
    </Card>
  );
}
