import { useMutation } from "@tanstack/react-query";
import type { FormState, VariationLabel } from "@/components/content/ContentLabFormV2";
import type { ResultV2 } from "@/components/content/ResultCardV2";
import { apiGet, apiPost } from "@/lib/api-client";

interface JobStartResponse { job_id: string; status: string; }
interface JobStatusResponse { job_id: string; status: string; video_url?: string; error?: string; }

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
      const { job_id } = await apiPost<JobStartResponse>(`/content-lab/generate-video`, {
        prompt: form.topic,
        ratio: "1280:768",
        aspect_ratio: form.aspect,
      });

      for (let i = 0; i < MAX_ATTEMPTS; i++) {
        await sleep(POLL_INTERVAL_MS);
        const job = await apiGet<JobStatusResponse>(`/content-lab/generate-video/${job_id}`);
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
