import { useMemo, useState } from "react";
import { Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { useCalendarList, groupByDay } from "@/hooks/useCalendarData";
import { MonthView } from "@/components/calendar/MonthView";
import { WeekView } from "@/components/calendar/WeekView";
import { DayView } from "@/components/calendar/DayView";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import { EmptyState } from "@/components/common/EmptyState";
import { RexCalendarBar } from "@/components/calendar/RexCalendarBar";
import { FilterChips, type ChipItem } from "@/components/ui/FilterChips";

type ViewMode = "month" | "week" | "day";
const VIEW_CHIPS: ChipItem[] = [
  { id: "month", label: "Mes" },
  { id: "week", label: "Semana" },
  { id: "day", label: "Día" },
];

function currentMonthKey(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

export default function Calendar() {
  const [month, setMonth] = useState<string>(currentMonthKey);
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [view, setView] = useState<ViewMode>("month");
  useTrackOnMount("feature_open", { feature: "calendar" });
  const { activeBusinessId, isReady } = useActiveBusiness();

  const q = useCalendarList(month, "all");
  const grouped = useMemo(
    () => groupByDay((q.data?.items ?? []).filter((p) => p.client_id === activeBusinessId)),
    [q.data, activeBusinessId],
  );
  const today = new Date().toISOString().slice(0, 10);
  const viewDay = selectedDay ?? today;              // entrar al chip Día sin elegir → hoy
  const openDay = (dk: string) => { setSelectedDay(dk); setView("day"); };

  if (!isReady) return null;
  if (!activeBusinessId) return <EmptyState feature="Calendario" />;

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-display font-bold tracking-tight">Calendario</h1>
          <div className="sm:mx-auto">
            <FilterChips items={VIEW_CHIPS} active={view} onSelect={(id) => setView(id as ViewMode)} />
          </div>
          <RexCalendarBar clientId={activeBusinessId} />
        </div>
        <p className="text-sm text-muted-foreground">Posts programados · click en un día para ver detalles.</p>
      </header>

      {q.isError ? (
        <Card><CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <p className="text-sm font-medium">No se pudo cargar el calendario</p>
          <Button size="sm" variant="outline" onClick={() => q.refetch()}>Reintentar</Button>
        </CardContent></Card>
      ) : q.isLoading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
      ) : view === "day" ? (
        <DayView day={viewDay} posts={grouped.get(viewDay) ?? []} onBack={() => setView("month")} />
      ) : view === "week" ? (
        <WeekView anchorDay={viewDay} month={month} setMonth={setMonth} grouped={grouped} />
      ) : (
        <MonthView month={month} setMonth={setMonth} selectedDay={selectedDay} grouped={grouped} onSelectDay={openDay} />
      )}
    </div>
  );
}
