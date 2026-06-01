import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";

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
  // Switcher V1: scope al negocio activo · queryKey incluye el id → cache invalida al cambiar.
  const { activeBusinessId } = useActiveBusiness();
  return useQuery<BrandVoiceSummary, Error>({
    queryKey: ["brand-voice", "summary", activeBusinessId],
    queryFn: () => apiGet<BrandVoiceSummary>(
      `/brand-voice/summary${activeBusinessId ? `?client_id=${encodeURIComponent(activeBusinessId)}` : ""}`,
    ),
    staleTime: 60_000,
  });
}
