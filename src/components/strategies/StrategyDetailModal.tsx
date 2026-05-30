import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Lightbulb } from "lucide-react";
import type { Strategy } from "@/hooks/useStrategies";

function fmtDate(iso: string): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" });
}

// posts_sugeridos: forma esperada {plataforma, idea} pero es JSON de LLM (parse_strategy NO valida
// su forma) → render defensivo: lo que haya, fallback por campo. SIN CTA por idea (estrategia != post
// · evita la trampa de Agendar) · el "Usar" de la card sigue siendo el único camino a Content Lab.
function ideaLine(p: { plataforma?: string; idea?: string }): { red: string; idea: string } {
  return { red: (p?.plataforma ?? "").trim(), idea: (p?.idea ?? "").trim() };
}

export function StrategyDetailModal({ strategy, onClose }: { strategy: Strategy | null; onClose: () => void }) {
  if (!strategy) return null;
  const c = strategy.contenido || {};
  const pilares = Array.isArray(c.pilares) ? c.pilares : [];
  const ideas = Array.isArray(c.posts_sugeridos) ? c.posts_sugeridos : [];

  return (
    <Dialog open={!!strategy} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-base">{strategy.titulo}</DialogTitle>
          <DialogDescription className="text-[11px]">
            {(strategy.tipo || "estrategia")} · {fmtDate(strategy.created_at)}
          </DialogDescription>
        </DialogHeader>

        {c.resumen && <p className="text-sm whitespace-pre-wrap">{c.resumen}</p>}

        {pilares.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {pilares.map((p, i) => <Badge key={`${p}-${i}`} variant="secondary" className="text-[10px]">{p}</Badge>)}
          </div>
        )}

        {ideas.length > 0 && (
          <div className="space-y-1.5 border-t border-border/20 pt-3 max-h-60 overflow-y-auto">
            <p className="text-xs font-medium text-muted-foreground flex items-center gap-1">
              <Lightbulb className="h-3.5 w-3.5" /> Ideas de posts (sugerencias · aún no generadas)
            </p>
            {ideas.map((p, i) => {
              const { red, idea } = ideaLine(p);
              return (
                <p key={i} className="text-sm">
                  {red && <span className="font-medium">{red}: </span>}{idea || "(idea sin texto)"}
                </p>
              );
            })}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
