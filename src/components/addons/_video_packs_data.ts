// Data shape para VideoAddonModal + AddOnsPage · espejo de MODELO_NEGOCIO §4.4
// y backend/app/bc_billing/domain/plan_pricing.py VIDEO_PACK_CODES.
// Mantener bullets espejo del doc + code sincronizado con backend frozen set.

export type VideoPackCode = "starter" | "creator" | "cinematic_pro";

export interface VideoPack {
  code: VideoPackCode;
  name: string;
  price: string;
  bullets: string[];
  idealFor: string;
}

export const VIDEO_PACKS: readonly VideoPack[] = [
  {
    code: "starter",
    name: "Pack Starter",
    price: "$39/mes",
    bullets: [
      "6 videos por mes (incluye 2 de regalo)",
      "Videos de 8 segundos · optimizados para Reels/Stories",
      "ARIA genera el prompt de video desde tu brief",
      "Brand DNA aplicado automáticamente",
    ],
    idealFor: "presencia constante en redes",
  },
  {
    code: "creator",
    name: "Pack Creator",
    price: "$95/mes",
    bullets: [
      "5 videos por mes (incluye 1 de regalo)",
      "Videos de 30 segundos · formato narrativo",
      "Script completo generado por ARIA antes de producir",
      "Brand DNA + revisión de tono antes de generar",
      "Apto para Facebook Ads y LinkedIn",
    ],
    idealFor: "campañas y contenido de valor",
  },
  {
    code: "cinematic_pro",
    name: "Pack Cinematic Pro",
    price: "$125/mes",
    bullets: [
      "3 videos por mes (incluye 1 de regalo)",
      "Videos de 60 segundos · calidad cinematográfica",
      "Script profesional con estructura HOOK-DESARROLLO-CTA",
      "Brand DNA completo aplicado en cada escena",
      "Revisión automática de voz de marca ANTES de generar",
      "Agente dedicado de video con memoria de tus aprobaciones previas",
    ],
    idealFor: "marca premium · contenido hero · campañas de alto impacto",
  },
] as const;
