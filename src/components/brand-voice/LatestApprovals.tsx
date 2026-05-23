import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { CorpusEntry } from "@/hooks/useBrandVoiceSummary";

interface Props {
  items: CorpusEntry[];
}

function formatDate(iso: string): string {
  if (!iso) return "";
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? ""
    : d.toLocaleDateString("es", { day: "numeric", month: "short" });
}

export function LatestApprovals({ items }: Props) {
  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-base font-display">
          Últimas aprobaciones
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground font-body">
            Aún no has aprobado posts. Cada aprobación en Content Lab alimenta esta voz.
          </p>
        ) : (
          items.map((it, idx) => (
            <div
              key={`${it.created_at}-${idx}`}
              className="rounded-md border border-border/40 bg-background/50 p-3"
            >
              <p className="text-sm font-body line-clamp-2">{it.text}</p>
              <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                {it.platform && (
                  <Badge variant="secondary" className="capitalize">
                    {it.platform}
                  </Badge>
                )}
                <span>{formatDate(it.created_at)}</span>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
