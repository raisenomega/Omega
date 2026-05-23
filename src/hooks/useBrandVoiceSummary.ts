import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

export interface CorpusEntry {
  text: string;
  platform: string | null;
  created_at: string;
}

export interface KeywordCount {
  keyword: string;
  count: number;
}

export interface BrandVoiceSummary {
  corpus_count: number;
  latest_approvals: CorpusEntry[];
  top_keywords: KeywordCount[];
}

export function useBrandVoiceSummary() {
  return useQuery<BrandVoiceSummary, Error>({
    queryKey: ["brand-voice", "summary"],
    queryFn: () => apiGet<BrandVoiceSummary>("/brand-voice/summary"),
    staleTime: 60_000,
  });
}
