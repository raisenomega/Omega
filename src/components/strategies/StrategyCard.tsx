import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Strategy } from "@/hooks/useStrategies";
import { StrategyCardActions } from "@/components/strategies/StrategyCardActions";
import { StrategyDetailModal } from "@/components/strategies/StrategyDetailModal";

type Variant = "active" | "used" | "archived";

function fmtDate(iso: string): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("es", { day: "2-digit", month: "short" });
}

export function StrategyCard({ strategy, variant = "active" }: { strategy: Strategy; variant?: Variant }) {
  const c = strategy.contenido || {};
  const [open, setOpen] = useState(false);
  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardContent className="p-3 space-y-2">
        <div className="space-y-2 cursor-pointer" onClick={() => setOpen(true)}>
          <div className="flex items-center justify-between gap-2 text-xs">
            <span className="font-medium line-clamp-1">{strategy.titulo}</span>
            <span className="text-muted-foreground shrink-0">{fmtDate(strategy.created_at)}</span>
          </div>
          {variant === "used" && (
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-[10px]">Usada</Badge>
              {strategy.used_at && <span className="text-[10px] text-muted-foreground">{fmtDate(strategy.used_at)}</span>}
            </div>
          )}
          {c.resumen && <p className="text-sm text-muted-foreground line-clamp-3">{c.resumen}</p>}
          {Array.isArray(c.pilares) && c.pilares.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {c.pilares.slice(0, 4).map((p, i) => (
                <Badge key={`${p}-${i}`} variant="secondary" className="text-[10px]">{p}</Badge>
              ))}
            </div>
          )}
        </div>
        {/* Archivadas = solo lectura. Activas = todas las acciones. Usadas = solo "Usar" (re-usar). */}
        {variant !== "archived" && <StrategyCardActions strategy={strategy} variant={variant} />}
      </CardContent>
      <StrategyDetailModal strategy={open ? strategy : null} onClose={() => setOpen(false)} />
    </Card>
  );
}
