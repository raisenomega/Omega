import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

export interface RuntimeIssue { severity: string; check: string; detail: string; }

export interface RuntimeScan {
  scanned_at: string | null;
  window_minutes: number;
  backend_error_rate_pct: number | null;
  backend_exception_count: number;
  frontend_error_count: number;
  recurring_patterns: { source: string; sample: string; count: number }[];
  railway_5xx_count: number | null;
  score: number;
  issues: RuntimeIssue[];
}

export interface TopSignature { signature: string; message: string; count: number; }

export interface RuntimeStatus {
  last_scan: RuntimeScan | null;
  last_24h: { total_errors_backend: number; total_errors_frontend: number; top_signatures: TopSignature[] };
  coverage: { railway_api_active: boolean; reason: string };
}

export function useRuntimeStatus() {
  return useQuery({
    queryKey: ["runtime-status"],
    queryFn: () => apiGet<RuntimeStatus>("/sentinel/runtime/status"),
    refetchInterval: 30 * 1000,
  });
}
