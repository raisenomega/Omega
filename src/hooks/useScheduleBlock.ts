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
  scheduledAt: string;  // ISO datetime-local · "YYYY-MM-DDTHH:MM"
}

async function resolveAccountId(clientId: string, platform: string): Promise<string> {
  const { data, error } = await supabase
    .from("social_accounts")
    .select("id")
    .eq("client_id", clientId)
    .eq("platform", platform)
    .order("is_primary", { ascending: false })
    .limit(1)
    .maybeSingle();
  if (error) throw new Error(`account_lookup_failed:${error.message}`);
  if (!data) throw new Error(`No hay cuenta de ${platform} conectada para este cliente`);
  return data.id;
}

function parseHashtags(text: string | undefined): string[] {
  if (!text) return [];
  return text.split(/\s+/).filter(t => t.startsWith("#")).map(t => t.slice(1));
}

export function useScheduleBlock() {
  return useMutation<SchedulePostResponse, Error, ScheduleBlockInput>({
    mutationFn: async ({ block, clientId, platform, scheduledAt }) => {
      if (!block.caption) throw new Error("Falta el caption del bloque");
      const accountId = await resolveAccountId(clientId, platform);
      const [date, time] = scheduledAt.split("T");
      return apiPost<SchedulePostResponse>(`/calendar/schedule/`, {
        account_id: accountId,
        content_lab_id: block.caption.id,
        content_type: "post",
        text_content: block.caption.generated_text,
        image_url: block.image?.generated_text ?? null,
        hashtags: parseHashtags(block.hashtags?.generated_text),
        scheduled_date: date,
        scheduled_time: time + ":00",
      });
    },
  });
}
