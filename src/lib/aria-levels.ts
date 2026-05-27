// Info de presentación por nivel ARIA (1-4) · label/color/desc/benefits. Fuente única
// compartida entre settings del cliente (ARIASection), la vista de agencia (ClientDetail)
// y el modal de upgrade (AriaUpgradeModal).
export interface AriaLevelInfo {
  label: string;
  color: string;
  desc: string;
  benefits: readonly string[];
}

export const ARIA_LEVELS: Record<number, AriaLevelInfo> = {
  1: {
    label: "ARIA 1.0 · Adopción",
    color: "bg-muted text-muted-foreground",
    desc: "Conversacional básico · onboarding y respuestas FAQ.",
    benefits: ["Onboarding guiado", "Respuestas a preguntas frecuentes", "Chat conversacional básico"],
  },
  2: {
    label: "ARIA 2.0 · Básico",
    color: "bg-blue-500 text-white",
    desc: "Conversacional estándar · sugerencias + análisis simple.",
    benefits: ["Todo lo de 1.0", "Sugerencias de contenido", "Análisis simple de tu marca"],
  },
  3: {
    label: "ARIA 3.0 · Pro",
    color: "bg-emerald-500 text-white",
    desc: "Avanzado · NBA engine + auto-publicación con aprobación.",
    benefits: ["Todo lo de 2.0", "Mejor próxima acción (NBA)", "Auto-publicación con aprobación"],
  },
  4: {
    label: "ARIA 4.0 · Pro+addons",
    color: "bg-amber-500 text-white",
    desc: "Near-NOVA · contexto extendido + autónomas con guardrails.",
    benefits: ["Todo lo de 3.0", "Contexto extendido near-NOVA", "Acciones autónomas con guardrails"],
  },
};

export const ariaLevelInfo = (level: number | null | undefined): AriaLevelInfo =>
  ARIA_LEVELS[level ?? 1] ?? ARIA_LEVELS[1];
