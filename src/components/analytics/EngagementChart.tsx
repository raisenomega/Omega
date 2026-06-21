import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Cell } from "recharts";
import { PLATFORM_COLORS, type Platform } from "@/lib/onboarding-constants";

interface EngagementRow {
  platform: string;
  likes: number;
  comments: number;
  shares: number;
  saves: number;
  views: number;
}

interface EngagementChartProps {
  data: EngagementRow[];
}

const chartConfig = {
  likes: { label: "Likes", color: "hsl(var(--chart-1))" },
  comments: { label: "Comentarios", color: "hsl(var(--chart-2))" },
  shares: { label: "Compartidos", color: "hsl(var(--chart-3))" },
  saves: { label: "Guardados", color: "hsl(var(--chart-4))" },
  views: { label: "Vistas", color: "hsl(var(--chart-5))" },
};

function colorFor(platform: string): string {
  const key = platform.toLowerCase() as Platform;
  return key in PLATFORM_COLORS ? PLATFORM_COLORS[key] : "#9CA3AF";
}

export function EngagementChart({ data }: EngagementChartProps) {
  if (data.length === 0) {
    return (
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardHeader className="pb-2"><CardTitle className="text-sm">Engagement por plataforma</CardTitle></CardHeader>
        <CardContent className="flex items-center justify-center h-56 text-xs text-muted-foreground text-center">
          Sin engagement aún · publica contenido para ver métricas
        </CardContent>
      </Card>
    );
  }
  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Engagement por plataforma · del período</CardTitle>
      </CardHeader>
      <CardContent className="pt-2">
        <ChartContainer config={chartConfig} className="h-64 w-full">
          <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border/30" />
            <XAxis dataKey="platform" tick={{ fontSize: 10 }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 10 }} tickLine={false} axisLine={false} width={40} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey="likes" radius={[4, 4, 0, 0]}>
              {data.map((d, i) => <Cell key={i} fill={colorFor(d.platform)} />)}
            </Bar>
            <Bar dataKey="comments" fill="hsl(var(--chart-2))" radius={[4, 4, 0, 0]} fillOpacity={0.7} />
            <Bar dataKey="shares" fill="hsl(var(--chart-3))" radius={[4, 4, 0, 0]} fillOpacity={0.5} />
            <Bar dataKey="saves" fill="hsl(var(--chart-4))" radius={[4, 4, 0, 0]} fillOpacity={0.5} />
            <Bar dataKey="views" fill="hsl(var(--chart-5))" radius={[4, 4, 0, 0]} fillOpacity={0.35} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
