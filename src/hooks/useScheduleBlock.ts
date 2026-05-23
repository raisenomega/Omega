import { useMutation } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
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

async function resolveAccountId(clientId: string, platform: string): Promise<string> {
  const { data, error } = await supabase
    .from("social_accounts").select("id")
    .eq("client_id", clientId).eq("platform", platform)
    .order("is_primary", { ascending: false }).limit(1).maybeSingle();
  if (error) throw new Error(`account_lookup_failed:${error.message}`);
  if (!data) throw new Error(`No hay cuenta de ${platform} conectada para este cliente`);
  return data.id;
}

function parseHashtags(text: string | undefined): string[] {
  if (!text) return [];
  return text.split(/\s+/).filter(t => t.startsWith("#")).map(t => t.slice(1));
}

const MEDIA_TYPES = ["image", "video"];
const TEXT_EXCLUDED = ["image", "video", "hashtags"];

export function useScheduleBlock() {
  return useMutation<SchedulePostResponse, Error, ScheduleBlockInput>({
    mutationFn: async ({ block, clientId, platform, scheduledAt }) => {
      if (block.items.length === 0) throw new Error("Bloque vacío");
      const textItem = block.items.find(i => !TEXT_EXCLUDED.includes(i.content_type));
      const mediaItem = block.items.find(i => MEDIA_TYPES.includes(i.content_type));
      const hashtagsItem = block.items.find(i => i.content_type === "hashtags");
      const anchor = textItem ?? block.items[0];
      const accountId = await resolveAccountId(clientId, platform);
      const [date, time] = scheduledAt.split("T");
      return apiPost<SchedulePostResponse>(`/calendar/schedule/`, {
        account_id: accountId,
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
