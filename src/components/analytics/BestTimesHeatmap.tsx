import { Star } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface HeatmapCell { day: string; hour: number; value: number }
interface BestTimesHeatmapProps { data: HeatmapCell[] }

// Día abreviado del backend (_DAY) → nombre completo para el "Mejor momento".
const FULL_DAY: Record<string, string> = {
  Dom: "Domingo", Lun: "Lunes", Mar: "Martes", Mié: "Miércoles",
  Jue: "Jueves", Vie: "Viernes", Sáb: "Sábado",
};

function fmtHour(h: number): string {
  return `${String(h).padStart(2, "0")}:00`;
}

// Compacto (FIX UI): solo el MEJOR slot (día + hora del mayor avg_engagement), sin grilla de % en cero.
// Empty honesto si no hay slots reales.
export function BestTimesHeatmap({ data }: BestTimesHeatmapProps) {
  const top = data.length > 0 ? data.reduce((m, c) => (c.value > m.value ? c : m)) : null;

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader className="pb-2"><CardTitle className="text-sm">Mejor momento para publicar</CardTitle></CardHeader>
      <CardContent className="pt-2 pb-3">
        {top ? (
          <div className="flex items-center gap-2 text-sm">
            <Star className="h-4 w-4 text-primary shrink-0" />
            <span className="font-medium">{FULL_DAY[top.day] ?? top.day} {fmtHour(top.hour)}</span>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground text-center py-2">
            Publicá contenido para descubrir tu mejor horario
          </p>
        )}
      </CardContent>
    </Card>
  );
}
