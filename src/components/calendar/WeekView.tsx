import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { PostsList } from "./PostsList";
import { addDays, startOfWeek } from "@/lib/calendar-dates";
import type { CalendarPost } from "@/hooks/useCalendarData";

const WD_FULL = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

interface WeekViewProps {
  anchorDay: string;        // selectedDay ?? hoy (lo resuelve el padre)
  month: string;            // mes cargado (YYYY-MM)
  setMonth: (m: string) => void;
  grouped: Map<string, CalendarPost[]>;
  onOpenDay?: (day: string) => void;   // click en el header de columna → vista Día
}

// Vista SEMANA · 7 columnas full-width (Lun→Dom) · cada una = header (día completo · clickable
// → Día) + <PostsList> (reusa el panel · scroll + empty). Hoy sombreado. Flechas semana-a-semana
// · al cruzar mes pide el mes nuevo vía setMonth (mismo useCalendarList · cero backend).
export function WeekView({ anchorDay, month, setMonth, grouped, onOpenDay }: WeekViewProps) {
  const [start, setStart] = useState<string>(() => startOfWeek(anchorDay));
  const days = Array.from({ length: 7 }, (_, i) => addDays(start, i));
  const today = new Date().toISOString().slice(0, 10);
  const shift = (delta: number) => {
    const ns = addDays(start, delta * 7);
    setStart(ns);
    if (ns.slice(0, 7) !== month) setMonth(ns.slice(0, 7));  // nueva semana en otro mes → pedirlo
  };
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Button size="icon" variant="outline" className="h-8 w-8 border-primary text-primary" onClick={() => shift(-1)} aria-label="Semana anterior"><ChevronLeft className="h-4 w-4" /></Button>
        <span className="text-sm font-medium flex-1 text-center tabular-nums">{days[0]} — {days[6]}</span>
        <Button size="icon" variant="outline" className="h-8 w-8 border-primary text-primary" onClick={() => shift(1)} aria-label="Semana siguiente"><ChevronRight className="h-4 w-4" /></Button>
      </div>
      <div className="grid grid-cols-7 gap-2">
        {days.map((dk, i) => (
          <div key={dk} className={cn("space-y-1 min-w-0 rounded p-1", dk === today && "bg-primary/5")}>
            <button type="button" onClick={() => onOpenDay?.(dk)} className="w-full truncate text-center text-[11px] font-medium tabular-nums hover:text-primary">
              {WD_FULL[i]} {Number(dk.slice(8, 10))}
            </button>
            <PostsList day={dk} posts={grouped.get(dk) ?? []} />
          </div>
        ))}
      </div>
    </div>
  );
}
