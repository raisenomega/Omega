import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

export interface EndpointLatency { path: string; calls: number; p95: number; p99: number; max_status: number; }
export interface SlowQuery { query: string; calls: number; mean_ms: number; }

export interface PerformanceScan {
  scanned_at: string | null;
  window_minutes: number;
  p95_per_endpoint: EndpointLatency[];
  slow_queries: SlowQuery[];
  bundle_size_kb: number | null;
  memory_pct: number | null;
  cpu_pct: number | null;
  score: number;
  issues: { severity: string; check: string; detail: string }[];
}

export interface BuildStat { git_sha: string; bundle_size_kb: number; created_at: string; }

export interface PerformanceStatus {
  last_scan: PerformanceScan | null;
  last_24h: { top_5_slowest_endpoints_p95: EndpointLatency[]; bundle_size_trend: BuildStat[] };
  coverage: { pg_stat_statements_enabled: boolean; railway_metrics_active: boolean; last_build_age_hours: number | null };
}

export function usePerformanceStatus() {
  return useQuery({
    queryKey: ["performance-status"],
    queryFn: () => apiGet<PerformanceStatus>("/sentinel/performance/status"),
    refetchInterval: 30 * 1000,
  });
}
