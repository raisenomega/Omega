import { Users, TrendingUp, Clock, FileText, type LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface AnalyticsKPIsProps {
  followers: number | null;
  engagement: number | null;
  bestHour: string | null;
  posts: number | null;
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

function fmtPct(n: number | null): string {
  return n === null ? EMPTY : `${n.toFixed(2)}%`;
}

export function AnalyticsKPIs({ followers, engagement, bestHour, posts }: AnalyticsKPIsProps) {
  const kpis: KPI[] = [
    { label: "Seguidores", value: fmtNumber(followers), icon: Users },
    { label: "Engagement", value: fmtPct(engagement), icon: TrendingUp },
    { label: "Mejor hora", value: bestHour ?? EMPTY, icon: Clock },
    { label: "Posts", value: fmtNumber(posts), icon: FileText },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
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
