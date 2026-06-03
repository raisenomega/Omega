import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useNetworkHTTPStatus, type NetworkTarget } from "@/hooks/useNetworkHTTPStatus";
import { scoreColor, IssueChip } from "./parts";
import type { OpenIssuesParams } from "@/lib/sentinel_issue_loaders";

function TargetBlock({ t, onOpenIssues }: { t: NetworkTarget; onOpenIssues?: (p: OpenIssuesParams) => void }) {
  const s = t.last_scan;
  const host = t.url.replace(/^https?:\/\//, "");
  if (!s) return <div className="border-b border-border/40 py-1.5 text-xs"><span className="font-medium">{host}</span> · <span className="text-muted-foreground">sin scans aún</span></div>;
  const tls = s.tls_check;
  const missing = s.headers_check.missing ?? [];
  const present = Object.keys(s.headers_check.present ?? {});
  return (
    <div className="space-y-1 border-b border-border/40 py-2 text-xs">
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium">{host}</span>
        <span className="flex items-center gap-2">
          <span className={`font-semibold ${scoreColor(s.score)}`}>{s.score}</span>
          {s.issues.length > 0 && onOpenIssues && (
            <IssueChip onClick={() => onOpenIssues({ sourceType: "network_http", scopeLabel: host })}>
              <Badge variant="outline" className="border-amber-500/40 bg-amber-500/15 text-amber-500">{s.issues.length} issues</Badge>
            </IssueChip>
          )}
        </span>
      </div>
      <p className="text-[10px] text-muted-foreground">
        Headers: {present.length} ok{missing.length ? ` · faltan: ${missing.join(", ")}` : " · completos"}
        {s.headers_check.csp_mode ? ` · CSP: ${s.headers_check.csp_mode}` : ""}
      </p>
      <p className="text-[10px] text-muted-foreground">
        TLS: {tls.error ? `error (${tls.error})` : `${tls.version} · vence en ${tls.days_until_expiry}d (${tls.cert_issuer ?? "?"})`}
      </p>
      {s.rate_limit_check && (
        <p className="text-[10px] text-muted-foreground">
          Rate limit: {s.rate_limit_check.active ? `${s.rate_limit_check.limit_per_minute}/min · ${s.rate_limit_check.scope}` : "inactivo"}
        </p>
      )}
      {s.cors_check && (
        <p className="text-[10px] text-muted-foreground">
          CORS: {s.cors_check.wildcard_detected ? "wildcard (!)" : s.cors_check.reflects_untrusted ? "refleja origen no-confiable (!)" : "hardened"}
        </p>
      )}
    </div>
  );
}

export function SentinelNetworkHTTPCard({ onOpenIssues }: { onOpenIssues?: (p: OpenIssuesParams) => void }) {
  const { data, isLoading } = useNetworkHTTPStatus();
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Red y HTTP</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <Skeleton className="h-24 w-full" />
        ) : !data || data.targets.every((t) => !t.last_scan) ? (
          <p className="text-xs text-muted-foreground">Sin scans aún · el worker corre cada 2h.</p>
        ) : (
          <>
            {data.overall_score != null && (
              <div className="flex items-baseline gap-3">
                <span className={`text-4xl font-bold ${scoreColor(data.overall_score)}`}>{data.overall_score}</span>
                <span className="text-sm text-muted-foreground">/100 · global</span>
              </div>
            )}
            {data.targets.map((t) => <TargetBlock key={t.url} t={t} onOpenIssues={onOpenIssues} />)}
            <p className="text-[10px] text-muted-foreground">{data.coverage_note}</p>
          </>
        )}
      </CardContent>
    </Card>
  );
}
