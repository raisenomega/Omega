import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ExternalLink, ChevronRight } from "lucide-react";
import { useHermesData, type HermesIntegration } from "@/hooks/useSecurityDevData";
import { effectiveStatus, integrationLabel, integrationUrl, statusInfo } from "./hermes-labels";
import { fmtDateTime, relativeAgo, Section } from "./parts";
import { HermesDetailModal } from "./HermesDetailModal";

// HERMES · salud de integraciones externas (estado actual · §8 cero jerga).
// Orden por severidad (statusInfo.rank): fallidas/amarillas arriba. Cada fila → drill-down (modal).
export function HermesTab() {
  const { data, isLoading, error } = useHermesData();
  const [selected, setSelected] = useState<string | null>(null);

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
          <div key={it.integration} role="button" tabIndex={0} onClick={() => setSelected(it.integration)}
               className="cursor-pointer border-b border-border/40 py-2 text-sm hover:bg-muted/30">
            <div className="flex items-center justify-between gap-2">
              <span className="font-medium">{integrationLabel(it.integration)}</span>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className={st.cls} title={st.meaning}>{st.label}</Badge>
                <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
              </div>
            </div>
            <p className="text-xs text-muted-foreground">Último chequeo: {fmtDateTime(it.checked_at)} ({relativeAgo(it.checked_at)})</p>
            <p className="text-xs text-muted-foreground">Último uso real: {it.last_use ? fmtDateTime(it.last_use) : "sin uso registrado"}</p>
            <p className="text-xs text-muted-foreground">{desdeLabel}: {fmtDateTime(it.created_at)}</p>
            {url && (
              <a href={url} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()}
                 className="inline-flex items-center gap-1 text-xs text-primary hover:underline">
                Abrir consola <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </div>
        );
      })}
      {selected && <HermesDetailModal integration={selected} onClose={() => setSelected(null)} />}
    </Section>
  );
}
