import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { engagementTotalSeries, type EngagementSeriesPoint } from "@/lib/analytics-series";

interface Props {
  data: EngagementSeriesPoint[];
}

const chartConfig = {
  engagement: { label: "Engagement", color: "hsl(var(--chart-2))" },
};

// Engagement en el tiempo = Σ interacciones (likes+comments+shares+saves) por día · 1 línea limpia.
// ACUMULADO (la serie viene all-history del backend · NO "del período"). Serie vacía → empty state
// honesto (no un chart plano en cero que finja actividad).
export function EngagementOverTimeChart({ data }: Props) {
  const series = engagementTotalSeries(data);
  if (series.length === 0) {
    return (
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardHeader className="pb-2"><CardTitle className="text-sm">Engagement en el tiempo · acumulado</CardTitle></CardHeader>
        <CardContent className="flex items-center justify-center h-56 text-xs text-muted-foreground text-center">
          Sin engagement aún · publica contenido para ver la evolución
        </CardContent>
      </Card>
    );
  }
  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader className="pb-2"><CardTitle className="text-sm">Engagement en el tiempo · acumulado</CardTitle></CardHeader>
      <CardContent className="pt-2">
        <ChartContainer config={chartConfig} className="h-56 w-full">
          <AreaChart data={series} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="engGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="hsl(var(--chart-2))" stopOpacity={0.4} />
                <stop offset="100%" stopColor="hsl(var(--chart-2))" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border/30" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} width={40} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Area type="monotone" dataKey="engagement" stroke="hsl(var(--chart-2))" fill="url(#engGrad)" strokeWidth={2} />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
