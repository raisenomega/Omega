import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PLATFORM_LABELS } from "@/lib/onboarding-constants";
import type { Strategy } from "@/hooks/useStrategies";
import { StrategyCardActions } from "@/components/strategies/StrategyCardActions";
import { StrategyDetailModal } from "@/components/strategies/StrategyDetailModal";

type Variant = "active" | "used" | "archived";

function fmtDate(iso: string): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("es", { day: "2-digit", month: "short" });
}

export function StrategyCard({ strategy, variant = "active", usedCount = 0 }: { strategy: Strategy; variant?: Variant; usedCount?: number }) {
  const c = strategy.contenido || {};
  const [open, setOpen] = useState(false);
  const lu = strategy.last_used;
  // Fase B.3 · contador "X de N ideas usadas" en Activas (N = total de ideas · X = usadas de ESTA estrategia).
  const totalIdeas = Array.isArray(c.posts_sugeridos) ? c.posts_sugeridos.length : 0;
  // CAPA 1 · en Usadas pintamos lo que se USO de verdad (last_used.brief). Fallback al resumen si
  // last_used es null (estrategias marcadas usadas antes del arco · honesto: no se registro el detalle).
  const showUsed = variant === "used" && !!lu?.brief;
  const usedLabel = !lu?.platform || lu.platform === "completa"
    ? "Usaste la estrategia completa:"
    : `Usaste (${PLATFORM_LABELS[lu.platform as keyof typeof PLATFORM_LABELS] ?? lu.platform}):`;
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
          {showUsed ? (
            <div className="space-y-0.5">
              <p className="text-[10px] font-medium text-muted-foreground">{usedLabel}</p>
              <p className="text-sm line-clamp-3">{lu!.brief}</p>
            </div>
          ) : (
            c.resumen && <p className="text-sm text-muted-foreground line-clamp-3">{c.resumen}</p>
          )}
          {/* En Usadas con detalle (showUsed) mostramos SOLO el cuadro de lo usado · sin pilares.
              Usada sin last_used (fallback CAPA 1) y activas/archivadas → conservan los pilares. */}
          {!showUsed && Array.isArray(c.pilares) && c.pilares.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {c.pilares.slice(0, 4).map((p, i) => (
                <Badge key={`${p}-${i}`} variant="secondary" className="text-[10px]">{p}</Badge>
              ))}
            </div>
          )}
          {variant === "active" && totalIdeas > 0 && (
            <p className="text-[10px] text-muted-foreground">{usedCount} de {totalIdeas} ideas usadas</p>
          )}
        </div>
        {/* Archivadas = solo lectura. Activas = todas las acciones. Usadas = solo "Usar" (re-usar). */}
        {variant !== "archived" && <StrategyCardActions strategy={strategy} variant={variant} />}
      </CardContent>
      <StrategyDetailModal strategy={open ? strategy : null} onClose={() => setOpen(false)} />
    </Card>
  );
}
