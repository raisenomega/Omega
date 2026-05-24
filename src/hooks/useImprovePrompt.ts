import { useMutation } from "@tanstack/react-query";
import { apiPost } from "@/lib/api-client";

interface ImprovePromptResponse {
  improved_prompt: string;
}

export interface ImprovePromptInput {
  original_prompt: string;
  platform?: string;
  content_type?: string;
}

export function useImprovePrompt() {
  return useMutation<ImprovePromptResponse, Error, ImprovePromptInput>({
    mutationFn: (input) => apiPost<ImprovePromptResponse>(`/content-lab/improve-prompt`, input),
  });
}
