// Info de presentación por nivel ARIA (1-4) · label/color/desc. Fuente única compartida
// entre la sección de settings del cliente (ARIASection) y la vista de agencia (ClientDetail).
export interface AriaLevelInfo {
  label: string;
  color: string;
  desc: string;
}

export const ARIA_LEVELS: Record<number, AriaLevelInfo> = {
  1: { label: "ARIA 1.0 · Adopción", color: "bg-muted text-muted-foreground", desc: "Conversacional básico · onboarding y respuestas FAQ." },
  2: { label: "ARIA 2.0 · Básico", color: "bg-blue-500 text-white", desc: "Conversacional estándar · sugerencias + análisis simple." },
  3: { label: "ARIA 3.0 · Pro", color: "bg-emerald-500 text-white", desc: "Avanzado · NBA engine + auto-publicación con aprobación." },
  4: { label: "ARIA 4.0 · Pro+addons", color: "bg-amber-500 text-white", desc: "Near-NOVA · contexto extendido + autónomas con guardrails." },
};

export const ariaLevelInfo = (level: number | null | undefined): AriaLevelInfo =>
  ARIA_LEVELS[level ?? 1] ?? ARIA_LEVELS[1];
