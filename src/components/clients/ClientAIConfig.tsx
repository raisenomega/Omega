import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, Image as ImageIcon, Video, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";

// DEBT-057/058 (cierre · 25 may): panel read-only · refleja la verdad (P1 · I1 Solo-Anthropic
// para texto/razonamiento). Copy comercial · cero queries/writes.

interface Engine {
  icon: LucideIcon;
  color: string;
  capability: string;
  provider: string;
  detail: string;
}

const ENGINES: readonly Engine[] = [
  {
    icon: Brain,
    color: "text-amber-400",
    capability: "Razonamiento y contenido",
    provider: "Anthropic Claude",
    detail: "El cerebro de tu marca — crea, razona y decide por vos, con precisión y total seguridad.",
  },
  {
    icon: ImageIcon,
    color: "text-blue-400",
    capability: "Imagen",
    provider: "Nano Banana",
    detail: "Visuales únicos, generados al instante para cada publicación.",
  },
  {
    icon: Video,
    color: "text-purple-400",
    capability: "Video",
    provider: "Veo 3.1",
    detail: "Video con audio nativo, en calidad profesional.",
  },
] as const;

export function ClientAIConfig() {
  return (
    <Card className="border-border/50 bg-card/60">
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          Motor de IA
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-xs text-muted-foreground">
          Tu marca piensa con <span className="font-semibold text-amber-500">Anthropic Claude</span>, la
          inteligencia artificial más <span className="font-medium text-amber-500">avanzada y segura</span> del
          mercado. Es el único motor detrás de todo tu contenido — sin proveedores que elegir, sin complejidad técnica.
        </p>
        {ENGINES.map((e) => {
          const Icon = e.icon;
          return (
            <div key={e.capability} className="flex items-start gap-3 p-3 rounded-lg border border-border/30 bg-muted/10">
              <div className="h-9 w-9 rounded-lg bg-muted/30 flex items-center justify-center shrink-0">
                <Icon className={`h-5 w-5 ${e.color}`} />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-baseline justify-between gap-2">
                  <p className="text-sm font-semibold">{e.capability}</p>
                  <span className="text-xs font-medium text-amber-500 whitespace-nowrap">{e.provider}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-0.5">{e.detail}</p>
              </div>
            </div>
          );
        })}
        <p className="text-xs text-muted-foreground">
          Para imagen y video sumamos la tecnología de <span className="font-medium text-amber-500">Google (Gemini y Veo)</span> —
          siempre bajo la dirección creativa de Claude.
        </p>
      </CardContent>
    </Card>
  );
}
