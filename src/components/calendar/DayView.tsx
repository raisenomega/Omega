import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PostCard } from "./PostCard";
import type { CalendarPost } from "@/hooks/useCalendarData";

interface DayViewProps {
  day: string;            // YYYY-MM-DD
  posts: CalendarPost[];
  onBack: () => void;
}

function dayLabel(day: string): string {
  const [y, m, d] = day.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString("es", {
    weekday: "long", day: "numeric", month: "long", timeZone: "UTC",
  });
}

// Vista DÍA · los posts del día en tarjetas desplegadas (PostCard variant spacious · grid 1-3
// columnas, NO panel angosto) + volver al mes. Reusa PostCard + el dato ya agrupado · cero backend.
export function DayView({ day, posts, onBack }: DayViewProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Button size="sm" variant="outline" className="gap-1" onClick={onBack}>
          <ArrowLeft className="h-4 w-4" />Volver al mes
        </Button>
        <h2 className="text-lg font-medium capitalize tabular-nums">{dayLabel(day)}</h2>
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
