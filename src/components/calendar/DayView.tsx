import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PostCard } from "./PostCard";
import { addDays } from "@/lib/calendar-dates";
import type { CalendarPost } from "@/hooks/useCalendarData";

interface DayViewProps {
  day: string;            // YYYY-MM-DD
  posts: CalendarPost[];
  onChangeDay: (day: string) => void;   // flechas día ±1 (el padre cruza mes si hace falta)
}

function dayLabel(day: string): string {
  const [y, m, d] = day.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString("es", {
    weekday: "long", day: "numeric", month: "long", timeZone: "UTC",
  });
}

// Vista DÍA · los posts del día en tarjetas desplegadas (PostCard variant spacious · grid 1-3
// columnas) · flechas ‹ › día anterior/siguiente. Se vuelve al Mes con el chip de la barra
// (sin botón "Volver"). Reusa PostCard + el dato ya agrupado · cero backend.
export function DayView({ day, posts, onChangeDay }: DayViewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Button size="icon" variant="outline" className="h-8 w-8 border-primary text-primary" onClick={() => onChangeDay(addDays(day, -1))} aria-label="Día anterior"><ChevronLeft className="h-4 w-4" /></Button>
        <h2 className="text-lg font-medium flex-1 text-center capitalize tabular-nums">{dayLabel(day)}</h2>
        <Button size="icon" variant="outline" className="h-8 w-8 border-primary text-primary" onClick={() => onChangeDay(addDays(day, 1))} aria-label="Día siguiente"><ChevronRight className="h-4 w-4" /></Button>
      </div>
      {posts.length === 0 ? (
        <p className="text-sm text-muted-foreground text-center py-12">Sin posts ese día</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {posts.map((p) => <PostCard key={p.id} post={p} variant="spacious" />)}
        </div>
      )}
    </div>
  );
}
