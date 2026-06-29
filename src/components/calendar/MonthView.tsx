import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CalendarGrid } from "./CalendarGrid";
import type { CalendarPost } from "@/hooks/useCalendarData";

const MONTH_LABELS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

function shiftMonth(month: string, delta: number): string {
  const [y, m] = month.split("-").map(Number);
  const d = new Date(Date.UTC(y, m - 1 + delta, 1));
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
}

interface MonthViewProps {
  month: string;
  setMonth: (m: string) => void;
  selectedDay: string | null;
  grouped: Map<string, CalendarPost[]>;
  onSelectDay: (day: string) => void;
}

// Vista MES · grid full-width (sin panel lateral · ocupa todo el ancho) + navegación de mes.
// Click en un día → el padre abre la vista Día (onSelectDay). CalendarGrid intacto.
export function MonthView({ month, setMonth, selectedDay, grouped, onSelectDay }: MonthViewProps) {
  const [y, m] = month.split("-").map(Number);
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button size="icon" variant="outline" className="h-8 w-8 border-primary text-primary" onClick={() => setMonth(shiftMonth(month, -1))} aria-label="Mes anterior"><ChevronLeft className="h-4 w-4" /></Button>
        <h2 className="text-lg font-medium flex-1 text-center tabular-nums">{MONTH_LABELS[m - 1]} {y}</h2>
        <Button size="icon" variant="outline" className="h-8 w-8 border-primary text-primary" onClick={() => setMonth(shiftMonth(month, 1))} aria-label="Mes siguiente"><ChevronRight className="h-4 w-4" /></Button>
      </div>
      <CalendarGrid month={month} selectedDay={selectedDay} grouped={grouped} onSelectDay={onSelectDay} />
    </div>
  );
}
