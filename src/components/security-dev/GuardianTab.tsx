import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useGuardianData } from "@/hooks/useSecurityDevData";
import { Section, SEV_CLS, LIST_CLS, relativeAgo } from "./parts";

export function GuardianTab() {
  const { data, isLoading, error } = useGuardianData();

  if (isLoading) return <Skeleton className="h-64 w-full" />;
  const err = (error as Error)?.message ?? data?.error;
  if (err) return <p className="text-sm text-red-500">Error: {err}</p>;
  const d = data!;

  return (
    <div className="space-y-4">
      <Section title="Eventos recientes" empty={d.logs.length === 0} emptyText="Sin eventos de seguridad registrados.">
        {d.logs.slice(0, 10).map((l) => (
          <div key={l.id} className="flex items-center justify-between gap-2 border-b border-border/40 py-1 text-xs">
            <span className="font-medium">{l.event_type}</span>
            <span className="text-muted-foreground">{l.ip_address ?? "—"}</span>
            <span>riesgo {l.risk_score}</span>
            <span className="text-muted-foreground">{relativeAgo(l.created_at)}</span>
          </div>
        ))}
      </Section>
      <Section title="Incidentes" empty={d.incidents.length === 0} emptyText="Sin incidentes activos.">
        {d.incidents.map((i) => (
          <div key={i.id} className="flex items-center justify-between gap-2 border-b border-border/40 py-1 text-xs">
            <span className="font-medium">{i.incident_type}</span>
            <Badge variant="outline" className={SEV_CLS[i.severity] ?? SEV_CLS.low}>{i.severity}</Badge>
            <span className="text-muted-foreground">{i.status}</span>
          </div>
        ))}
      </Section>
      <Section title="IP Watchlist" empty={d.watchlist.length === 0} emptyText="Watchlist vacía.">
        {d.watchlist.map((w) => (
          <div key={w.id} className="flex items-center justify-between gap-2 border-b border-border/40 py-1 text-xs">
            <span className="font-mono">{w.ip_address}</span>
            <Badge variant="outline" className={LIST_CLS[w.list_type] ?? LIST_CLS.watch}>{w.list_type}</Badge>
            <span className="max-w-[40%] truncate text-muted-foreground">{w.reason ?? "—"}</span>
          </div>
        ))}
      </Section>
    </div>
  );
}
