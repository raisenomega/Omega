import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sparkles, MessageCircle, Archive } from "lucide-react";
import { useARIA } from "@/contexts/ARIAContext";
import { useSetStrategyStatus, type Strategy } from "@/hooks/useStrategies";
import { useRecordStrategyUse } from "@/hooks/useRecordStrategyUse";
import { PLATFORMS } from "@/lib/onboarding-constants";

// CAPA 1 · "Usar"/"Re-usar" registran el uso (POST /use · mark_used=true → la estrategia va a
// Usadas) + navegan a Content Lab. best-effort: /use NUNCA bloquea la navegacion. Ajuste→chat ARIA.
// Archivar→PATCH estado. "Re-usar" (variant used) reusa el last_used (el texto que se uso de verdad).
function briefFrom(s: Strategy): string {
  const c = s.contenido || {};
  const pilares = Array.isArray(c.pilares) ? c.pilares.join(", ") : "";
  return [s.titulo, c.resumen, pilares].filter(Boolean).join(" · ");
}

export function StrategyCardActions({ strategy, variant = "active" }: { strategy: Strategy; variant?: "active" | "used" }) {
  const navigate = useNavigate();
  const { openARIAWith } = useARIA();
  const setStatus = useSetStrategyStatus();
  const recordUse = useRecordStrategyUse();

  const go = (platform: string, brief: string) => {
    try { recordUse.mutate({ id: strategy.id, platform, brief, mark_used: true }); } catch { /* best-effort */ }
    const valid = (PLATFORMS as readonly string[]).includes(platform);  // "completa" → sin platform (default del form)
    navigate("/content-lab", { state: { brief, ...(valid ? { platform } : {}) } });
  };

  return (
    <div className="flex flex-wrap gap-1.5 pt-1">
      {variant === "used" ? (
        <Button
          size="sm" className="gap-1 h-8 flex-1"
          onClick={() => go(strategy.last_used?.platform || "completa", strategy.last_used?.brief || briefFrom(strategy))}
        >
          <Sparkles className="h-3.5 w-3.5" /> Re-usar
        </Button>
      ) : (
        <>
          <Button size="sm" className="gap-1 h-8 flex-1" onClick={() => go("completa", briefFrom(strategy))}>
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
        </>
      )}
    </div>
  );
}
