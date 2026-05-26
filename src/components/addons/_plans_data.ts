import type { PlanCode } from "@/lib/plan-limits";

// Orden de los planes pagos (de menor a mayor volumen).
export const PAID_PLANS: ReadonlyArray<"basic" | "pro" | "enterprise"> = ["basic", "pro", "enterprise"];

// Rank canónico de cada plan · usado para decidir upgrade vs downgrade.
export const PLAN_RANK: Record<PlanCode, number> = {
  adopcion: 0,
  basic: 1,
  pro: 2,
  enterprise: 3,
};

// Bullets del doc canónico · mostrados en cada PlanCard.
export const PLAN_HIGHLIGHTS: Record<"basic" | "pro" | "enterprise", string[]> = {
  basic: [
    "32 posts/mes",
    "1 cuenta por red (4 total)",
    "Content Lab + Brand Voice",
    "ARIA Nivel 1-2",
  ],
  pro: [
    "64 posts/mes",
    "2 cuentas por red (8 total)",
    "Todo + Centro de Inteligencia",
    "Reporte ejecutivo mensual PDF",
    "ARIA Nivel 3",
  ],
  enterprise: [
    "192 posts/mes",
    "3 cuentas por red (12 total)",
    "Todo de PRO ×3",
    "150 análisis SEO/GEO/AEO/mes",
    "300 imágenes extra/mes",
    "ARIA Nivel 4 incluido",
    "Análisis semanal del sitio + reporte semanal PDF",
    "Brave Search ilimitado · soporte prioritario",
    "Videos siempre por separado (Video Packs)",
  ],
};
