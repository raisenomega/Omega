import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface HeatmapCell { day: string; hour: number; value: number }
interface BestTimesHeatmapProps { data: HeatmapCell[] }

const DAYS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"] as const;
const HOURS = Array.from({ length: 24 }, (_, i) => i);

function cellColor(value: number, max: number): string {
  if (value <= 0 || max <= 0) return "rgba(148, 163, 184, 0.15)"; // slate-400/15 gris claro
  const intensity = Math.min(value / max, 1);
  return `rgba(16, 185, 129, ${0.15 + intensity * 0.75})`; // emerald-500 scale
}

export function BestTimesHeatmap({ data }: BestTimesHeatmapProps) {
  const max = data.reduce((m, d) => Math.max(m, d.value), 0);
  const lookup = new Map<string, number>();
  for (const d of data) lookup.set(`${d.day}|${d.hour}`, d.value);

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Mejores horarios (engagement por hora)</CardTitle>
      </CardHeader>
      <CardContent className="pt-2 max-h-64 overflow-hidden">
        <div className="space-y-1">
          <div className="flex gap-0.5 pl-7">
            {HOURS.map((h) => (
              <span key={h} className="flex-1 text-center text-[8px] text-muted-foreground tabular-nums">
                {h % 6 === 0 ? h : ""}
              </span>
            ))}
          </div>
          {DAYS.map((day) => (
            <div key={day} className="flex items-center gap-0.5">
              <span className="w-7 text-[10px] text-muted-foreground shrink-0">{day}</span>
              {HOURS.map((h) => {
                const v = lookup.get(`${day}|${h}`) ?? 0;
                return (
                  <div
                    key={h}
                    className="flex-1 aspect-square rounded-sm"
                    style={{ background: cellColor(v, max) }}
                    title={`${day} ${h}h: ${v}`}
                  />
                );
              })}
            </div>
          ))}
          <div className="flex items-center gap-2 pt-1 text-[10px] text-muted-foreground">
            <span>Menos</span>
            <div className="flex gap-0.5">
              {[0.15, 0.35, 0.55, 0.75, 0.9].map((o) => (
                <div key={o} className="h-2 w-3 rounded-sm" style={{ background: `rgba(16, 185, 129, ${o})` }} />
              ))}
            </div>
            <span>Más</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
