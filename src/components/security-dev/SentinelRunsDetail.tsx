import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ChevronDown } from "lucide-react";
import { useSentinelHistory } from "@/hooks/useSecurityDevData";
import { SentinelAgentCard } from "./SentinelAgentCard";
import { fmtDateTime, groupSentinelRuns } from "./parts";

// "Detalle por componente" · corridas de /sentinel/history agrupadas, expandibles a agentes.
export function SentinelRunsDetail({ onOpenAgentIssues }: { onOpenAgentIssues: (agentCode: string) => void }) {
  const { data, isLoading } = useSentinelHistory();
  const runs = useMemo(() => groupSentinelRuns(data?.scans ?? []), [data]);
  const [openKey, setOpenKey] = useState<string | null>(null);
  const open = openKey ?? runs[0]?.key ?? null;
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Detalle por componente</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {isLoading && <Skeleton className="h-20 w-full" />}
        {!isLoading && runs.length === 0 && (
          <p className="text-xs text-muted-foreground">Sin corridas per-componente aún. Corré un scan.</p>
        )}
        {runs.map((run) => (
          <div key={run.key} className="rounded-lg border border-border/40">
            <button onClick={() => setOpenKey(open === run.key ? "" : run.key)}
              className="flex w-full items-center justify-between gap-2 px-3 py-2 text-sm">
              <span className="text-muted-foreground">{fmtDateTime(run.scans[0].created_at)}</span>
              <span className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground">{run.scans.length} componentes</span>
                <ChevronDown className={`h-4 w-4 transition-transform ${open === run.key ? "" : "-rotate-90"}`} />
              </span>
            </button>
            {open === run.key && (
              <div className="space-y-2 p-3 pt-0">
                {run.scans.map((s) => (
                  <SentinelAgentCard key={s.id} scan={s} onOpenIssues={() => onOpenAgentIssues(s.agent_code)} />
                ))}
              </div>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
