// Data shape para la sección "Agente Publicador" de AddOnsPage. Frontend-only ·
// sin Stripe product aún (botón → toast "Próximamente"). `code` es identificador local.
// Cuando exista el backend, conectar a checkout como los Video Packs (useVideoPackCheckout).

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
      "Planifica tu semana de contenido con ARIA",
      "Programa hasta 7 posts con espaciado automático",
      "Alerta por email a la hora exacta de publicación",
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
      "Todo lo del plan Esencial",
      "Reporte semanal: publicados vs pendientes vs cancelados",
      "ARIA sugiere el mejor día y hora para publicar",
      "Aprende de tus aprobaciones semana a semana",
      "Genera el plan de contenido semanal completo solo",
      "Notificación si pasó la hora y no publicaste",
    ],
    idealFor: "marcas que no pueden permitirse un día sin publicar",
  },
] as const;
