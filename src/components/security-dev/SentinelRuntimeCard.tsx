import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useRuntimeStatus } from "@/hooks/useRuntimeStatus";
import { scoreColor, IssueChip } from "./parts";
import type { OpenIssuesParams } from "@/lib/sentinel_issue_loaders";

export function SentinelRuntimeCard({ onOpenIssues }: { onOpenIssues?: (p: OpenIssuesParams) => void }) {
  const { data, isLoading } = useRuntimeStatus();
  const [expanded, setExpanded] = useState(false);
  const scan = data?.last_scan ?? null;
  const recurring = scan?.recurring_patterns ?? [];
  const top = data?.last_24h.top_signatures ?? [];
  const open = () => onOpenIssues?.({ sourceType: "runtime_observability", scopeLabel: "Observabilidad Runtime" });

  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Observabilidad Runtime</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <Skeleton className="h-20 w-full" />
        ) : !scan ? (
          <p className="text-xs text-muted-foreground">Sin scans aún. El worker corre cada 5 min.</p>
        ) : (
          <>
            <div className="flex items-baseline gap-3">
              <span className={`text-4xl font-bold ${scoreColor(scan.score)}`}>{scan.score}</span>
              <span className="text-sm text-muted-foreground">/100 · ventana {scan.window_minutes}min</span>
              {scan.score < 80 && (
                <Badge variant="outline" className="bg-amber-500/15 text-amber-500 border-amber-500/40">Atención</Badge>
              )}
            </div>
            <div className="flex flex-wrap gap-2 text-xs">
              <IssueChip onClick={open}><Badge variant="outline" className="border-border/40">backend: {scan.backend_exception_count}</Badge></IssueChip>
              <IssueChip onClick={open}><Badge variant="outline" className="border-border/40">frontend: {scan.frontend_error_count}</Badge></IssueChip>
              <IssueChip onClick={open}><Badge variant="outline" className="border-border/40">recurrentes: {recurring.length}</Badge></IssueChip>
            </div>
            <p className="text-[10px] text-muted-foreground">
              error_rate:{" "}
              {scan.backend_error_rate_pct != null ? (
                <span className={scan.backend_error_rate_pct > 1.5 ? "text-red-500" : scan.backend_error_rate_pct > 0.5 ? "text-amber-500" : "text-green-500"}>
                  {scan.backend_error_rate_pct}%
                </span>
              ) : "sin tráfico en ventana"}
              {" · "}Railway 5xx: {data?.coverage.railway_api_active ? scan.railway_5xx_count : "no integrado (V1)"}
            </p>
            <p className="text-[10px] text-muted-foreground">
              24h: {data?.last_24h.total_errors_backend} backend · {data?.last_24h.total_errors_frontend} frontend
            </p>
            {(recurring.length > 0 || top.length > 0) && (
              <button onClick={() => setExpanded((v) => !v)} className="text-xs text-primary hover:underline">
                {expanded ? "Ocultar" : "Ver patrones / top signatures"}
              </button>
            )}
            {expanded && (
              <div className="space-y-1">
                {recurring.map((r, i) => (
                  <div key={`r${i}`} className="rounded border border-border/40 p-2 text-[10px]">
                    <span className="font-medium">{r.source}</span> · {r.sample} <span className="text-muted-foreground">x{r.count}</span>
                  </div>
                ))}
                {top.map((t, i) => (
                  <div key={`t${i}`} className="rounded border border-border/40 p-2 text-[10px]">
                    <span className="font-mono">{t.signature}</span> · {t.message} <span className="text-muted-foreground">x{t.count} (24h)</span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
