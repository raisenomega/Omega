import { X, Check, Zap } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { PLATFORM_COLORS, PLATFORM_LABELS, type Platform } from "@/lib/onboarding-constants";
import type { CalendarPost, DbStatus } from "@/hooks/useCalendarData";
import { useUpdatePostStatus } from "@/hooks/useCalendarData";

interface PostsListProps {
  day: string | null;
  posts: CalendarPost[];
}

const STATUS_LABELS: Record<DbStatus, string> = {
  pending: "Programado", publishing: "Publicando", published: "Publicado",
  published_manual: "Publicado (manual)", failed: "Falló", cancelled: "Cancelado",
};
const STATUS_VARIANT: Record<DbStatus, "default" | "secondary" | "destructive" | "outline"> = {
  pending: "secondary", publishing: "default", published: "default",
  published_manual: "default", failed: "destructive", cancelled: "outline",
};

function formatTime(iso: string): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleTimeString("es", { hour: "2-digit", minute: "2-digit" });
}

export function PostsList({ day, posts }: PostsListProps) {
  const update = useUpdatePostStatus();
  if (!day) {
    return <p className="text-xs text-muted-foreground text-center py-6">Selecciona un día del calendario</p>;
  }
  if (posts.length === 0) {
    return <p className="text-xs text-muted-foreground text-center py-6">Sin posts programados</p>;
  }
  return (
    <div className="space-y-2 max-h-[480px] overflow-y-auto pr-1">
      {posts.map((p) => {
        const platform = p.platform as Platform | null;
        const dot = platform && platform in PLATFORM_COLORS ? PLATFORM_COLORS[platform] : "#9CA3AF";
        const platformLabel = platform && platform in PLATFORM_LABELS ? PLATFORM_LABELS[platform] : "—";
        return (
          <Card key={p.id} className="border-border/50">
            <CardContent className="p-2.5 space-y-1.5">
              <div className="flex items-center gap-2 text-xs">
                <span className="h-2.5 w-2.5 rounded-full shrink-0" style={{ background: dot }} aria-label={platformLabel} />
                <span className="font-medium tabular-nums">{formatTime(p.scheduled_for)}</span>
                <span className="text-muted-foreground">{platformLabel}</span>
                <Badge variant={STATUS_VARIANT[p.status]} className="h-5 px-1.5 text-[10px] ml-auto">{STATUS_LABELS[p.status]}</Badge>
              </div>
              <p className="text-xs text-muted-foreground line-clamp-2">{p.content_preview || "(sin contenido)"}</p>
              {p.status === "pending" && (
                <div className="flex items-center gap-1">
                  <Button size="sm" variant="default" className="h-7 flex-1 gap-1 text-[11px]" disabled={update.isPending}
                    onClick={() => update.mutate({ id: p.id, status: "published_manual" })}>
                    <Check className="h-3.5 w-3.5" />Publicar Manual
                  </Button>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <span tabIndex={0} className="flex-1">
                        <Button size="sm" variant="secondary" className="h-7 w-full gap-1 text-[11px]" disabled>
                          <Zap className="h-3.5 w-3.5" />Publicar Auto
                        </Button>
                      </span>
                    </TooltipTrigger>
                    <TooltipContent>Requiere cuenta social conectada · disponible con MCP</TooltipContent>
                  </Tooltip>
                  <Button size="sm" variant="ghost" className="h-7 gap-1" disabled={update.isPending}
                    onClick={() => update.mutate({ id: p.id, status: "cancelled" })} aria-label="Cancelar">
                    <X className="h-3.5 w-3.5" />
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
