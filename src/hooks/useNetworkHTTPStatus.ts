import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

export interface NetIssue { severity: string; check: string; detail: string; }
export interface HeadersCheck { final_url: string; present: Record<string, string>; missing: string[]; }
export interface TLSCheck {
  version?: string;
  cert_subject?: string | null;
  cert_issuer?: string | null;
  cert_expires_at?: string;
  days_until_expiry?: number;
  error?: string;
}
export interface RateLimitCheck { active: boolean; limit_per_minute: number; scope: string; exempt_prefixes: string[]; verified_by: string; }
export interface CorsCheck { evil_origin_acao: string | null; wildcard_detected: boolean; reflects_untrusted: boolean; error?: string; }

export interface NetworkScan {
  id: string;
  scanned_at: string;
  target_url: string;
  headers_check: HeadersCheck;
  tls_check: TLSCheck;
  rate_limit_check: RateLimitCheck | null;
  cors_check: CorsCheck | null;
  score: number;
  issues: NetIssue[];
  created_at: string;
}

export interface NetworkTarget { url: string; last_scan: NetworkScan | null; last_24h_avg_score: number | null; }
export interface NetworkHTTPStatus { targets: NetworkTarget[]; overall_score: number | null; coverage_note: string; }

export function useNetworkHTTPStatus() {
  return useQuery({
    queryKey: ["network-http"],
    queryFn: () => apiGet<NetworkHTTPStatus>("/sentinel/network-http/status"),
    refetchInterval: 60 * 1000,
  });
}
