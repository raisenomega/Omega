import { useMutation } from "@tanstack/react-query";
import type { FormState, VariationLabel } from "@/components/content/ContentLabFormV2";
import type { ResultV2 } from "@/components/content/ResultCardV2";
import { apiGet, apiPost } from "@/lib/api-client";

// DEBT-IMAGE-ASYNC F4 · detección POR FORMA de la respuesta (invisible con flag OFF):
//   flag OFF → {generated_text} (imagen directa · comportamiento viejo INTACTO)
//   flag ON  → {job_id} → pollea GET /generate-image/{job_id} hasta completed (molde useVideoJobPolling)
// El branch vive ACÁ (no en un hook aparte) porque el frontend NO conoce el flag del backend ·
// distingue por la forma que llega. handleGenerate sigue igual (await mutateAsync → ResultV2[]).
interface ImageSyncResponse { id: string; content_type: string; generated_text: string; }
interface ImageJobStart { job_id: string; status: string; }
interface ImageJobStatus { job_id: string; status: string; image_url?: string; error?: string; content_id?: string; }

const sleep = (ms: number) => new Promise<void>(r => setTimeout(r, ms));
const POLL_INTERVAL_MS = 5000;
const MAX_ATTEMPTS = 60;  // 5 min · igual que video (imagen ~48s · margen de sobra)

export interface GenerateImageInput {
  form: FormState;
  selectedLabels: VariationLabel[];
}

function _result(id: string, url: string, label: VariationLabel): ResultV2 {
  return {
    id, generated_text: url, content_type: "image",
    variation_label: label, virality_score: 0, virality_estimated: false,
  };
}

export function useGenerateImage() {
  return useMutation<ResultV2[], Error, GenerateImageInput>({
    mutationFn: async ({ form, selectedLabels }) => {
      const data = await apiPost<ImageSyncResponse | ImageJobStart>(`/content-lab/generate-image`, {
        prompt: form.topic,
        // Decisión de producto (2-jun-2026): style fijo en "realistic" INTENCIONAL. Otros estilos
        // (cartoon/minimal) se piden vía el prompt de texto del usuario, no vía selector UI. NO es
        // violación G9 — es default consciente. El backend soporta los otros valores; exponerlos si
        // se construye la UI de estilo (DEBT-IMAGE-STYLE-SELECTOR · plan listo en chat 2-jun).
        style: "realistic",
        aspect_ratio: form.aspect,
        reference_image_b64: form.reference_image_b64,
        client_id: form.clientId || undefined,  // DEBT-CL-005 · multi-client reseller
        reference_attachment_b64: form.reference_attachment_b64,  // DEBT-CL-020
        reference_mime_type: form.reference_mime_type,
        apply_logo: form.applyLogo,  // Fase 1 · opt-in logo overlay
      });
      // flag ON → async: pollear hasta completed/failed. flag OFF → imagen directa (viejo).
      if ("job_id" in data) {
        for (let i = 0; i < MAX_ATTEMPTS; i++) {
          await sleep(POLL_INTERVAL_MS);
          const job = await apiGet<ImageJobStatus>(`/content-lab/generate-image/${data.job_id}`);
          // BUG 11 jun: usar el content_id real (fila content_lab_generated del worker) como id del
          // resultado · NO el job_id · sino Guardar busca content_lab_generated por job_id → 404.
          if (job.status === "completed" && job.image_url) return [_result(job.content_id ?? job.job_id, job.image_url, selectedLabels[0])];
          if (job.status === "failed") throw new Error(job.error ?? "image_generation_failed");
        }
        throw new Error("image_timeout · 5min sin respuesta");
      }
      return [_result(data.id, data.generated_text, selectedLabels[0])];  // OFF · comportamiento viejo
    },
  });
}
