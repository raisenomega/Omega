/**
 * Mapea el error del backend de POST /calendar-v3/schedule/ a un mensaje
 * legible para el usuario (extraído de useContentLabState · regla ≤75L del
 * archivo tocado · P0-2 auditoría 10 jun 2026). Solo el caso de voz de marca
 * (gate X5); el resto lo maneja el toast genérico de "Error al agendar".
 *
 * NO incluye botón/acción de override (force_brand_voice) · eso es Fase 2+.
 */

export type ScheduleErrorMessage = { title: string; description: string };

/**
 * 422 `brand_voice_below_threshold:cid=score,...` → mensaje que dice CUÁNTOS
 * fallaron (Ajuste 1). 503 `brand_voice_check_unavailable` → mensaje honesto
 * sin filtrar tecnicismos (no menciona el param force al usuario). null = no
 * es un error de voz de marca → cae al toast genérico.
 */
export const brandVoiceScheduleError = (msg: string): ScheduleErrorMessage | null => {
  if (msg.startsWith("brand_voice_below_threshold")) {
    const list = msg.split(":")[1] ?? "";
    const count = list.split(",").filter(Boolean).length;
    const cuantos = count > 1
      ? `${count} contenidos no pasan`
      : "Este contenido no pasa";
    return {
      title: "Filtro de voz de marca",
      description: `${cuantos} el filtro de voz de marca del cliente (score < 0.7). Regeneralo o aprueba manualmente.`,
    };
  }
  if (msg.startsWith("brand_voice_check_unavailable")) {
    return {
      title: "Verificador no disponible",
      description: "El filtro de voz de marca no está disponible ahora mismo. Intentá de nuevo en unos minutos.",
    };
  }
  return null;
};
