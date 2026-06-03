import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, ShieldCheck } from "lucide-react";
import { useRLSAuditLatest, useTriggerRLSAudit } from "@/hooks/useRLSAudit";
import { IssueChip } from "./parts";
import type { OpenIssuesParams } from "@/lib/sentinel_issue_loaders";

const SEV_CLS: Record<string, string> = {
  CRITICAL: "bg-red-500/15 text-red-500 border-red-500/40",
  HIGH: "bg-orange-500/15 text-orange-500 border-orange-500/40",
  MEDIUM: "bg-amber-500/15 text-amber-500 border-amber-500/40",
};

export function SentinelRLSCard({ onOpenIssues }: { onOpenIssues?: (p: OpenIssuesParams) => void }) {
  const { data, isLoading } = useRLSAuditLatest();
  const trigger = useTriggerRLSAudit();
  const [expanded, setExpanded] = useState(false);
  const latest = data?.latest ?? null;
  const issues = latest?.issues ?? [];
  const open = (severity: string, label: string) =>
    onOpenIssues?.({ sourceType: "rls_audit", severity, scopeLabel: `RLS · ${label}` });

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm">RLS Hardening</CardTitle>
        <Button size="sm" variant="outline" onClick={() => trigger.mutate()} disabled={trigger.isPending}>
          {trigger.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShieldCheck className="h-4 w-4" />}
          <span className="ml-2">{trigger.isPending ? "Auditando…" : "Auditar ahora"}</span>
        </Button>
      </CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <Skeleton className="h-16 w-full" />
        ) : !latest ? (
          <p className="text-xs text-muted-foreground">Sin auditorías aún. Corré "Auditar ahora".</p>
        ) : (
          <>
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="text-muted-foreground">{latest.total_tables} tablas ·</span>
              {latest.total_issues === 0 ? (
                <Badge variant="outline" className={SEV_CLS.CRITICAL.replace("red", "green")}>RLS limpio ✅</Badge>
              ) : (
                <>
                  <IssueChip onClick={() => open("CRITICAL", "críticos")}>
                    <Badge variant="outline" className={SEV_CLS.CRITICAL}>críticos {latest.severity_critical}</Badge>
                  </IssueChip>
                  <IssueChip onClick={() => open("HIGH", "altos")}>
                    <Badge variant="outline" className={SEV_CLS.HIGH}>altos {latest.severity_high}</Badge>
                  </IssueChip>
                  <IssueChip onClick={() => open("MEDIUM", "medios")}>
                    <Badge variant="outline" className={SEV_CLS.MEDIUM}>medios {latest.severity_medium}</Badge>
                  </IssueChip>
                </>
              )}
            </div>
            {issues.length > 0 && (
              <button onClick={() => setExpanded((v) => !v)} className="text-xs text-primary hover:underline">
                {expanded ? "Ocultar" : `Ver top ${Math.min(5, issues.length)}`}
              </button>
            )}
            {expanded && issues.slice(0, 5).map((it, i) => (
              <div key={i} className="rounded border border-border/40 p-2 text-xs">
                <span className="font-medium">{it.severity}</span> · <span className="font-mono">{it.table}</span> · {it.issue_type}
                <p className="text-[10px] text-muted-foreground">{it.detail}</p>
              </div>
            ))}
          </>
        )}
      </CardContent>
    </Card>
  );
}
