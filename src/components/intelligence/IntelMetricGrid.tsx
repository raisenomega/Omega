import { Skeleton } from "@/components/ui/skeleton";

export interface MetricCell {
  label: string;
  value?: number;
}

interface IntelMetricGridProps {
  cells: MetricCell[];
}

// Grilla de métricas REALES (Fase 2). Solo muestra un número cuando viene del backend
// (value !== undefined). Si falta una métrica, esa celda dice "Sin datos" en vez de
// inventar un valor (regla cero-mocks). Compartido por GoogleIntelChip.
export function IntelMetricGrid({ cells }: IntelMetricGridProps) {
  return (
    <div className="grid grid-cols-3 gap-2">
      {cells.map((c) => (
        <div
          key={c.label}
          className="rounded-md border border-border/60 bg-muted/20 px-3 py-4 text-center"
        >
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground/70">{c.label}</p>
          <p className="mt-1 text-lg font-semibold text-foreground">
            {typeof c.value === "number" ? c.value.toLocaleString() : "—"}
          </p>
          {typeof c.value !== "number" && (
            <p className="text-[10px] text-muted-foreground/60">Sin datos</p>
          )}
        </div>
      ))}
    </div>
  );
}

export function IntelMetricGridSkeleton() {
  return (
    <div className="grid grid-cols-3 gap-2">
      {[0, 1, 2].map((i) => (
        <Skeleton key={i} className="h-[72px] w-full" />
      ))}
    </div>
  );
}
