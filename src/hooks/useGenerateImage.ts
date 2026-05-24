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
