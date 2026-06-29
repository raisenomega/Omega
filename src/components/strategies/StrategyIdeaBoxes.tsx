import { useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PLATFORM_LABELS } from "@/lib/onboarding-constants";

// Estrategias C3 · agrupa las ideas de posts en CUADROS por red social y, por cuadro, una flecha
// que lleva SOLO esa red a Content Lab (brief = la idea de ese cuadro + platform pre-seleccionada).
// NO marca la estrategia "used" (idea suelta · ≠ botón "Usar" que lleva la estrategia completa).
// NORMALIZACIÓN TOLERANTE: la plataforma es texto libre del LLM (no enum · strategy_prompt.py).
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

export function StrategyIdeaBoxes({ posts }: { posts: IdeaPost[] }) {
  const navigate = useNavigate();
  const boxes = buildBoxes(Array.isArray(posts) ? posts : []);
  if (boxes.length === 0) return null;

  const go = (box: Box) => {
    const brief = box.ideas.join("\n\n") || box.label;
    navigate("/content-lab", { state: { brief, ...(box.platform ? { platform: box.platform } : {}) } });
  };

  return (
    <div className="grid gap-2 sm:grid-cols-2">
      {boxes.map((box) => (
        <div key={box.key} className="rounded-lg border border-border/40 bg-card/50 p-3 space-y-2">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-semibold">{box.label}</span>
            <Button
              size="sm" variant="ghost"
              className="h-7 px-2 gap-1 text-primary hover:text-primary"
              aria-label={`Usar la idea de ${box.label} en Content Lab`}
              onClick={() => go(box)}
            >
              Usar <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </div>
          {box.ideas.length > 0 ? (
            box.ideas.map((idea, i) => <p key={i} className="text-sm">{idea}</p>)
          ) : (
            <p className="text-sm text-muted-foreground">(idea sin texto)</p>
          )}
        </div>
      ))}
    </div>
  );
}
