import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PostsList } from "./PostsList";
import type { CalendarPost } from "@/hooks/useCalendarData";

const WD = ["L", "M", "X", "J", "V", "S", "D"];

function startOfWeek(day: string): Date {
  const [y, m, d] = day.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  dt.setUTCDate(dt.getUTCDate() - ((dt.getUTCDay() + 6) % 7));  // Lun=0
  return dt;
}
function iso(dt: Date): string { return dt.toISOString().slice(0, 10); }
function addDays(dt: Date, n: number): Date { const c = new Date(dt); c.setUTCDate(c.getUTCDate() + n); return c; }

interface WeekViewProps {
  anchorDay: string;        // selectedDay ?? hoy (lo resuelve el padre)
  month: string;            // mes cargado (YYYY-MM)
  setMonth: (m: string) => void;
  grouped: Map<string, CalendarPost[]>;
}

// Vista SEMANA · 7 columnas full-width (L→D) · cada una = header + <PostsList> (reusa el panel
// tal cual · su scroll + empty "Sin posts"). Flechas semana-a-semana · al cruzar mes pide el mes
// nuevo vía setMonth (mismo useCalendarList · cero backend). Mes y sus flechas NO se tocan.
export function WeekView({ anchorDay, month, setMonth, grouped }: WeekViewProps) {
  const [start, setStart] = useState<Date>(() => startOfWeek(anchorDay));
  const days = Array.from({ length: 7 }, (_, i) => addDays(start, i));
  const shift = (delta: number) => {
    const ns = addDays(start, delta * 7);
    setStart(ns);
    const nm = iso(ns).slice(0, 7);
    if (nm !== month) setMonth(nm);  // la nueva semana cae en otro mes → pedir ese mes
  };
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-center gap-2">
        <Button size="icon" variant="outline" className="h-8 w-8 border-primary text-primary" onClick={() => shift(-1)} aria-label="Semana anterior"><ChevronLeft className="h-4 w-4" /></Button>
        <span className="text-sm font-medium tabular-nums">{iso(days[0])} — {iso(days[6])}</span>
        <Button size="icon" variant="outline" className="h-8 w-8 border-primary text-primary" onClick={() => shift(1)} aria-label="Semana siguiente"><ChevronRight className="h-4 w-4" /></Button>
      </div>
      <div className="grid grid-cols-7 gap-2">
        {days.map((dt, i) => {
          const dk = iso(dt);
          return (
            <div key={dk} className="space-y-1 min-w-0">
              <div className="text-center text-[11px] text-muted-foreground tabular-nums">{WD[i]} {dt.getUTCDate()}</div>
              <PostsList day={dk} posts={grouped.get(dk) ?? []} />
            </div>
          );
        })}
      </div>
    </div>
  );
}
