import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock } from "lucide-react";
import type { SentinelComponentMeta } from "@/lib/sentinel_components_registry";

// Card de catálogo (metadata) para "Componentes monitoreados" · qué vigila + frecuencia.
// onClickDetail queda preparado para Sub-bloque B (modal universal) · en A no se cablea (sin afordancia falsa).
export function SentinelComponentCard({ meta, onClickDetail }: { meta: SentinelComponentMeta; onClickDetail?: () => void }) {
  const clickable = !!onClickDetail;
  return (
    <Card
      onClick={onClickDetail}
      className={clickable ? "cursor-pointer transition-colors hover:bg-muted/40" : ""}
    >
      <CardContent className="space-y-1 p-3">
        <div className="flex items-center justify-between gap-2">
          <span className="text-sm font-medium">{meta.name}</span>
          <Badge variant="outline" className="border-border/40 text-[10px] text-muted-foreground">
            <Clock className="mr-1 h-3 w-3" />{meta.frequency}
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground">{meta.whatItChecks}</p>
      </CardContent>
    </Card>
  );
}
