import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import type { PostsSeriesPoint } from "@/lib/analytics-series";

interface Props {
  data: PostsSeriesPoint[];
}

const chartConfig = {
  count: { label: "Publicaciones", color: "hsl(var(--chart-3))" },
};

// Publicaciones por día (postCount real de Zernio · ACUMULADO · NO ventana 'this period').
// Serie vacía → empty state honesto (no barras en cero que finjan actividad).
export function PostsOverTimeChart({ data }: Props) {
  if (data.length === 0) {
    return (
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardHeader className="pb-2"><CardTitle className="text-sm">Publicaciones por día · acumulado</CardTitle></CardHeader>
        <CardContent className="flex items-center justify-center h-56 text-xs text-muted-foreground text-center">
          Sin publicaciones registradas aún
        </CardContent>
      </Card>
    );
  }
  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader className="pb-2"><CardTitle className="text-sm">Publicaciones por día · acumulado</CardTitle></CardHeader>
      <CardContent className="pt-2">
        <ChartContainer config={chartConfig} className="h-56 w-full">
          <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border/30" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} width={40} allowDecimals={false} />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey="count" fill="hsl(var(--chart-3))" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
