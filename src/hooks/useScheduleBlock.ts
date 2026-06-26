import { useMutation } from "@tanstack/react-query";
import { apiPost } from "@/lib/api-client";
import { toUtcIso } from "@/lib/schedule-time";
import type { BlockState } from "@/components/content/ResultCardV2";

interface SchedulePostResponse {
  id: string;
  status: string;
}

export interface ScheduleBlockInput {
  block: BlockState;
  clientId: string;
  platform: string;
  platforms?: string[];  // E · redes marcadas (fan-out). Backend crea 1 row por red active resuelta.
  scheduledAt: string;  // formato 'YYYY-MM-DDTHH:MM' del datetime-local input
  accountId?: string;  // DEBT-CL-015 · vacío = backend resuelve primera activa (solo flujo legacy single-red)
}

export const MEDIA_TYPES = ["image", "video"];
export const MAX_PIECES = 12;  // tope de piezas por bloque (A+B · gateado al agregar en useContentLabState)
const TEXT_EXCLUDED = ["image", "video", "hashtags"];

export function useScheduleBlock() {
  // DEBT-CL-018 (23 may 2026): N text items → N rows · backend espacia
  // según LIMITS_OMEGA. POST /api/v1/calendar-v3/schedule/ con content_ids
  // list · response es list de N rows · atómico (todos o ninguno).
  return useMutation<SchedulePostResponse[], Error, ScheduleBlockInput>({
    mutationFn: async ({ block, clientId, platform, platforms, scheduledAt, accountId }) => {
      if (block.items.length === 0) throw new Error("Bloque vacío");
      const textItems = block.items.filter(i => !TEXT_EXCLUDED.includes(i.content_type));
      const mediaItem = block.items.find(i => MEDIA_TYPES.includes(i.content_type));
      if (textItems.length === 0) {
        throw new Error("Bloque sin items de texto · agregá al menos 1 caption/post/email/etc");
      }
      // Bug tz (11 jun): convertir la hora LOCAL del usuario a UTC explícito (Z) ·
      // sino el backend la guardaba como UTC → corrimiento -4h en AST.
      const scheduledForIso = toUtcIso(scheduledAt);
      return apiPost<SchedulePostResponse[]>(`/calendar-v3/schedule/`, {
        client_id: clientId,
        platform,                                        // seed · satisface campo requerido + retrocompat
        platforms: platforms?.length ? platforms : undefined,  // E · fan-out multi-red (si vacío → backend usa platform)
        content_ids: textItems.map(t => t.id),
        scheduled_for: scheduledForIso,
        media_url: mediaItem?.generated_text ?? null,
        is_story: mediaItem?.is_story ?? false,  // Pieza 3 · placement (REX filtra a IG/FB al publicar)
        social_account_id: accountId || undefined,  // DEBT-CL-015 (solo legacy single-red · ignorado en fan-out)
      });
    },
  });
}
