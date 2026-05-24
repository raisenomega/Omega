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
  // DEBT-CL-017 + path X (23 may 2026): apunta al handler V3 que usa el
  // schema real de scheduled_posts (client_id, social_account_id, content_id,
  // scheduled_for, status, media_url). El handler legacy /calendar/schedule/
  // queda intacto pero deprecated (DEBT-031 partial).
  return useMutation<SchedulePostResponse, Error, ScheduleBlockInput>({
    mutationFn: async ({ block, clientId, platform, scheduledAt }) => {
      if (block.items.length === 0) throw new Error("Bloque vacío");
      const textItem = block.items.find(i => !TEXT_EXCLUDED.includes(i.content_type));
      const mediaItem = block.items.find(i => MEDIA_TYPES.includes(i.content_type));
      const anchor = textItem ?? block.items[0];
      // scheduledAt formato 'YYYY-MM-DDTHH:MM' · agregar segundos para ISO completo
      const scheduledForIso = scheduledAt.length === 16 ? `${scheduledAt}:00` : scheduledAt;
      return apiPost<SchedulePostResponse>(`/calendar-v3/schedule/`, {
        client_id: clientId,
        platform,
        content_id: anchor.id,
        scheduled_for: scheduledForIso,
        media_url: mediaItem?.generated_text ?? null,
      });
    },
  });
}
