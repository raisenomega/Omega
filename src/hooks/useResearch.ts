import { useMutation } from "@tanstack/react-query";
import { apiPost } from "@/lib/api-client";

export interface ResearchResult {
  title: string;
  url: string;
  snippet: string;
}

export interface ResearchResponse {
  query: string;
  results: ResearchResult[];
  answer?: string | null;
  count: number;
  duration_ms: number;
}

interface ResearchInput {
  query: string;
  max_results?: number;
}

// Brave Search wrapper · cablea botón Research del form bar al backend
// /content-lab/research · usa BRAVE_API_KEY de Railway. Cero cache local V1.
export function useResearch() {
  return useMutation<ResearchResponse, Error, ResearchInput>({
    mutationFn: ({ query, max_results = 5 }) =>
      apiPost<ResearchResponse>(`/content-lab/research`, { query, max_results }),
  });
}
