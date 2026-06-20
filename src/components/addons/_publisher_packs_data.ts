// Data shape para la sección "Agente Publicador" de AddOnsPage. El checkout Stripe es REAL
// (useAgentAddonCheckout → POST /billing/checkout-agent-addon · DEBT-091 · redirect Stripe).
// `code` = agent_addon_code que consume el checkout (publisher_esencial / publisher_pro).

export interface PublisherPack {
  code: string;
  name: string;
  price: string;
  bullets: string[];
  idealFor: string;
}

export const PUBLISHER_PACKS: readonly PublisherPack[] = [
  {
    code: "publisher_esencial",
    name: "Agente Publicador Esencial",
    price: "$19/mes",
    bullets: [
      "REX publica tus posts automáticamente a su hora — solo los que tú apruebas",
      "Organiza tu semana de contenido junto a ARIA",
      "Programa hasta 7 posts con espaciado automático",
      "Brand Voice aplicado antes de cada post",
      "Vista de calendario con estado de cada publicación",
    ],
    idealFor: "negocios que quieren consistencia sin esfuerzo",
  },
  {
    code: "publisher_pro",
    name: "Agente Publicador Pro",
    price: "$29/mes",
    bullets: [
      "REX publica tus posts automáticamente a su hora — solo los que tú apruebas",
      "Todo lo del plan Esencial",
      "Reporte semanal: publicados vs pendientes vs cancelados (Próximamente)",
      "ARIA sugiere el mejor día y hora para publicar (Próximamente)",
      "Aprende de tus aprobaciones semana a semana (Próximamente)",
      "Genera el plan de contenido semanal completo solo (Próximamente)",
      "Notificación si pasó la hora y no publicaste (Próximamente)",
    ],
    idealFor: "marcas que no pueden permitirse un día sin publicar",
  },
] as const;
