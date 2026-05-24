import { useRef, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import type { FormState, VariationLabel } from "@/components/content/ContentLabFormV2";
import type { ResultV2 } from "@/components/content/ResultCardV2";
import { apiGet, apiPost, apiDelete } from "@/lib/api-client";

interface JobStartResponse { job_id: string; status: string; }
interface JobStatusResponse { job_id: string; status: string; video_url?: string; error?: string; }

const sleep = (ms: number) => new Promise<void>(r => setTimeout(r, ms));
const POLL_INTERVAL_MS = 5000;
const MAX_ATTEMPTS = 60;

export interface VideoJobInput {
  form: FormState;
  selectedLabels: VariationLabel[];
}

// DEBT-CL-010: useRef cancel + apiDelete server-side + check status='cancelled'.
// Cierra agujero económico Veo ($2-10/video) si user cancela mid-flight.
export function useVideoJobPolling() {
  const cancelRef = useRef(false);
  const activeJobIdRef = useRef<string | null>(null);

  const mutation = useMutation<ResultV2[], Error, VideoJobInput>({
    mutationFn: async ({ form, selectedLabels }) => {
      cancelRef.current = false;
      activeJobIdRef.current = null;
      const { job_id } = await apiPost<JobStartResponse>(`/content-lab/generate-video`, {
        prompt: form.topic,
        ratio: "1280:768",
        aspect_ratio: form.aspect,
        client_id: form.clientId || undefined,
      });
      activeJobIdRef.current = job_id;

      for (let i = 0; i < MAX_ATTEMPTS; i++) {
        if (cancelRef.current) {
          await apiDelete(`/content-lab/generate-video/${job_id}`).catch(() => {});
          throw new Error("cancelled_by_user");
        }
        await sleep(POLL_INTERVAL_MS);
        if (cancelRef.current) {
          await apiDelete(`/content-lab/generate-video/${job_id}`).catch(() => {});
          throw new Error("cancelled_by_user");
        }
        const job = await apiGet<JobStatusResponse>(`/content-lab/generate-video/${job_id}`);
        if (job.status === "cancelled") throw new Error("cancelled_by_user");
        if (job.status === "completed" && job.video_url) {
          activeJobIdRef.current = null;
          return [{
            id: job.job_id, generated_text: job.video_url, content_type: "video",
            variation_label: selectedLabels[0], virality_score: 0, virality_estimated: false,
          }];
        }
        if (job.status === "failed") throw new Error(job.error ?? "video_generation_failed");
      }
      throw new Error("video_timeout · 5min sin respuesta");
    },
  });

  const cancel = useCallback(() => {
    cancelRef.current = true;
    // Si la mutation ya inició job_id pero no estamos en loop checkpoint,
    // dispara DELETE side-effect inmediato para acelerar server cancel.
    const jid = activeJobIdRef.current;
    if (jid) apiDelete(`/content-lab/generate-video/${jid}`).catch(() => {});
  }, []);

  return { ...mutation, cancel };
}
