import { cn } from "@/lib/utils";
import type { CalendarPost, DbStatus } from "@/hooks/useCalendarData";

interface CalendarGridProps {
  month: string;
  selectedDay: string | null;
  grouped: Map<string, CalendarPost[]>;
  onSelectDay: (day: string) => void;
}

const WEEKDAYS = ["L", "M", "X", "J", "V", "S", "D"];
const STATUS_COLOR: Record<DbStatus, string> = {
  pending: "bg-blue-500",
  publishing: "bg-amber-500",
  published: "bg-emerald-500",
  published_manual: "bg-teal-500",
  failed: "bg-rose-500",
  cancelled: "bg-muted-foreground/40",
};

function buildMonthCells(month: string): { dateKey: string | null; day: number | null }[] {
  const [y, m] = month.split("-").map(Number);
  const first = new Date(Date.UTC(y, m - 1, 1));
  const daysInMonth = new Date(Date.UTC(y, m, 0)).getUTCDate();
  const startOffset = (first.getUTCDay() + 6) % 7;  // Lun=0
  const cells: { dateKey: string | null; day: number | null }[] = [];
  for (let i = 0; i < startOffset; i++) cells.push({ dateKey: null, day: null });
  for (let d = 1; d <= daysInMonth; d++) {
    const dk = `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    cells.push({ dateKey: dk, day: d });
  }
  while (cells.length % 7 !== 0) cells.push({ dateKey: null, day: null });
  return cells;
}

export function CalendarGrid({ month, selectedDay, grouped, onSelectDay }: CalendarGridProps) {
  const today = new Date().toISOString().slice(0, 10);
  const cells = buildMonthCells(month);
  return (
    <div className="space-y-1">
      <div className="grid grid-cols-7 gap-1 text-[10px] text-muted-foreground text-center">
        {WEEKDAYS.map((d) => <div key={d} className="py-1">{d}</div>)}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {cells.map((c, i) => {
          if (!c.dateKey) return <div key={i} className="h-16" />;
          const posts = grouped.get(c.dateKey) ?? [];
          const isToday = c.dateKey === today;
          const isSelected = c.dateKey === selectedDay;
          return (
            <button
              key={c.dateKey}
              type="button"
              onClick={() => onSelectDay(c.dateKey!)}
              className={cn(
                "h-16 rounded border border-border/40 p-1 flex flex-col items-center justify-start text-xs hover:bg-muted/50 transition",
                isToday && "ring-1 ring-primary",
                isSelected && "bg-primary/10 border-primary",
              )}
            >
              <span className={cn("font-medium", isToday && "text-primary")}>{c.day}</span>
              <div className="flex gap-0.5 mt-auto flex-wrap justify-center">
                {posts.slice(0, 3).map((p) => (
                  <span key={p.id} className={cn("h-1.5 w-1.5 rounded-full", STATUS_COLOR[p.status])} aria-label={p.status} />
                ))}
                {posts.length > 3 && <span className="text-[8px] text-muted-foreground">+{posts.length - 3}</span>}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
