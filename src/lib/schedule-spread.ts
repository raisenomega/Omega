// Spread automático de timestamps para bulk schedule · split de ScheduleModalV2 (C4)
export const SPREAD_HOURS = 2;   // LIMITS_OMEGA MIN_HORAS_ENTRE_POSTS
export const SPREAD_MAX_DAY = 3; // reparto bulk 3/día (UX · desacoplado del límite de publicación de REX por red)

export function computeSpread(base: string, n: number): string[] {
  if (n < 1 || !base) return [];
  const baseDate = new Date(base);
  return Array.from({ length: n }, (_, i) => {
    const day = Math.floor(i / SPREAD_MAX_DAY);
    const inDay = i % SPREAD_MAX_DAY;
    const ts = new Date(baseDate);
    ts.setDate(ts.getDate() + day);
    ts.setHours(ts.getHours() + inDay * SPREAD_HOURS);
    return ts.toLocaleString("es-AR", { dateStyle: "short", timeStyle: "short" });
  });
}
