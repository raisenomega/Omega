import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, RefreshCw } from "lucide-react";
import { useSentinelData, type SentinelScore } from "@/hooks/useSecurityDevData";
import { useSentinelScan } from "@/hooks/useSentinelScan";
import { SentinelComponentsHeader } from "./SentinelComponentsHeader";
import { SentinelRunsDetail } from "./SentinelRunsDetail";
import { SentinelIssueModal } from "./SentinelIssueModal";
import { scoreColor, fmtDateTime } from "./parts";

type ModalState = { scope: "aggregate" | "agent"; severity?: string; agentCode?: string };

export function SentinelTab() {
  const { data, isLoading, error } = useSentinelData();
  const { runScan, isScanning } = useSentinelScan();
  const [modal, setModal] = useState<ModalState | null>(null);

  if (isLoading) return <Skeleton className="h-64 w-full" />;
  const err = (error as Error)?.message ?? data?.error;
  if (err) return <p className="text-sm text-red-500">Error: {err}</p>;
  if (!data || data.count === 0)
    return <p className="text-sm text-muted-foreground">Sin corridas registradas aún. SENTINEL corre a las 7 AM.</p>;

  const latest = data.latest as SentinelScore;
  const chips = [
    { label: "críticos", sev: "CRITICAL", n: latest.issues_critical, cls: "bg-red-500/15 text-red-500 border-red-500/40" },
    { label: "altos", sev: "HIGH", n: latest.issues_high, cls: "bg-orange-500/15 text-orange-500 border-orange-500/40" },
    { label: "medios", sev: "MEDIUM", n: latest.issues_medium, cls: "bg-amber-500/15 text-amber-500 border-amber-500/40" },
  ];
  return (
    <div className="space-y-4">
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
            {chips.map((c) => (
              <button key={c.sev} onClick={() => setModal({ scope: "aggregate", severity: c.sev })}
                className={`rounded border px-2 py-0.5 text-xs ${c.cls}`}>{c.label} {c.n}</button>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-sm">Últimas corridas</CardTitle></CardHeader>
        <CardContent className="space-y-1">
          {data.history.slice(0, 3).map((r) => (
            <div key={r.id} className="flex items-center justify-between gap-2 border-b border-border/40 py-1 text-sm">
              <span className="text-muted-foreground">{fmtDateTime(r.calculated_at)}</span>
              <span className={`font-medium ${scoreColor(r.score)}`}>{Math.round(r.score)}</span>
              <span className="text-xs text-muted-foreground">{r.verdict}</span>
            </div>
          ))}
        </CardContent>
      </Card>

      <SentinelComponentsHeader />
      <SentinelRunsDetail onOpenAgentIssues={(agentCode) => setModal({ scope: "agent", agentCode })} />

      {modal && (
        <SentinelIssueModal open onClose={() => setModal(null)} scope={modal.scope} severity={modal.severity} agentCode={modal.agentCode} />
      )}
    </div>
  );
}
