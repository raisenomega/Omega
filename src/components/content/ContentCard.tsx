import { useState } from "react";
import { Check, X } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PLATFORM_COLORS, PLATFORM_LABELS, type Platform } from "@/lib/onboarding-constants";
import type { ContentItem } from "@/hooks/useContentActions";
import { useSaveContent } from "@/hooks/useContentActions";

interface ContentCardProps { item: ContentItem }

function formatDate(iso: string): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("es", { day: "2-digit", month: "short" });
}

export function ContentCard({ item }: ContentCardProps) {
  const [expanded, setExpanded] = useState(false);
  const save = useSaveContent();
  const platform = item.platform as Platform | null;
  const dotColor = platform && platform in PLATFORM_COLORS ? PLATFORM_COLORS[platform] : "#9CA3AF";
  const platformLabel = platform && platform in PLATFORM_LABELS ? PLATFORM_LABELS[platform] : "—";

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardContent className="p-3 space-y-2">
        <div className="flex items-center gap-2 text-xs">
          <span className="h-2.5 w-2.5 rounded-full shrink-0" style={{ background: dotColor }} aria-label={platformLabel} />
          <span className="font-medium">{platformLabel}</span>
          <Badge variant="secondary" className="h-5 px-1.5 text-[10px] capitalize">{item.content_type}</Badge>
          <span className="text-muted-foreground ml-auto">{formatDate(item.created_at)}</span>
        </div>
        <p
          className={`text-sm whitespace-pre-wrap cursor-pointer ${expanded ? "" : "line-clamp-3"}`}
          onClick={() => setExpanded((v) => !v)}
        >
          {item.content || "(sin contenido)"}
        </p>
        {item.model && <p className="text-[10px] text-muted-foreground">Modelo: {item.model}</p>}
        <div className="flex gap-2 pt-1">
          <Button
            size="sm"
            variant={item.is_saved ? "default" : "outline"}
            className={`gap-1 h-8 flex-1 ${item.is_saved ? "bg-emerald-600 hover:bg-emerald-700" : ""}`}
            disabled={save.isPending}
            onClick={() => save.mutate({ id: item.id, is_saved: !item.is_saved })}
          >
            <Check className="h-3.5 w-3.5" />
            {item.is_saved ? "Guardado" : "Guardar"}
          </Button>
          {item.is_saved && (
            <Button
              size="sm"
              variant="ghost"
              className="gap-1 h-8"
              disabled={save.isPending}
              onClick={() => save.mutate({ id: item.id, is_saved: false })}
            >
              <X className="h-3.5 w-3.5" />Descartar
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
