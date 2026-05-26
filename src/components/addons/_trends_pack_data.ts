// Data shape para la sección "Agente de Tendencias" de AddOnsPage. Frontend-only ·
// sin Stripe product aún (botón → toast "Próximamente"). `code` es identificador local.
// Producto único (1 card). Mismo patrón que _publisher_packs_data.ts.

export interface TrendsPack {
  code: string;
  name: string;
  price: string;
  bullets: string[];
  idealFor: string;
}

export const TRENDS_PACK: TrendsPack = {
  code: "trends_unico",
  name: "Agente de Tendencias",
  price: "$15/mes",
  bullets: [
    "Detecta tendencias de tu industria en tiempo real",
    "Búsquedas personalizadas por región y vertical",
    "Monitoreo de competidores cada 6 horas",
    "Noticias relevantes de tu sector cada 2 horas",
    "ARIA recibe el contexto antes de cada generación",
    "Alertas cuando tu competencia publica algo relevante",
  ],
  idealFor: "negocios que quieren estar un paso adelante de su competencia",
};
