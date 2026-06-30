import { useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PLATFORM_LABELS } from "@/lib/onboarding-constants";
import { useRecordStrategyUse } from "@/hooks/useRecordStrategyUse";

// Estrategias · REDISEÑO Fase 0 "la idea es la unidad" · agrupa visualmente por red (encabezado)
// pero cada IDEA tiene su PROPIA flecha → lleva SOLO esa idea a Content Lab (no el join de la red).
// mark_used:FALSE → la flecha NO consume la estrategia (sigue en Activas con sus demás ideas · el
// estado por-idea llega en la Fase A). NORMALIZACIÓN TOLERANTE: la plataforma es texto libre del LLM.
interface IdeaPost { plataforma?: string; idea?: string }
interface Box { key: string; label: string; platform: string | null; ideas: string[] }

// raw → red canónica del form (PLATFORMS) si matchea; null si es desconocida (red rara).
function normalize(raw: string): string | null {
  const s = raw.toLowerCase();
  if (s.includes("insta") || s === "ig") return "instagram";
  if (s.includes("tik")) return "tiktok";
  if (s.includes("face") || s === "fb") return "facebook";
  if (s.includes("linkedin")) return "linkedin";
  if (s.includes("twitter") || s === "x") return "twitter";
  if (s.includes("youtube") || s.includes("yt")) return "youtube";
  return null;
}

// Agrupa por red normalizada (variantes "IG"/"insta"/"Instagram" → un solo cuadro). Una red
// desconocida conserva su nombre crudo y su idea (nunca se pierde ni rompe).
function buildBoxes(posts: IdeaPost[]): Box[] {
  const map = new Map<string, Box>();
  for (const p of posts) {
    const raw = (p?.plataforma ?? "").trim();
    const norm = normalize(raw);
    const key = norm ?? (raw.toLowerCase() || "otra");
    const label = norm ? PLATFORM_LABELS[norm as keyof typeof PLATFORM_LABELS] : (raw || "Otra red");
    const idea = (p?.idea ?? "").trim();
    if (!map.has(key)) map.set(key, { key, label, platform: norm, ideas: [] });
    if (idea) map.get(key)!.ideas.push(idea);
  }
  return [...map.values()];
}

export function StrategyIdeaBoxes({ strategyId, posts }: { strategyId: string; posts: IdeaPost[] }) {
  const navigate = useNavigate();
  const recordUse = useRecordStrategyUse();
  const boxes = buildBoxes(Array.isArray(posts) ? posts : []);
  if (boxes.length === 0) return null;

  // Fase 0 · manda SOLO esta idea (no el join de la red) y NO consume la estrategia (mark_used:false
  // · sigue en Activas). best-effort: si /use falla NO bloquea la navegacion al generador.
  const go = (box: Box, idea: string) => {
    try { recordUse.mutate({ id: strategyId, platform: box.platform ?? box.label, brief: idea, mark_used: false }); } catch { /* best-effort */ }
    navigate("/content-lab", { state: { brief: idea, ...(box.platform ? { platform: box.platform } : {}) } });
  };

  return (
    <div className="grid gap-2 sm:grid-cols-2">
      {boxes.map((box) => (
        <div key={box.key} className="rounded-lg border border-border/40 bg-card/50 p-3 space-y-2">
          <span className="text-xs font-semibold">{box.label}</span>
          {box.ideas.length > 0 ? (
            box.ideas.map((idea, i) => (
              <div key={i} className="flex items-start justify-between gap-2">
                <p className="text-sm flex-1">{idea}</p>
                <Button
                  size="sm" variant="ghost"
                  className="h-7 px-2 gap-1 text-primary hover:text-primary shrink-0"
                  aria-label={`Usar en Content Lab: ${idea}`}
                  onClick={() => go(box, idea)}
                >
                  Usar <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">(idea sin texto)</p>
          )}
        </div>
      ))}
    </div>
  );
}
