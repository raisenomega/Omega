import { useMutation } from "@tanstack/react-query";
import type { FormState, VariationLabel } from "@/components/content/ContentLabFormV2";
import type { ResultV2 } from "@/components/content/ResultCardV2";
import { apiPost } from "@/lib/api-client";

interface GenerateImageResponse {
  id: string;
  content_type: string;
  generated_text: string;
}

export interface GenerateImageInput {
  form: FormState;
  selectedLabels: VariationLabel[];
}

export function useGenerateImage() {
  return useMutation<ResultV2[], Error, GenerateImageInput>({
    mutationFn: async ({ form, selectedLabels }) => {
      const data = await apiPost<GenerateImageResponse>(`/content-lab/generate-image`, {
        prompt: form.topic,
        style: "realistic",
        aspect_ratio: form.aspect,
        reference_image_b64: form.reference_image_b64,
        client_id: form.clientId || undefined,  // DEBT-CL-005 · multi-client reseller
        reference_attachment_b64: form.reference_attachment_b64,  // DEBT-CL-020
        reference_mime_type: form.reference_mime_type,
        apply_logo: form.applyLogo,  // Fase 1 · opt-in logo overlay
      });
      return [{
        id: data.id,
        generated_text: data.generated_text,
        content_type: "image",
        variation_label: selectedLabels[0],
        virality_score: 0,
        virality_estimated: false,
      }];
    },
  });
}
