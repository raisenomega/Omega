// Data shape para VideoAddonModal · espejo de MODELO_NEGOCIO §4.4 y
// backend/app/bc_billing/domain/video_entitlements.py
// Mantener bullets espejo del doc para que el cliente vea exactamente lo
// que se aprobó en pricing.

export interface VideoPack {
  name: string;
  price: string;
  bullets: string[];
  idealFor: string;
}

export const VIDEO_PACKS: readonly VideoPack[] = [
  {
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
