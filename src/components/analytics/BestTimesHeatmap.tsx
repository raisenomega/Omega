import { Star } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface HeatmapCell { day: string; hour: number; value: number }
interface BestTimesHeatmapProps { data: HeatmapCell[] }

// 12 horas (9am-9pm · todas caben sin scroll · spec FIX 2).
const PEAK_HOURS = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20];

function fmtHour(h: number): string {
  if (h === 0) return "12am";
  if (h < 12) return `${h}am`;
  if (h === 12) return "12pm";
  return `${h - 12}pm`;
}

export function BestTimesHeatmap({ data }: BestTimesHeatmapProps) {
  if (data.length === 0) {
    return (
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardHeader className="pb-2"><CardTitle className="text-sm">Mejores horas para publicar</CardTitle></CardHeader>
        <CardContent className="flex items-center justify-center h-32 text-xs text-muted-foreground text-center">
          Publica contenido para descubrir tus mejores horarios
        </CardContent>
      </Card>
    );
  }

  const byHour = new Map<number, number[]>();
  for (const d of data) {
    const arr = byHour.get(d.hour) ?? [];
    arr.push(d.value);
    byHour.set(d.hour, arr);
  }
  const hours = PEAK_HOURS.map((h) => {
    const vals = byHour.get(h) ?? [0];
    const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
    return { hour: h, value: Math.round(avg) };
  });
  const max = hours.reduce((m, h) => Math.max(m, h.value), 1);
  const top3 = new Set([...hours].sort((a, b) => b.value - a.value).slice(0, 3).map((h) => h.hour));

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader className="pb-2"><CardTitle className="text-sm">Mejores horas para publicar</CardTitle></CardHeader>
      <CardContent className="pt-2 pb-3 space-y-1 overflow-hidden">
        {hours.map(({ hour, value }) => {
          const pct = Math.round((value / max) * 100);
          const isTop = top3.has(hour);
          return (
            <div key={hour} className="flex items-center gap-2 text-xs">
              <span className="w-10 shrink-0 tabular-nums text-muted-foreground">{fmtHour(hour)}</span>
              <div className="flex-1 h-4 rounded bg-muted/40 overflow-hidden">
                <div className={`h-full rounded transition-all ${isTop ? "bg-primary" : "bg-muted-foreground/40"}`} style={{ width: `${pct}%` }} />
              </div>
              <span className="w-10 shrink-0 tabular-nums text-right text-muted-foreground">{pct}%</span>
              {isTop ? (
                <Badge variant="secondary" className="h-4 px-1.5 text-[10px] gap-0.5 shrink-0"><Star className="h-3 w-3" />Mejor</Badge>
              ) : <span className="w-12 shrink-0" />}
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
