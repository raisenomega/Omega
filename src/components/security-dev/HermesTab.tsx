import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useHermesData, type HermesIntegration } from "@/hooks/useSecurityDevData";
import { integrationLabel, statusInfo } from "./hermes-labels";
import { relativeAgo, Section } from "./parts";

// HERMES · salud de integraciones externas (estado actual · §8 cero jerga).
// Orden: fallidas arriba (rank 0), luego operativas, luego sin configurar.
export function HermesTab() {
  const { data, isLoading, error } = useHermesData();

  if (isLoading) return <Skeleton className="h-64 w-full" />;
  const err = (error as Error)?.message ?? data?.error;
  if (err) return <p className="text-sm text-red-500">Error: {err}</p>;

  const rows = [...(data?.integrations ?? [])].sort(
    (a, b) => statusInfo(a.status).rank - statusInfo(b.status).rank,
  );

  return (
    <Section
      title="Integraciones externas"
      empty={rows.length === 0}
      emptyText="HERMES aún no registró integraciones. El monitor corre cada 5 min."
    >
      {rows.map((it: HermesIntegration) => {
        const st = statusInfo(it.status);
        const latido = it.last_use ?? it.checked_at;
        return (
          <div key={it.integration} className="flex items-center justify-between gap-2 border-b border-border/40 py-2 text-sm">
            <span className="font-medium">{integrationLabel(it.integration)}</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">{relativeAgo(latido)}</span>
              <Badge variant="outline" className={st.cls}>{st.label}</Badge>
            </div>
          </div>
        );
      })}
    </Section>
  );
}
