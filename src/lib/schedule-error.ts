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
 * Damage gate (11 jun): 422 `brand_voice_damages_brand:cid=score,...` significa
 * que el contenido DAÑA la voz de marca (insultos/spam/off-tone · score <0.5) →
 * mensaje de daño + cuántos (Ajuste 1). El contenido genérico (0.5–0.7) ya NO da
 * 422 (pasa con flag below_brand_bar). 503 `brand_voice_check_unavailable` →
 * mensaje honesto sin filtrar el param force. null = cae al toast genérico.
 */
export const brandVoiceScheduleError = (msg: string): ScheduleErrorMessage | null => {
  if (msg.startsWith("brand_voice_damages_brand")) {
    const list = msg.split(":")[1] ?? "";
    const count = list.split(",").filter(Boolean).length;
    const cuantos = count > 1
      ? `${count} contenidos dañan`
      : "Este contenido daña";
    return {
      title: "Daña la voz de marca",
      description: `${cuantos} la voz de marca del cliente (insultos, spam u off-tone severo). Regeneralo o aprueba manualmente.`,
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
