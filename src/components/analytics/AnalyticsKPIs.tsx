import { Users, Eye, TrendingUp, type LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { fmtPct } from "@/lib/analytics-series";

interface AnalyticsKPIsProps {
  followers: number | null;
  totalReach: number | null;
  profileEngagement: number | null;   // ER histórico (Σinter/Σreach·100) · null → "—"
  networkLabel?: string | null;       // si hay red seleccionada → sufijo "· [Red]" (vista por-red)
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
// Todo ACUMULADO (la API no tiene ventana · NO "del período"). "Eng. promedio · histórico" = la ÚNICA
// métrica % · el label "histórico" es OBLIGATORIO (evita leerlo como ER comparable con Zernio).
// networkLabel → vista por-red: "· [Red]" en cada KPI para que el usuario sepa que NO es agregado.
export function AnalyticsKPIs({ followers, totalReach, profileEngagement, networkLabel }: AnalyticsKPIsProps) {
  const suf = networkLabel ? ` · ${networkLabel}` : "";
  const kpis: KPI[] = [
    { label: `Seguidores${suf}`, value: fmtNumber(followers), icon: Users },
    { label: `Alcance total${suf}`, value: fmtNumber(totalReach), icon: Eye },
    { label: `Eng. promedio · histórico${suf}`, value: fmtPct(profileEngagement), icon: TrendingUp },
  ];

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
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
