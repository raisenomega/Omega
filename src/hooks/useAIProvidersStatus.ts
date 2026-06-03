import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

export interface ProviderStats {
  total_calls: number;
  success: number;
  failed: number;
  success_rate: number | null;
  avg_latency_ms: number | null;
  failover_triggered_count: number;
}

export interface AIProvider {
  name: string;
  configured: boolean;
  reason_not_configured: string | null;
  circuit_state: string;
  consecutive_failures: number;
  last_24h: ProviderStats;
}

export interface LegacyPath {
  name: string;
  debt: string;
  callers_count: number;
}

export interface AIProvidersStatus {
  providers: AIProvider[];
  coverage_summary: { canonical_path_covered: boolean; legacy_paths_uncovered: LegacyPath[] };
  pct_calls_covered_by_router: number | null;
  coverage_percentage_unknown: boolean;
  total_router_calls_24h: number;
}

export function useAIProvidersStatus() {
  return useQuery({
    queryKey: ["ai-providers"],
    queryFn: () => apiGet<AIProvidersStatus>("/sentinel/ai-providers/status"),
    refetchInterval: 30 * 1000,
  });
}
