import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, Bot } from "lucide-react";
import { useAgentsHealthStatus, useTriggerAgentsHealth, type AgentHealth } from "@/hooks/useAgentsHealthStatus";
import { scoreColor, IssueChip } from "./parts";
import type { OpenIssuesParams } from "@/lib/sentinel_issue_loaders";

const pct = (v: number | null) => (v == null ? "—" : `${Math.round(v * 100)}%`);

function rateColor(v: number | null): string {
  if (v == null) return "text-muted-foreground";
  return v >= 0.95 ? "text-green-500" : v >= 0.8 ? "text-amber-500" : "text-red-500";
}

const hasIssue = (a: AgentHealth) => a.success_rate != null && a.success_rate < 0.95;

export function SentinelAgentsHealthCard({ onOpenIssues }: { onOpenIssues?: (p: OpenIssuesParams) => void }) {
  const { data, isLoading } = useAgentsHealthStatus();
  const trigger = useTriggerAgentsHealth();
  const scan = data?.last_scan ?? null;
  const agents: AgentHealth[] = scan?.per_agent ?? [];

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm">Agentes IA · Health</CardTitle>
        <Button size="sm" variant="outline" onClick={() => trigger.mutate()} disabled={trigger.isPending}>
          {trigger.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Bot className="h-4 w-4" />}
          <span className="ml-2">{trigger.isPending ? "Escaneando…" : "Escanear ahora"}</span>
        </Button>
      </CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <Skeleton className="h-20 w-full" />
        ) : !scan ? (
          <p className="text-xs text-muted-foreground">Sin scans aún. Corré "Escanear ahora".</p>
        ) : (
          <>
            <div className="flex items-baseline gap-3">
              <span className={`text-4xl font-bold ${scoreColor(scan.score)}`}>{scan.score}</span>
              <span className="text-sm text-muted-foreground">
                /100 · {data?.summary.total_agents_monitored} agentes · {data?.summary.total_calls_24h} calls 24h
              </span>
            </div>
            {scan.model_drift_alerts.length > 0 && (
              onOpenIssues ? (
                <IssueChip onClick={() => onOpenIssues({ sourceType: "agents_health", scopeLabel: "Agentes · model drift" })}>
                  <Badge variant="outline" className="border-red-500/40 bg-red-500/15 text-red-500">model drift</Badge>
                </IssueChip>
              ) : (
                <Badge variant="outline" className="border-red-500/40 bg-red-500/15 text-red-500">model drift</Badge>
              )
            )}
            <div className="space-y-1">
              {agents.length === 0 && (
                <p className="text-xs text-muted-foreground">Sin actividad de agentes en la ventana.</p>
              )}
              {agents.map((a) => (
                <div key={a.agent_code} className="flex items-center justify-between gap-2 border-b border-border/40 py-1 text-xs">
                  <span className="font-mono">{a.agent_code}</span>
                  <span className="flex items-center gap-2 text-[10px] text-muted-foreground">
                    <span className={rateColor(a.success_rate)}>{pct(a.success_rate)} ok</span>
                    <span>{a.calls_24h} calls</span>
                    {a.avg_latency_ms != null && <span>{a.avg_latency_ms}ms</span>}
                    <span>null30d {pct(a.was_correct_null_pct_30d)}</span>
                    <span>acc {pct(a.accuracy_30d)}</span>
                    {hasIssue(a) && onOpenIssues && (
                      <IssueChip onClick={() => onOpenIssues({ sourceType: "agents_health", agentCode: a.agent_code, scopeLabel: a.agent_code })}>
                        <Badge variant="outline" className="border-amber-500/40 bg-amber-500/15 text-amber-500">revisar</Badge>
                      </IssueChip>
                    )}
                  </span>
                </div>
              ))}
            </div>
            <p className="text-[10px] text-muted-foreground">
              Costo diario:{" "}
              {scan.total_daily_cost_usd != null
                ? `$${scan.total_daily_cost_usd} (${scan.cost_calculation_source})`
                : "no calculable (tokens no registrados V1)"}
            </p>
            {scan.coverage_note && <p className="text-[10px] text-muted-foreground">{scan.coverage_note}</p>}
          </>
        )}
      </CardContent>
    </Card>
  );
}
