import { Users, Clock, type LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface AnalyticsKPIsProps {
  followers: number | null;
  bestHour: string | null;
}

interface KPI {
  label: string;
  value: string;
  icon: LucideIcon;
}

const EMPTY = "—";

function fmtNumber(n: number | null): string {
  if (n === null) return EMPTY;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return String(n);
}

// Regla GLOBAL cero-sintéticos: sin dato real → "—" (vacío honesto), NUNCA un número de relleno.
// SIN KPI engagement % NI KPI Posts (decisión P1): la API no da ER por-post ni ventana 'this period'
// (el 5/7 vive solo en el panel UI · 7 date-params probados, ignorados) → solo Seguidores + Mejor hora
// (reales por profileId) + conteos por red abajo. Reintroducir Posts con fuente de ventana honesta.
export function AnalyticsKPIs({ followers, bestHour }: AnalyticsKPIsProps) {
  const kpis: KPI[] = [
    { label: "Seguidores", value: fmtNumber(followers), icon: Users },
    { label: "Mejor hora", value: bestHour ?? EMPTY, icon: Clock },
  ];

  return (
    <div className="grid grid-cols-2 gap-3">
      {kpis.map((k) => {
        const Icon = k.icon;
        return (
          <Card key={k.label} className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="p-3 flex items-center gap-3">
              <div className="h-9 w-9 shrink-0 rounded-lg bg-primary/10 flex items-center justify-center">
                <Icon className="h-4 w-4 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[10px] text-muted-foreground uppercase tracking-wide">{k.label}</p>
                <p className="text-lg font-semibold tabular-nums truncate">{k.value}</p>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
