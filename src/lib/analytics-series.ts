/** Transformaciones PURAS de las series del panel Analytics (testeable · sin I/O).
 * Las series vienen ACUMULADO del backend (Zernio no tiene ventana · NO "del período"). */

export interface EngagementSeriesPoint {
  date: string;
  impressions: number;
  reach: number;
  likes: number;
  comments: number;
  shares: number;
  saves: number;
  clicks: number;
  views: number;
}

export interface PostsSeriesPoint {
  date: string;
  count: number;
}

/** Σ interacciones (likes+comments+shares+saves · views NO es interacción) por día → 1 línea
 * limpia de "engagement en el tiempo". Vacío → [] (empty state honesto, no chart en cero). */
export function engagementTotalSeries(
  series: EngagementSeriesPoint[],
): { date: string; engagement: number }[] {
  return series.map((p) => ({
    date: p.date,
    engagement: p.likes + p.comments + p.shares + p.saves,
  }));
}

/** % del KPI engagement promedio histórico · "—" si null (cero-sintético: nunca 0 de relleno). */
export function fmtPct(v: number | null): string {
  return v === null ? "—" : `${v}%`;
}

/** ¿Hay suficiente historial para mostrar una TENDENCIA? <2 puntos = 1 solo dato → NO dibujar
 * línea (sugeriría tendencia donde solo hay un punto · regla P1). El GrowthChart muestra
 * "historial insuficiente" en vez de una línea plana engañosa. */
export function hasGrowthTrend(points: { date: string; followers: number }[]): boolean {
  return points.length >= 2;
}
