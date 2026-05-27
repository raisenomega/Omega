// DEBT-053 · Posts Tab · historial de ejecuciones de agentes por cliente.
// Muestra ROI concreto: "Agente X — N ejecuciones · última: fecha · N completadas".
// Cero mocks — datos reales de agent_executions vía useClientAgentExecutions.

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Bot, CheckCircle2, XCircle, Clock } from "lucide-react";
import { useClientAgentExecutions } from "@/hooks/useClientAgentExecutions";
import type { AgentExecutionGroup } from "@/hooks/useClientAgentExecutions";

// ── Status badge helper ────────────────────────────────────────────────────
type StatusKey = "completed" | "failed" | "running" | "pending" | "cancelled";

const STATUS_LABELS: Record<StatusKey, string> = {
  completed: "Completada",
  failed: "Error",
  running: "En curso",
  pending: "Pendiente",
  cancelled: "Cancelada",
};

function statusLabel(s: string): string {
  return STATUS_LABELS[s as StatusKey] ?? s;
}

function statusVariant(s: string): "default" | "secondary" | "destructive" | "outline" {
  if (s === "completed") return "default";
  if (s === "failed") return "destructive";
  if (s === "running") return "secondary";
  return "outline";
}

// ── Date formatter ─────────────────────────────────────────────────────────
function fmtDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("es-ES", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function fmtMs(ms: number | null): string {
  if (ms === null) return "";
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}

// ── Single agent group card ────────────────────────────────────────────────
function AgentGroupCard({ group }: { group: AgentExecutionGroup }) {
  const recent = group.executions.slice(0, 5); // last 5 executions in the group

  return (
    <div className="rounded-lg border border-border/40 bg-muted/10 p-4 space-y-3">
      {/* Group header */}
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10">
          <Bot className="h-4 w-4 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold truncate">{group.agentName}</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            {group.totalCount} {group.totalCount === 1 ? "ejecución" : "ejecuciones"} · última {fmtDate(group.lastExecution)}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          {group.completedCount > 0 && (
            <span className="flex items-center gap-1 text-xs text-emerald-500">
              <CheckCircle2 className="h-3 w-3" />
              {group.completedCount} OK
            </span>
          )}
          {group.failedCount > 0 && (
            <span className="flex items-center gap-1 text-xs text-destructive">
              <XCircle className="h-3 w-3" />
              {group.failedCount} error{group.failedCount !== 1 ? "es" : ""}
            </span>
          )}
        </div>
      </div>

      {/* Last executions list */}
      <div className="space-y-1.5 border-t border-border/20 pt-2">
        {recent.map((exec) => (
          <div
            key={exec.id}
            className="flex items-center gap-2 text-xs text-muted-foreground"
          >
            <Clock className="h-3 w-3 shrink-0" />
            <span className="flex-1">{fmtDate(exec.started_at ?? exec.created_at)}</span>
            <Badge variant={statusVariant(exec.status)} className="text-[10px] px-1.5 py-0">
              {statusLabel(exec.status)}
            </Badge>
            {exec.execution_time_ms !== null && (
              <span className="tabular-nums">{fmtMs(exec.execution_time_ms)}</span>
            )}
          </div>
        ))}
        {group.executions.length > 5 && (
          <p className="text-[11px] text-muted-foreground/60 pt-0.5">
            + {group.executions.length - 5} ejecuciones anteriores
          </p>
        )}
      </div>
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────
interface ClientAgentExecutionsProps {
  clientId: string;
}

export function ClientAgentExecutions({ clientId }: ClientAgentExecutionsProps) {
  const { groups, totalExecutions, isLoading, isError } = useClientAgentExecutions(clientId);

  return (
    <Card className="border-border/50 bg-card/60">
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-sm font-medium">
          <span className="flex items-center gap-2">
            <Bot className="h-4 w-4" /> Actividad de Agentes
          </span>
          {totalExecutions > 0 && (
            <Badge variant="secondary" className="text-xs">
              {totalExecutions} {totalExecutions === 1 ? "ejecución" : "ejecuciones"}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
          </div>
        ) : isError ? (
          <p className="text-xs text-destructive text-center py-8">
            Error al cargar la actividad. Intenta recargar la página.
          </p>
        ) : groups.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-8">
            Aún no hay actividad de agentes para este cliente.
          </p>
        ) : (
          <div className="space-y-3">
            {groups.map((group) => (
              <AgentGroupCard key={group.agent_id} group={group} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
