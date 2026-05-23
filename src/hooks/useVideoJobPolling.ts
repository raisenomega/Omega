import { useMutation } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import type { FormState, VariationLabel } from "@/components/content/ContentLabFormV2";
import type { ResultV2 } from "@/components/content/ResultCardV2";

interface JobStartResponse { job_id: string; status: string; }
interface JobStatusResponse { job_id: string; status: string; video_url?: string; error?: string; }

async function authHeaders(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();
  return { "Content-Type": "application/json", Authorization: `Bearer ${session?.access_token ?? ""}` };
}

function apiBase(): string {
  return import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
}

const sleep = (ms: number) => new Promise<void>(r => setTimeout(r, ms));
const POLL_INTERVAL_MS = 5000;
const MAX_ATTEMPTS = 60;

export interface VideoJobInput {
  form: FormState;
  selectedLabels: VariationLabel[];
}

export function useVideoJobPolling() {
  return useMutation<ResultV2[], Error, VideoJobInput>({
    mutationFn: async ({ form, selectedLabels }) => {
      const startRes = await fetch(`${apiBase()}/content-lab/generate-video`, {
        method: "POST",
        headers: await authHeaders(),
        body: JSON.stringify({ prompt: form.topic, ratio: "1280:768" }),
      });
      if (!startRes.ok) {
        const err = (await startRes.json().catch(() => ({}))) as { detail?: string };
        throw new Error(typeof err.detail === "string" ? err.detail : `HTTP ${startRes.status}`);
      }
      const { job_id } = (await startRes.json()) as JobStartResponse;

      for (let i = 0; i < MAX_ATTEMPTS; i++) {
        await sleep(POLL_INTERVAL_MS);
        const sRes = await fetch(`${apiBase()}/content-lab/generate-video/${job_id}`, { headers: await authHeaders() });
        if (!sRes.ok) throw new Error(`polling_http_${sRes.status}`);
        const job = (await sRes.json()) as JobStatusResponse;
        if (job.status === "completed" && job.video_url) {
          return [{
            id: job.job_id,
            generated_text: job.video_url,
            content_type: "video",
            variation_label: selectedLabels[0],
            virality_score: 0,
            virality_estimated: false,
          }];
        }
        if (job.status === "failed") throw new Error(job.error ?? "video_generation_failed");
      }
      throw new Error("video_timeout · 5min sin respuesta");
    },
  });
}
