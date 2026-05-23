import { useMutation } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import type { FormState, VariationLabel } from "@/components/content/ContentLabFormV2";
import type { ResultV2 } from "@/components/content/ResultCardV2";

interface VariationItem {
  id: string;
  label: "A" | "B" | "C";
  temperature: number;
  generated_text: string;
  virality_score: number;
  virality_estimated: boolean;
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

async function authHeaders(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();
  return { "Content-Type": "application/json", Authorization: `Bearer ${session?.access_token ?? ""}` };
}

function apiBase(): string {
  return import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
}

export interface GenerateInput {
  form: FormState;
  selectedLabels: VariationLabel[];
}

export function useGenerateText() {
  return useMutation<ResultV2[], Error, GenerateInput>({
    mutationFn: async ({ form, selectedLabels }) => {
      const variationsCount = selectedLabels.length > 1 ? 3 : 1;
      const res = await fetch(`${apiBase()}/content-lab/generate`, {
        method: "POST",
        headers: await authHeaders(),
        body: JSON.stringify({
          platform: form.platform,
          content_type: form.type,
          topic: form.topic,
          tone: form.tone,
          variations: variationsCount,
        }),
      });
      if (!res.ok) {
        const err = (await res.json().catch(() => ({}))) as { detail?: string };
        throw new Error(typeof err.detail === "string" ? err.detail : `HTTP ${res.status}`);
      }
      const data = (await res.json()) as GenerateTextResponse;
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
      }));
    },
  });
}
