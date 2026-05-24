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
  scheduledAt: string;
}

function parseHashtags(text: string | undefined): string[] {
  if (!text) return [];
  return text.split(/\s+/).filter(t => t.startsWith("#")).map(t => t.slice(1));
}

const MEDIA_TYPES = ["image", "video"];
const TEXT_EXCLUDED = ["image", "video", "hashtags"];

export function useScheduleBlock() {
  // DEBT-CL-013 cerrada: cero Supabase directo · backend resuelve account_id
  // desde client_id+platform con auth + RBAC (cierra agujero seguridad C).
  return useMutation<SchedulePostResponse, Error, ScheduleBlockInput>({
    mutationFn: async ({ block, clientId, platform, scheduledAt }) => {
      if (block.items.length === 0) throw new Error("Bloque vacío");
      const textItem = block.items.find(i => !TEXT_EXCLUDED.includes(i.content_type));
      const mediaItem = block.items.find(i => MEDIA_TYPES.includes(i.content_type));
      const hashtagsItem = block.items.find(i => i.content_type === "hashtags");
      const anchor = textItem ?? block.items[0];
      const [date, time] = scheduledAt.split("T");
      return apiPost<SchedulePostResponse>(`/calendar/schedule/`, {
        client_id: clientId,
        platform,
        content_lab_id: anchor.id,
        content_type: "post",
        text_content: textItem?.generated_text ?? block.items[0].generated_text,
        image_url: mediaItem?.generated_text ?? null,
        hashtags: parseHashtags(hashtagsItem?.generated_text),
        scheduled_date: date,
        scheduled_time: time + ":00",
      });
    },
  });
}
