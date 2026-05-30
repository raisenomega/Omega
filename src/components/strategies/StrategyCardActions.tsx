import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sparkles, MessageCircle, Archive } from "lucide-react";
import { useARIA } from "@/contexts/ARIAContext";
import { useSetStrategyStatus, type Strategy } from "@/hooks/useStrategies";

// Las 3 acciones de Fase 1 · HONESTAS (ninguna promete más de lo que hace):
// Usar→Content Lab pre-llenado (real) · Pedir ajuste→chat ARIA (real) · Archivar→PATCH estado (real).
// "Agendar" se quitó (DEBT-096 F1): una estrategia no es un post (posts_sugeridos = ideas sin
// content_id). El agendado real va por Usar→Content Lab→ScheduleModalV2. Botón propio = Fase 1.5/2.
function briefFrom(s: Strategy): string {
  const c = s.contenido || {};
  const pilares = Array.isArray(c.pilares) ? c.pilares.join(", ") : "";
  return [s.titulo, c.resumen, pilares].filter(Boolean).join(" · ");
}

export function StrategyCardActions({ strategy }: { strategy: Strategy }) {
  const navigate = useNavigate();
  const { openARIAWith } = useARIA();
  const setStatus = useSetStrategyStatus();

  return (
    <div className="flex flex-wrap gap-1.5 pt-1">
      <Button
        size="sm" className="gap-1 h-8 flex-1"
        onClick={() => {
          setStatus.mutate({ id: strategy.id, estado: "used" });
          navigate("/content-lab", { state: { brief: briefFrom(strategy) } });
        }}
      >
        <Sparkles className="h-3.5 w-3.5" /> Usar
      </Button>
      <Button
        size="sm" variant="ghost" className="gap-1 h-8"
        onClick={() => openARIAWith(`Ajustá esta estrategia: ${strategy.titulo}`)}
      >
        <MessageCircle className="h-3.5 w-3.5" /> Ajuste
      </Button>
      <Button
        size="sm" variant="ghost" className="gap-1 h-8 text-muted-foreground hover:text-destructive"
        disabled={setStatus.isPending}
        onClick={() => setStatus.mutate({ id: strategy.id, estado: "archived" })}
      >
        <Archive className="h-3.5 w-3.5" /> Archivar
      </Button>
    </div>
  );
}
