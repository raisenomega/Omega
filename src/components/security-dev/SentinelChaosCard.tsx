import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, Zap } from "lucide-react";
import { useChaosStatus, useTriggerChaos } from "@/hooks/useChaosStatus";
import { scoreColor, IssueChip } from "./parts";
import type { OpenIssuesParams } from "@/lib/sentinel_issue_loaders";

const RESULT_CLS: Record<string, string> = {
  passed: "bg-green-500/15 text-green-500 border-green-500/40",
  partial: "bg-amber-500/15 text-amber-500 border-amber-500/40",
  failed: "bg-red-500/15 text-red-500 border-red-500/40",
  skipped: "bg-muted/40 text-muted-foreground border-border/40",
};

export function SentinelChaosCard({ onOpenIssues }: { onOpenIssues?: (p: OpenIssuesParams) => void }) {
  const { data, isLoading } = useChaosStatus();
  const trigger = useTriggerChaos();
  const scenarios = data?.scenarios ?? [];
  const failed = scenarios.filter((s) => s.result === "failed" || s.result === "partial").length;
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm">Chaos Engineering</CardTitle>
        <Button size="sm" variant="outline" onClick={() => trigger.mutate(undefined)} disabled={trigger.isPending}>
          {trigger.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
          <span className="ml-2">{trigger.isPending ? "Corriendo…" : "Disparar chaos test"}</span>
        </Button>
      </CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <Skeleton className="h-24 w-full" />
        ) : !data || scenarios.length === 0 ? (
          <p className="text-xs text-muted-foreground">Sin chaos tests aún · corré "Disparar chaos test" o esperá el cron (1er lunes/mes).</p>
        ) : (
          <>
            <div className="flex items-baseline gap-3">
              <span className={`text-4xl font-bold ${scoreColor(data.score ?? 0)}`}>{data.score}</span>
              <span className="text-sm text-muted-foreground">/100</span>
              {failed > 0 && onOpenIssues && (
                <IssueChip onClick={() => onOpenIssues({ sourceType: "chaos", scopeLabel: "Chaos Engineering" })}>
                  <Badge variant="outline" className={RESULT_CLS.failed}>{failed} con fallo</Badge>
                </IssueChip>
              )}
            </div>
            {scenarios.map((s) => (
              <div key={s.id} className="flex items-center justify-between gap-2 border-b border-border/40 py-1 text-xs">
                <span className="font-mono">{s.scenario}</span>
                <span className="flex items-center gap-2">
                  {s.recovery_time_ms != null && <span className="text-[10px] text-muted-foreground">{s.recovery_time_ms}ms</span>}
                  <Badge variant="outline" className={RESULT_CLS[s.result] ?? RESULT_CLS.skipped}>{s.result}</Badge>
                </span>
              </div>
            ))}
            {data.coverage_note && <p className="text-[10px] text-muted-foreground">{data.coverage_note}</p>}
          </>
        )}
      </CardContent>
    </Card>
  );
}
