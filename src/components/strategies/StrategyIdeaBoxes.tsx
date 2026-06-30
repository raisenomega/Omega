import { useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PLATFORM_LABELS } from "@/lib/onboarding-constants";
import { useRecordIdeaUse } from "@/hooks/useRecordIdeaUse";

// Estrategias · REDISEÑO "la idea es la unidad" · agrupa visualmente por red (encabezado) pero cada
// IDEA tiene su PROPIA flecha → lleva SOLO esa idea a Content Lab + la registra via /use-idea (Fase
// B.3 · idx = posicion en posts_sugeridos · el backend flipea a "used" si se usaron TODAS). best-
// effort: el registro NO bloquea la navegacion. NORMALIZACIÓN TOLERANTE: plataforma = texto libre del LLM.
interface IdeaPost { plataforma?: string; idea?: string }
interface BoxIdea { text: string; idx: number }
interface Box { key: string; label: string; platform: string | null; ideas: BoxIdea[] }

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
// desconocida conserva su nombre crudo y su idea (nunca se pierde ni rompe). ⚠️ idx = posicion en
// el array PLANO posts_sugeridos (no dentro del grupo) · use-idea lo necesita para marcar LA idea correcta.
export function buildBoxes(posts: IdeaPost[]): Box[] {
  const map = new Map<string, Box>();
  posts.forEach((p, idx) => {
    const raw = (p?.plataforma ?? "").trim();
    const norm = normalize(raw);
    const key = norm ?? (raw.toLowerCase() || "otra");
    const label = norm ? PLATFORM_LABELS[norm as keyof typeof PLATFORM_LABELS] : (raw || "Otra red");
    const text = (p?.idea ?? "").trim();
    if (!map.has(key)) map.set(key, { key, label, platform: norm, ideas: [] });
    if (text) map.get(key)!.ideas.push({ text, idx });
  });
  return [...map.values()];
}

export function StrategyIdeaBoxes({ strategyId, posts, usedIdxs = [] }: { strategyId: string; posts: IdeaPost[]; usedIdxs?: number[] }) {
  const navigate = useNavigate();
  const recordIdea = useRecordIdeaUse();
  // Fase C.1 · ocultar las ideas YA usadas (idx ∈ usedIdxs · cruce exacto con posts_sugeridos) y
  // descartar los cuadros de red que queden sin ideas disponibles.
  const usedSet = new Set(usedIdxs);
  const boxes = buildBoxes(Array.isArray(posts) ? posts : [])
    .map((b) => ({ ...b, ideas: b.ideas.filter((i) => !usedSet.has(i.idx)) }))
    .filter((b) => b.ideas.length > 0);
  if (boxes.length === 0) return null;

  // Fase B.3 · manda SOLO esta idea + la registra via /use-idea (idx correcto · el backend flipea a
  // "used" cuando se usaron todas). best-effort: si /use-idea falla NO bloquea la navegacion al generador.
  const go = (box: Box, item: BoxIdea) => {
    try { recordIdea.mutate({ id: strategyId, idea_idx: item.idx, platform: box.platform ?? box.label, brief: item.text }); } catch { /* best-effort */ }
    navigate("/content-lab", { state: { brief: item.text, ...(box.platform ? { platform: box.platform } : {}) } });
  };

  return (
    <div className="grid gap-2 sm:grid-cols-2">
      {boxes.map((box) => (
        <div key={box.key} className="rounded-lg border border-border/40 bg-card/50 p-3 space-y-2">
          <span className="text-xs font-semibold">{box.label}</span>
          {box.ideas.map((item) => (
            <div key={item.idx} className="flex items-start justify-between gap-2">
              <p className="text-sm flex-1">{item.text}</p>
              <Button
                size="sm" variant="ghost"
                className="h-7 px-2 gap-1 text-primary hover:text-primary shrink-0"
                aria-label={`Usar en Content Lab: ${item.text}`}
                onClick={() => go(box, item)}
              >
                Usar <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
