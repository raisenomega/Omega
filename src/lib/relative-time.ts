// "Datos de hace X" · tiempo relativo legible en español. Sin datos sintéticos:
// si no hay fecha (generated_at null) devolvemos un fallback honesto.
export function dataAgoLabel(at: string | null): string {
  if (!at) return "Sin fecha de análisis";
  const then = new Date(at).getTime();
  if (Number.isNaN(then)) return "Sin fecha de análisis";

  const secs = Math.max(0, Math.round((Date.now() - then) / 1000));
  if (secs < 60) return "Datos de hace unos segundos";

  const mins = Math.round(secs / 60);
  if (mins < 60) return `Datos de hace ${mins} ${mins === 1 ? "minuto" : "minutos"}`;

  const hours = Math.round(mins / 60);
  if (hours < 24) return `Datos de hace ${hours} ${hours === 1 ? "hora" : "horas"}`;

  const days = Math.round(hours / 24);
  return `Datos de hace ${days} ${days === 1 ? "día" : "días"}`;
}
