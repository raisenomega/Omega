import { useMutation } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import type { FormState, VariationLabel } from "@/components/content/ContentLabFormV2";
import type { ResultV2 } from "@/components/content/ResultCardV2";

interface GenerateImageResponse {
  id: string;
  content_type: string;
  generated_text: string;
}

async function authHeaders(): Promise<HeadersInit> {
  const { data: { session } } = await supabase.auth.getSession();
  return { "Content-Type": "application/json", Authorization: `Bearer ${session?.access_token ?? ""}` };
}

function apiBase(): string {
  return import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
}

export interface GenerateImageInput {
  form: FormState;
  selectedLabels: VariationLabel[];
}

export function useGenerateImage() {
  return useMutation<ResultV2[], Error, GenerateImageInput>({
    mutationFn: async ({ form, selectedLabels }) => {
      const res = await fetch(`${apiBase()}/content-lab/generate-image`, {
        method: "POST",
        headers: await authHeaders(),
        body: JSON.stringify({
          prompt: form.topic,
          style: "realistic",
        }),
      });
      if (!res.ok) {
        const err = (await res.json().catch(() => ({}))) as { detail?: string };
        throw new Error(typeof err.detail === "string" ? err.detail : `HTTP ${res.status}`);
      }
      const data = (await res.json()) as GenerateImageResponse;
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
