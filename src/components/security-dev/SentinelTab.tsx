import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, RefreshCw, ChevronDown } from "lucide-react";
import { useSentinelData, useSentinelHistory, type SentinelScore } from "@/hooks/useSecurityDevData";
import { useSentinelScan } from "@/hooks/useSentinelScan";
import { SentinelAgentCard } from "./SentinelAgentCard";
import { SentinelComponentsHeader } from "./SentinelComponentsHeader";
import { scoreColor, fmtDateTime, groupSentinelRuns } from "./parts";

export function SentinelTab() {
  const { data, isLoading, error } = useSentinelData();
  const history = useSentinelHistory();
  const { runScan, isScanning } = useSentinelScan();
  const runs = useMemo(() => groupSentinelRuns(history.data?.scans ?? []), [history.data]);
  const [openKey, setOpenKey] = useState<string | null>(null);
  const open = openKey ?? runs[0]?.key ?? null;

  if (isLoading) return <Skeleton className="h-64 w-full" />;
  const err = (error as Error)?.message ?? data?.error;
  if (err) return <p className="text-sm text-red-500">Error: {err}</p>;
  if (!data || data.count === 0)
    return <p className="text-sm text-muted-foreground">Sin corridas registradas aún. SENTINEL corre a las 7 AM.</p>;

  const latest = data.latest as SentinelScore;
  return (
    <div className="space-y-4">
      <SentinelComponentsHeader />
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Último scan</CardTitle>
          <Button size="sm" variant="outline" onClick={runScan} disabled={isScanning}>
            {isScanning ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            <span className="ml-2">{isScanning ? "Escaneando…" : "Correr scan ahora"}</span>
          </Button>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-baseline gap-3">
            <span className={`text-5xl font-bold ${scoreColor(latest.score)}`}>{Math.round(latest.score)}</span>
            <span className="text-sm text-muted-foreground">/100 · {latest.verdict}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="bg-red-500/15 text-red-500 border-red-500/40">críticos {latest.issues_critical}</Badge>
            <Badge variant="outline" className="bg-orange-500/15 text-orange-500 border-orange-500/40">altos {latest.issues_high}</Badge>
            <Badge variant="outline" className="bg-amber-500/15 text-amber-500 border-amber-500/40">medios {latest.issues_medium}</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">Últimas corridas</CardTitle></CardHeader>
        <CardContent className="space-y-1">
          {data.history.map((r) => (
            <div key={r.id} className="flex items-center justify-between gap-2 border-b border-border/40 py-1 text-sm">
              <span className="text-muted-foreground">{fmtDateTime(r.calculated_at)}</span>
              <span className={`font-medium ${scoreColor(r.score)}`}>{Math.round(r.score)}</span>
              <span className="text-xs text-muted-foreground">{r.verdict}</span>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">Detalle por componente</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {history.isLoading && <Skeleton className="h-20 w-full" />}
          {!history.isLoading && runs.length === 0 && (
            <p className="text-xs text-muted-foreground">Sin corridas per-componente aún. Corré un scan.</p>
          )}
          {runs.map((run) => (
            <div key={run.key} className="rounded-lg border border-border/40">
              <button
                onClick={() => setOpenKey(open === run.key ? "" : run.key)}
                className="flex w-full items-center justify-between gap-2 px-3 py-2 text-sm"
              >
                <span className="text-muted-foreground">{fmtDateTime(run.scans[0].created_at)}</span>
                <span className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">{run.scans.length} componentes</span>
                  <ChevronDown className={`h-4 w-4 transition-transform ${open === run.key ? "" : "-rotate-90"}`} />
                </span>
              </button>
              {open === run.key && (
                <div className="space-y-2 p-3 pt-0">
                  {run.scans.map((s) => <SentinelAgentCard key={s.id} scan={s} />)}
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
