import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Brain, Image as ImageIcon, Video, Sparkles } from "lucide-react";
import type { LucideIcon } from "lucide-react";

// DEBT-057/058 (cierre · 25 may): este panel reemplaza el legacy Lovable multi-proveedor
// (vendía "hasta 3 proveedores" + consultaba tablas fantasma ai_providers/client_ai_config).
// Es read-only y refleja la verdad (P1 · regla I1 Solo-Anthropic): cero queries, cero writes.

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
    color: "text-purple-400",
    capability: "Razonamiento y texto",
    provider: "Anthropic Claude",
    detail: "Haiku 4.5 (clasificación · tags) · Sonnet 4.6 (contenido · default) · Opus 4.7 (decisiones críticas)",
  },
  {
    icon: ImageIcon,
    color: "text-blue-400",
    capability: "Imagen",
    provider: "Nano Banana",
    detail: "Generación de imágenes (Google Gemini · única excepción de infraestructura)",
  },
  {
    icon: Video,
    color: "text-amber-400",
    capability: "Video",
    provider: "Veo 3.1",
    detail: "Video con audio nativo (excepción de infraestructura)",
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
          OmegaRaisen opera con un único motor de razonamiento — Anthropic Claude — más motores
          dedicados para imagen y video. No hay selección de proveedor por cliente.
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
                  <span className="text-xs font-medium text-primary whitespace-nowrap">{e.provider}</span>
                </div>
                <p className="text-xs text-muted-foreground mt-0.5">{e.detail}</p>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
