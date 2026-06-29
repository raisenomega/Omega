import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Lightbulb } from "lucide-react";
import { StrategyIdeaBoxes } from "@/components/strategies/StrategyIdeaBoxes";
import type { Strategy } from "@/hooks/useStrategies";

function fmtDate(iso: string): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" });
}

export function StrategyDetailModal({ strategy, onClose }: { strategy: Strategy | null; onClose: () => void }) {
  if (!strategy) return null;
  const c = strategy.contenido || {};
  const pilares = Array.isArray(c.pilares) ? c.pilares : [];
  const ideas = Array.isArray(c.posts_sugeridos) ? c.posts_sugeridos : [];

  return (
    <Dialog open={!!strategy} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle className="text-base">{strategy.titulo}</DialogTitle>
          <DialogDescription className="text-[11px]">
            {(strategy.tipo || "estrategia")} · {fmtDate(strategy.created_at)}
          </DialogDescription>
        </DialogHeader>

        {c.resumen && (
          <div className="space-y-1">
            <p className="text-[11px] text-muted-foreground">El enfoque general de esta estrategia.</p>
            <p className="text-sm whitespace-pre-wrap">{c.resumen}</p>
          </div>
        )}

        {pilares.length > 0 && (
          <div className="space-y-1.5">
            <p className="text-[11px] text-muted-foreground">Los ejes de contenido sobre los que construir.</p>
            <div className="flex flex-wrap gap-1">
              {pilares.map((p, i) => <Badge key={`${p}-${i}`} variant="secondary" className="text-[10px]">{p}</Badge>)}
            </div>
          </div>
        )}

        {ideas.length > 0 && (
          <div className="space-y-1.5 border-t border-border/20 pt-3 max-h-72 overflow-y-auto">
            <p className="text-xs font-medium flex items-center gap-1">
              <Lightbulb className="h-3.5 w-3.5" /> Ideas de posts
            </p>
            <p className="text-[11px] text-muted-foreground">
              Sugerencias de posts por red social — aún no son posts reales, son puntos de partida.
              Usá la flecha de una red para llevar solo esa idea a Content Lab.
            </p>
            <StrategyIdeaBoxes posts={ideas} />
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
