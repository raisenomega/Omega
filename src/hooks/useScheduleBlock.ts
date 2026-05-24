import { useMutation } from "@tanstack/react-query";
import { apiPost } from "@/lib/api-client";
import type { BlockState } from "@/components/content/ResultCardV2";

interface SchedulePostResponse {
  id: string;
  status: string;
}

export interface ScheduleBlockInput {
  block: BlockState;
  clientId: string;
  platform: string;
  scheduledAt: string;  // formato 'YYYY-MM-DDTHH:MM' del datetime-local input
}

const MEDIA_TYPES = ["image", "video"];
const TEXT_EXCLUDED = ["image", "video", "hashtags"];

export function useScheduleBlock() {
  // DEBT-CL-018 (23 may 2026): N text items → N rows · backend espacia
  // según LIMITS_OMEGA. POST /api/v1/calendar-v3/schedule/ con content_ids
  // list · response es list de N rows · atómico (todos o ninguno).
  return useMutation<SchedulePostResponse[], Error, ScheduleBlockInput>({
    mutationFn: async ({ block, clientId, platform, scheduledAt }) => {
      if (block.items.length === 0) throw new Error("Bloque vacío");
      const textItems = block.items.filter(i => !TEXT_EXCLUDED.includes(i.content_type));
      const mediaItem = block.items.find(i => MEDIA_TYPES.includes(i.content_type));
      if (textItems.length === 0) {
        throw new Error("Bloque sin items de texto · agregá al menos 1 caption/post/email/etc");
      }
      const scheduledForIso = scheduledAt.length === 16 ? `${scheduledAt}:00` : scheduledAt;
      return apiPost<SchedulePostResponse[]>(`/calendar-v3/schedule/`, {
        client_id: clientId,
        platform,
        content_ids: textItems.map(t => t.id),
        scheduled_for: scheduledForIso,
        media_url: mediaItem?.generated_text ?? null,
      });
    },
  });
}
