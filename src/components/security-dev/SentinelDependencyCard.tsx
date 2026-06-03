import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ExternalLink } from "lucide-react";
import { useDependencyScans } from "@/hooks/useSecurityDevData";
import { fmtDateTime, IssueChip } from "./parts";
import type { OpenIssuesParams } from "@/lib/sentinel_issue_loaders";

const STATUS_CLS: Record<string, string> = {
  passed: "bg-green-500/15 text-green-500 border-green-500/40",
  warn: "bg-amber-500/15 text-amber-500 border-amber-500/40",
  failed: "bg-red-500/15 text-red-500 border-red-500/40",
};
const GH_ACTIONS = "https://github.com/raisenomega/Omega/actions";

interface DepJs { critical?: number; high?: number; moderate?: number; low?: number; total?: number }
interface DepSummary { js?: DepJs; python?: { high?: number; medium?: number } }

export function SentinelDependencyCard({ onOpenIssues }: { onOpenIssues?: (p: OpenIssuesParams) => void }) {
  const { data, isLoading } = useDependencyScans();
  const latest = data?.latest ?? null;
  const s = (latest?.summary ?? {}) as DepSummary;
  const open = () => onOpenIssues?.({ sourceType: "dependency_scan", scopeLabel: "Dependencias y CVEs" });
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Dependencias y CVEs</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <Skeleton className="h-16 w-full" />
        ) : !latest ? (
          <p className="text-xs text-muted-foreground">Sin scans aún. Corré "SENTINEL Dependency Scan" en GitHub Actions.</p>
        ) : (
          <>
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-medium">{latest.scan_type}</span>
              <Badge variant="outline" className={STATUS_CLS[latest.status] ?? "bg-muted/40 text-muted-foreground border-border/40"}>{latest.status}</Badge>
            </div>
            {s.js && (
              <div className="flex flex-wrap items-center gap-2 text-[10px] text-muted-foreground">
                <span>JS: {s.js.critical ?? 0} critical · {s.js.high ?? 0} high · {s.js.moderate ?? 0} moderate</span>
                {((s.js.critical ?? 0) + (s.js.high ?? 0) + (s.js.moderate ?? 0)) > 0 && onOpenIssues && (
                  <IssueChip onClick={open}>
                    <Badge variant="outline" className={(s.js.critical ?? 0) > 0 ? STATUS_CLS.failed : STATUS_CLS.warn}>
                      {(s.js.critical ?? 0) > 0 ? `${s.js.critical} critical` : `${s.js.moderate ?? 0} moderate`}
                    </Badge>
                  </IssueChip>
                )}
              </div>
            )}
            {s.python && (
              <div className="flex flex-wrap items-center gap-2 text-[10px] text-muted-foreground">
                <span>Python: {s.python.high ?? 0} high · {s.python.medium ?? 0} low-noise (test/standard · accepted)</span>
                {((s.python.high ?? 0) + (s.python.medium ?? 0)) > 0 && onOpenIssues && (
                  <IssueChip onClick={open}><Badge variant="outline" className={(s.python.high ?? 0) > 0 ? STATUS_CLS.failed : STATUS_CLS.warn}>{(s.python.high ?? 0)} high · {(s.python.medium ?? 0)} noise</Badge></IssueChip>
                )}
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              {fmtDateTime(latest.created_at)}{latest.github_run_id ? ` · run ${latest.github_run_id}` : ""}
            </p>
          </>
        )}
        <a href={GH_ACTIONS} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-xs text-primary hover:underline">
          Ver en GitHub Actions <ExternalLink className="h-3 w-3" />
        </a>
      </CardContent>
    </Card>
  );
}
