import { Users, TrendingUp, Clock, FileText, type LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface AnalyticsKPIsProps {
  followers: number;
  engagement: number;
  bestHour: string;
  posts: number;
}

interface KPI {
  label: string;
  value: string;
  icon: LucideIcon;
}

function fmtNumber(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return String(n);
}

export function AnalyticsKPIs({ followers, engagement, bestHour, posts }: AnalyticsKPIsProps) {
  const kpis: KPI[] = [
    { label: "Seguidores", value: fmtNumber(followers), icon: Users },
    { label: "Engagement", value: `${engagement.toFixed(2)}%`, icon: TrendingUp },
    { label: "Mejor hora", value: bestHour, icon: Clock },
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
