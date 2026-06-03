import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { usePerformanceStatus } from "@/hooks/usePerformanceStatus";
import { scoreColor, IssueChip } from "./parts";
import type { OpenIssuesParams } from "@/lib/sentinel_issue_loaders";

export function SentinelPerformanceCard({ onOpenIssues }: { onOpenIssues?: (p: OpenIssuesParams) => void }) {
  const { data, isLoading } = usePerformanceStatus();
  const [expanded, setExpanded] = useState(false);
  const scan = data?.last_scan ?? null;
  const endpoints = scan?.p95_per_endpoint ?? [];
  const slow = scan?.slow_queries ?? [];
  const issues = scan?.issues ?? [];
  const builds = data?.last_24h.bundle_size_trend ?? [];

  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Performance / APM</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <Skeleton className="h-20 w-full" />
        ) : !scan ? (
          <p className="text-xs text-muted-foreground">Sin scans aún. El worker corre cada 5 min.</p>
        ) : (
          <>
            <div className="flex items-baseline gap-3">
              <span className={`text-4xl font-bold ${scoreColor(scan.score)}`}>{scan.score}</span>
              <span className="text-sm text-muted-foreground">/100</span>
              {scan.score < 80 && (
                <Badge variant="outline" className="bg-amber-500/15 text-amber-500 border-amber-500/40">Atención</Badge>
              )}
            </div>
            {(issues.length > 0 || slow.length > 0) && onOpenIssues && (
              <div className="flex flex-wrap gap-2">
                {issues.length > 0 && (
                  <IssueChip onClick={() => onOpenIssues({ sourceType: "performance", scopeLabel: "Performance" })}>
                    <Badge variant="outline" className="border-amber-500/40 bg-amber-500/15 text-amber-500">{issues.length} issues</Badge>
                  </IssueChip>
                )}
                {slow.length > 0 && (
                  <IssueChip onClick={() => onOpenIssues({ sourceType: "performance", scopeLabel: "Performance · slow queries" })}>
                    <Badge variant="outline" className="border-amber-500/40 bg-amber-500/15 text-amber-500">{slow.length} slow queries</Badge>
                  </IssueChip>
                )}
              </div>
            )}
            <p className="text-[10px] text-muted-foreground">
              bundle: {scan.bundle_size_kb != null ? `${scan.bundle_size_kb}kb` : "sin build aún"} · recursos backend:{" "}
              {data?.coverage.railway_metrics_active ? `${scan.memory_pct}% mem` : "Railway no integrado (V1)"}
            </p>
            <button onClick={() => setExpanded((v) => !v)} className="text-xs text-primary hover:underline">
              {expanded ? "Ocultar" : `Ver p95 (${endpoints.length}) · slow queries (${slow.length})`}
            </button>
            {expanded && (
              <div className="space-y-1">
                {endpoints.slice(0, 5).map((e, i) => (
                  <div key={`e${i}`} className="flex items-center justify-between gap-2 rounded border border-border/40 p-2 text-[10px]">
                    <span className="font-mono">{e.path}</span>
                    <span className="text-muted-foreground">p95 {e.p95}ms · p99 {e.p99}ms · {e.calls} calls</span>
                  </div>
                ))}
                {slow.slice(0, 5).map((q, i) => (
                  <div key={`q${i}`} className="rounded border border-border/40 p-2 text-[10px]">
                    <span className="text-amber-500">slow query</span> · {q.mean_ms}ms x{q.calls}
                    <p className="font-mono text-muted-foreground">{q.query.slice(0, 80)}</p>
                  </div>
                ))}
                {builds.length > 0 && (
                  <p className="text-[10px] text-muted-foreground">
                    builds: {builds.map((b) => `${b.bundle_size_kb}kb`).join(" → ")}
                  </p>
                )}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
