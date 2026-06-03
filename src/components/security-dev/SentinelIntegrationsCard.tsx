import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useIntegrationsStatus } from "@/hooks/useIntegrationsStatus";
import { scoreColor, IssueChip } from "./parts";
import type { OpenIssuesParams } from "@/lib/sentinel_issue_loaders";

export function SentinelIntegrationsCard({ onOpenIssues }: { onOpenIssues?: (p: OpenIssuesParams) => void }) {
  const { data, isLoading } = useIntegrationsStatus();
  const s = data?.last_scan ?? null;
  const w = s?.stripe_webhooks_check;
  const o = s?.oauth_check;
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Integraciones</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <Skeleton className="h-24 w-full" />
        ) : !s || !w || !o ? (
          <p className="text-xs text-muted-foreground">Sin scans aún · el worker corre cada hora.</p>
        ) : (
          <>
            <div className="flex items-baseline gap-3">
              <span className={`text-4xl font-bold ${scoreColor(s.score)}`}>{s.score}</span>
              <span className="text-sm text-muted-foreground">/100</span>
              {s.issues.length > 0 && onOpenIssues && (
                <IssueChip onClick={() => onOpenIssues({ sourceType: "integrations", scopeLabel: "Integraciones" })}>
                  <Badge variant="outline" className="border-amber-500/40 bg-amber-500/15 text-amber-500">{s.issues.length} issues</Badge>
                </IssueChip>
              )}
            </div>
            <p className="text-[10px] text-muted-foreground">
              Stripe webhooks: {w.event_count_24h} en 24h · idempotencia X4 {w.idempotency_enforced === true ? "enforced" : w.idempotency_enforced === false ? "NO ENFORCED" : "no verificable"} · liveness {w.stripe_liveness ?? w.liveness_note}
            </p>
            <p className="text-[10px] text-muted-foreground">
              Stripe Connect: {s.stripe_connect_check.with_stripe_account}/{s.stripe_connect_check.total_resellers} resellers con cuenta
            </p>
            <div className="space-y-0.5">
              <span className="text-xs font-medium">OAuth · {o.total} cuentas · {o.expiring_24h} vencen 24h · {o.expiring_7d} vencen 7d</span>
              {o.per_platform.map((p) => (
                <p key={p.platform} className="text-[10px] text-muted-foreground">
                  {p.platform}: {p.count} · {p.connected} conectadas{p.expiring_24h || p.expiring_7d ? ` · ${p.expiring_24h}/${p.expiring_7d} venciendo` : ""}
                </p>
              ))}
            </div>
            {s.coverage_note && <p className="text-[10px] text-muted-foreground">{s.coverage_note}</p>}
          </>
        )}
      </CardContent>
    </Card>
  );
}
