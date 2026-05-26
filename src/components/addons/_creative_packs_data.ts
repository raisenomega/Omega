// Data shape para la sección "Agente Creativo" de AddOnsPage. Frontend-only ·
// sin Stripe product aún (botón → toast "Próximamente"). `code` es identificador local.
// Mismo patrón que _publisher_packs_data.ts.

export interface CreativePack {
  code: string;
  name: string;
  price: string;
  bullets: string[];
  idealFor: string;
}

export const CREATIVE_PACKS: readonly CreativePack[] = [
  {
    code: "creative_esencial",
    name: "Agente Creativo Esencial",
    price: "$25/mes",
    bullets: [
      "Genera captions para Instagram, TikTok y LinkedIn",
      "Brand Voice aplicado en cada pieza de contenido",
      "30 formatos de contenido del Vault de prompts",
      "Genera imágenes con tu identidad visual",
      "Variaciones A/B para elegir el mejor ángulo",
    ],
    idealFor: "marcas que quieren contenido profesional sin contratar un copywriter",
  },
  {
    code: "creative_pro",
    name: "Agente Creativo Pro",
    price: "$35/mes",
    bullets: [
      "Todo lo del plan Esencial",
      "Videos cortos con audio nativo (Veo 3.1)",
      "ARIA revisa el prompt antes de generar",
      "Brand DNA completo aplicado (tono + keywords + estilo)",
      "Historial de aprobaciones para mejorar cada semana",
      "Genera bloques de 3 piezas coordinadas",
    ],
    idealFor: "marcas con presencia activa en redes que necesitan volumen y consistencia",
  },
] as const;
