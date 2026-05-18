import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

interface HeatmapCell {
  day: string;
  hour: number;
  value: number;
}

interface ScheduleHeatmapProps {
  data: HeatmapCell[];
}

function getColor(value: number) {
  if (value >= 80) return "bg-primary/90";
  if (value >= 60) return "bg-primary/60";
  if (value >= 40) return "bg-primary/35";
  if (value >= 20) return "bg-primary/15";
  return "bg-muted/40";
}

const days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];
const hours = Array.from({ length: 18 }, (_, i) => i + 6);

export function ScheduleHeatmap({ data }: ScheduleHeatmapProps) {
  const lookup = new Map(data.map((d) => [`${d.day}-${d.hour}`, d.value]));

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-base">Mejores Horarios para Publicar</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div className="min-w-[600px]">
            {/* Hour labels */}
            <div className="flex gap-1 mb-1 ml-10">
              {hours.map((h) => (
                <div key={h} className="flex-1 text-center text-[10px] text-muted-foreground">
                  {h}h
                </div>
              ))}
            </div>
            {/* Rows */}
            {days.map((day) => (
              <div key={day} className="flex gap-1 mb-1 items-center">
                <span className="w-10 text-xs text-muted-foreground shrink-0">{day}</span>
                {hours.map((hour) => {
                  const val = lookup.get(`${day}-${hour}`) ?? 0;
                  return (
                    <Tooltip key={hour}>
                      <TooltipTrigger asChild>
                        <div
                          className={`flex-1 aspect-square rounded-sm ${getColor(val)} transition-colors cursor-default min-h-[18px]`}
                        />
                      </TooltipTrigger>
                      <TooltipContent side="top" className="text-xs">
                        {day} {hour}:00 — Engagement: {val}%
                      </TooltipContent>
                    </Tooltip>
                  );
                })}
              </div>
            ))}
            {/* Legend */}
            <div className="flex items-center gap-2 mt-3 ml-10">
              <span className="text-[10px] text-muted-foreground">Bajo</span>
              <div className="w-4 h-3 rounded-sm bg-muted/40" />
              <div className="w-4 h-3 rounded-sm bg-primary/15" />
              <div className="w-4 h-3 rounded-sm bg-primary/35" />
              <div className="w-4 h-3 rounded-sm bg-primary/60" />
              <div className="w-4 h-3 rounded-sm bg-primary/90" />
              <span className="text-[10px] text-muted-foreground">Alto</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
