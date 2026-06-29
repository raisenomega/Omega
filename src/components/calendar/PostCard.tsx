import { X, ClipboardCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AutoPublishButton } from "./AutoPublishButton";
import { PLATFORM_COLORS, PLATFORM_LABELS, type Platform } from "@/lib/onboarding-constants";
import type { CalendarPost, DbStatus } from "@/hooks/useCalendarData";
import { useUpdatePostStatus } from "@/hooks/useCalendarData";

type CardVariant = "compact" | "spacious";

interface PostCardProps {
  post: CalendarPost;
  variant?: CardVariant;  // "compact" = look idéntico al panel lateral actual (default · cero cambio visual)
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

// Tarjeta de un post del calendario (hora + red + estado + preview + acciones si está pending).
// Extraída tal cual de PostsList (Commit 1 · refactor invisible) para reusarla en las vistas
// Semana y Día. variant="compact" reproduce el panel lateral actual byte-por-byte (cero cambio visual).
// Reusa los MISMOS hooks de acción (useUpdatePostStatus + AutoPublishButton) · cero lógica nueva.
export function PostCard({ post: p, variant = "compact" }: PostCardProps) {
  const update = useUpdatePostStatus();
  const platform = p.platform as Platform | null;
  const dot = platform && platform in PLATFORM_COLORS ? PLATFORM_COLORS[platform] : "#9CA3AF";
  const platformLabel = platform && platform in PLATFORM_LABELS ? PLATFORM_LABELS[platform] : "—";
  const pad = variant === "spacious" ? "p-3 space-y-2" : "p-2.5 space-y-1.5";
  return (
    <Card className="border-border/50">
      <CardContent className={pad}>
        <div className="flex items-center gap-2 text-xs">
          <span className="h-2.5 w-2.5 rounded-full shrink-0" style={{ background: dot }} aria-label={platformLabel} />
          <span className="font-medium tabular-nums">{formatTime(p.scheduled_for)}</span>
          <span className="text-muted-foreground">{platformLabel}</span>
          <Badge variant={STATUS_VARIANT[p.status]} className="h-5 px-1.5 text-[10px] ml-auto">{STATUS_LABELS[p.status]}</Badge>
        </div>
        <p className="text-xs text-muted-foreground line-clamp-2">{p.content_preview || "(sin contenido)"}</p>
        {p.status === "pending" && (
          <div className="flex items-center gap-1">
            {variant === "spacious" && (
              <Button size="sm" variant="default" className="h-7 flex-1 gap-1 text-[11px]" disabled={update.isPending}
                onClick={() => update.mutate({ id: p.id, status: "published_manual" })}>
                <ClipboardCheck className="h-3.5 w-3.5" />Marcar como publicado
              </Button>
            )}
            <span className="flex-1">
              <AutoPublishButton postId={p.id} />
            </span>
            <Button size="sm" variant="ghost" className="h-7 gap-1" disabled={update.isPending}
              onClick={() => update.mutate({ id: p.id, status: "cancelled" })} aria-label="Cancelar">
              <X className="h-3.5 w-3.5" />
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
