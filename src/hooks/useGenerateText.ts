import { useMutation } from "@tanstack/react-query";
import type { FormState, VariationLabel } from "@/components/content/ContentLabFormV2";
import type { ResultV2 } from "@/components/content/ResultCardV2";
import { apiPost } from "@/lib/api-client";

interface VariationItem {
  id: string;
  label: "A" | "B" | "C";
  temperature: number;
  generated_text: string;
  virality_score: number;
  virality_estimated: boolean;
  brand_dna_score: number;
}

interface GenerateTextResponse {
  id: string;
  content_type: string;
  generated_text: string;
  virality_score: number;
  virality_estimated: boolean;
  variations: VariationItem[];
}

const LABEL_TO_FRONTEND: Record<string, VariationLabel> = {
  A: "Conservadora", B: "Balanceada", C: "Atrevida",
};

export interface GenerateInput {
  form: FormState;
  selectedLabels: VariationLabel[];
}

export function useGenerateText() {
  return useMutation<ResultV2[], Error, GenerateInput>({
    mutationFn: async ({ form, selectedLabels }) => {
      const variationsCount = selectedLabels.length > 1 ? 3 : 1;
      const data = await apiPost<GenerateTextResponse>(`/content-lab/generate`, {
        platform: form.platform,
        content_type: form.type,
        topic: form.topic,
        tone: form.tone,
        variations: variationsCount,
      });
      const items = variationsCount === 3
        ? data.variations.filter(v => selectedLabels.includes(LABEL_TO_FRONTEND[v.label]))
        : data.variations;
      return items.map(v => ({
        id: v.id,
        generated_text: v.generated_text,
        content_type: form.type,
        variation_label: LABEL_TO_FRONTEND[v.label] ?? selectedLabels[0],
        virality_score: v.virality_score,
        virality_estimated: v.virality_estimated,
        brand_dna_score: v.brand_dna_score,
      }));
    },
  });
}
