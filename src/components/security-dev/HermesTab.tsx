import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ExternalLink } from "lucide-react";
import { useHermesData, type HermesIntegration } from "@/hooks/useSecurityDevData";
import { effectiveStatus, integrationLabel, integrationUrl, statusInfo } from "./hermes-labels";
import { fmtDateTime, relativeAgo, Section } from "./parts";

// HERMES · salud de integraciones externas (estado actual · §8 cero jerga).
// Orden por severidad (statusInfo.rank): fallidas/amarillas arriba, luego operativas.
export function HermesTab() {
  const { data, isLoading, error } = useHermesData();

  if (isLoading) return <Skeleton className="h-64 w-full" />;
  const err = (error as Error)?.message ?? data?.error;
  if (err) return <p className="text-sm text-red-500">Error: {err}</p>;

  const rows = [...(data?.integrations ?? [])]
    .sort((a, b) => statusInfo(effectiveStatus(a)).rank - statusInfo(effectiveStatus(b)).rank);

  return (
    <Section
      title="Integraciones externas"
      empty={rows.length === 0}
      emptyText="HERMES aún no registró integraciones. El monitor corre cada 5 min."
    >
      {rows.map((it: HermesIntegration) => {
        const st = statusInfo(effectiveStatus(it));
        const url = integrationUrl(it.integration);
        const desdeLabel = it.status === "ok" ? "Operativa desde" : "En este estado desde";
        return (
          <div key={it.integration} className="border-b border-border/40 py-2 text-sm">
            <div className="flex items-center justify-between gap-2">
              <span className="font-medium">{integrationLabel(it.integration)}</span>
              <Badge variant="outline" className={st.cls} title={st.meaning}>{st.label}</Badge>
            </div>
            <p className="text-xs text-muted-foreground">Último chequeo: {fmtDateTime(it.checked_at)} ({relativeAgo(it.checked_at)})</p>
            <p className="text-xs text-muted-foreground">Último uso real: {it.last_use ? fmtDateTime(it.last_use) : "sin uso registrado"}</p>
            <p className="text-xs text-muted-foreground">{desdeLabel}: {fmtDateTime(it.created_at)}</p>
            {url && (
              <a href={url} target="_blank" rel="noopener noreferrer"
                 className="inline-flex items-center gap-1 text-xs text-primary hover:underline">
                Abrir consola <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </div>
        );
      })}
    </Section>
  );
}
