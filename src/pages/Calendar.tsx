import { useState } from "react";
import type { Post } from "@/types/post";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Loader2,
} from "lucide-react";
import {
  format,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  isSameMonth,
  isSameDay,
  addMonths,
  subMonths,
  startOfWeek,
  endOfWeek,
  isToday,
} from "date-fns";
import { es } from "date-fns/locale";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-muted-foreground",
  scheduled: "bg-primary",
  published: "bg-success",
  failed: "bg-destructive",
};

export default function CalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const { data: posts, isLoading } = useQuery<Post[]>({
    queryKey: ["posts"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("posts" as any)
        .select("*")
        .order("scheduled_at", { ascending: true });
      if (error) throw error;
      return data as unknown as Post[];
    },
  });

  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const calStart = startOfWeek(monthStart, { weekStartsOn: 1 });
  const calEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });
  const days = eachDayOfInterval({ start: calStart, end: calEnd });

  const getPostsForDay = (day: Date) =>
    (posts ?? []).filter((p) => {
      const postDate = p.scheduled_at
        ? new Date(p.scheduled_at)
        : new Date(p.created_at);
      return isSameDay(postDate, day);
    });

  const weekDays = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-display font-bold tracking-tight">Calendario</h1>
        <p className="text-muted-foreground font-body">Visualiza y programa tus publicaciones</p>
      </div>

      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between pb-4">
          <CardTitle className="font-display text-lg capitalize">
            {format(currentMonth, "MMMM yyyy", { locale: es })}
          </CardTitle>
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setCurrentMonth(new Date())}
            >
              Hoy
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : (
            <div className="grid grid-cols-7 gap-px bg-border rounded-lg overflow-hidden">
              {/* Header */}
              {weekDays.map((d) => (
                <div
                  key={d}
                  className="bg-secondary px-2 py-2 text-center text-xs font-medium text-muted-foreground"
                >
                  {d}
                </div>
              ))}

              {/* Days */}
              {days.map((day, i) => {
                const dayPosts = getPostsForDay(day);
                const inMonth = isSameMonth(day, currentMonth);
                const today = isToday(day);

                return (
                  <div
                    key={i}
                    className={`min-h-[80px] bg-card p-1.5 ${
                      !inMonth ? "opacity-30" : ""
                    } ${today ? "ring-1 ring-primary ring-inset" : ""}`}
                  >
                    <span
                      className={`text-xs font-medium ${
                        today
                          ? "flex h-5 w-5 items-center justify-center rounded-full gradient-primary text-primary-foreground"
                          : "text-muted-foreground"
                      }`}
                    >
                      {format(day, "d")}
                    </span>
                    <div className="mt-1 space-y-0.5">
                      {dayPosts.slice(0, 3).map((post) => (
                        <div
                          key={post.id}
                          className="flex items-center gap-1 rounded px-1 py-0.5 bg-secondary/50 cursor-pointer hover:bg-secondary"
                          title={post.title}
                        >
                          <div
                            className={`h-1.5 w-1.5 rounded-full shrink-0 ${
                              STATUS_COLORS[post.status] || "bg-muted-foreground"
                            }`}
                          />
                          <span className="text-[10px] truncate">{post.title}</span>
                        </div>
                      ))}
                      {dayPosts.length > 3 && (
                        <span className="text-[10px] text-muted-foreground px-1">
                          +{dayPosts.length - 3} más
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Legend */}
      <div className="flex gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full bg-muted-foreground" /> Borrador
        </span>
        <span className="flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full bg-primary" /> Programado
        </span>
        <span className="flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full bg-success" /> Publicado
        </span>
        <span className="flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full bg-destructive" /> Fallido
        </span>
      </div>
    </div>
  );
}
