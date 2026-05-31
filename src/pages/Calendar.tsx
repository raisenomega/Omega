import { useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { useCalendarList, groupByDay } from "@/hooks/useCalendarData";
import { CalendarGrid } from "@/components/calendar/CalendarGrid";
import { PostsList } from "@/components/calendar/PostsList";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import { EmptyState } from "@/components/common/EmptyState";

const MONTH_LABELS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

function currentMonthKey(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function shiftMonth(month: string, delta: number): string {
  const [y, m] = month.split("-").map(Number);
  const d = new Date(Date.UTC(y, m - 1 + delta, 1));
  return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}`;
}

export default function Calendar() {
  const [month, setMonth] = useState<string>(currentMonthKey);
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  useTrackOnMount("feature_open", { feature: "calendar" });
  const { activeBusinessId, isReady } = useActiveBusiness();

  const q = useCalendarList(month, "all");
  const grouped = useMemo(
    () => groupByDay((q.data?.items ?? []).filter((p) => p.client_id === activeBusinessId)),
    [q.data, activeBusinessId],
  );
  const dayPosts = selectedDay ? (grouped.get(selectedDay) ?? []) : [];
  const [y, m] = month.split("-").map(Number);

  if (!isReady) return null;
  if (!activeBusinessId) return <EmptyState feature="Calendario" />;

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-display font-bold tracking-tight">Calendario</h1>
        <p className="text-sm text-muted-foreground">Posts programados · click en un día para ver detalles.</p>
      </header>

      <div className="flex items-center gap-2">
        <Button size="icon" variant="outline" className="h-8 w-8" onClick={() => setMonth(shiftMonth(month, -1))} aria-label="Mes anterior"><ChevronLeft className="h-4 w-4" /></Button>
        <h2 className="text-lg font-medium flex-1 text-center tabular-nums">{MONTH_LABELS[m - 1]} {y}</h2>
        <Button size="icon" variant="outline" className="h-8 w-8" onClick={() => setMonth(shiftMonth(month, 1))} aria-label="Mes siguiente"><ChevronRight className="h-4 w-4" /></Button>
      </div>

      {q.isError ? (
        <Card><CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <AlertCircle className="h-10 w-10 text-destructive" />
          <p className="text-sm font-medium">No se pudo cargar el calendario</p>
          <Button size="sm" variant="outline" onClick={() => q.refetch()}>Reintentar</Button>
        </CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            {q.isLoading ? (
              <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
            ) : (
              <CalendarGrid month={month} selectedDay={selectedDay} grouped={grouped} onSelectDay={setSelectedDay} />
            )}
          </div>
          <div className="md:col-span-1">
            <PostsList day={selectedDay} posts={dayPosts} />
          </div>
        </div>
      )}
    </div>
  );
}
