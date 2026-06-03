import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useAIProvidersStatus, type AIProvider } from "@/hooks/useAIProvidersStatus";

function ProviderRow({ p }: { p: AIProvider }) {
  const cls = p.configured
    ? "bg-green-500/15 text-green-500 border-green-500/40"
    : "bg-muted/40 text-muted-foreground border-border/40";
  const s = p.last_24h;
  return (
    <div className="space-y-0.5 border-b border-border/40 py-1.5 text-sm">
      <div className="flex items-center justify-between gap-2">
        <span className="font-medium">{p.name}</span>
        <div className="flex items-center gap-2">
          {p.circuit_state === "open" && (
            <Badge variant="outline" className="border-red-500/40 bg-red-500/15 text-red-500">circuito abierto</Badge>
          )}
          <Badge variant="outline" className={cls} title={p.reason_not_configured ?? ""}>
            {p.configured ? "configurado" : "no configurado"}
          </Badge>
        </div>
      </div>
      {p.configured ? (
        <p className="text-[10px] text-muted-foreground">
          24h: {s.total_calls} calls · {s.success} ok / {s.failed} fail
          {s.avg_latency_ms != null ? ` · ${s.avg_latency_ms}ms prom` : ""}
          {s.failover_triggered_count ? ` · ${s.failover_triggered_count} failover` : ""}
        </p>
      ) : (
        <p className="text-[10px] text-muted-foreground">{p.reason_not_configured}</p>
      )}
    </div>
  );
}

export function SentinelAIProvidersCard() {
  const { data, isLoading } = useAIProvidersStatus();
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">AI Providers</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {isLoading || !data ? (
          <Skeleton className="h-24 w-full" />
        ) : (
          <>
            {data.providers.map((p) => <ProviderRow key={p.name} p={p} />)}
            <div className="space-y-1 pt-1">
              <span className="text-xs font-medium">Cobertura</span>
              <Badge variant="outline" className="ml-2 border-amber-500/40 bg-amber-500/15 text-amber-500">
                {data.coverage_percentage_unknown ? "parcial · % pendiente" : `${data.pct_calls_covered_by_router}%`}
              </Badge>
              <p className="text-[10px] text-muted-foreground">
                Path canónico (anthropic_adapter) instrumentado · {data.total_router_calls_24h} calls 24h por router.
                Paths legacy sin instrumentar (unificación pendiente):
              </p>
              {data.coverage_summary.legacy_paths_uncovered.map((l) => (
                <p key={l.name} className="text-[10px] text-muted-foreground">
                  · {l.name} ({l.callers_count} callers · {l.debt})
                </p>
              ))}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
