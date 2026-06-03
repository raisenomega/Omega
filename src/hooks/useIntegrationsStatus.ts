import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

export interface IntIssue { severity: string; check: string; detail: string; }
export interface WebhooksCheck {
  event_count_24h: number;
  idempotency_enforced: boolean | null;
  stripe_liveness: string | null;
  liveness_checked_at: string | null;
  liveness_note: string | null;
}
export interface ConnectCheck { total_resellers: number; with_stripe_account: number; note: string; }
export interface OAuthPlatform { platform: string; count: number; connected: number; expiring_24h: number; expiring_7d: number; }
export interface OAuthCheck { total: number; expiring_24h: number; expiring_7d: number; per_platform: OAuthPlatform[]; }

export interface IntegrationsScan {
  id: string;
  scanned_at: string;
  stripe_webhooks_check: WebhooksCheck;
  stripe_connect_check: ConnectCheck;
  oauth_check: OAuthCheck;
  mcp_check: { covered_by: string; anthropic_health: string } | null;
  score: number;
  issues: IntIssue[];
  coverage_note: string | null;
  created_at: string;
}

export interface IntegrationsStatus { last_scan: IntegrationsScan | null; last_24h_avg_score: number | null; }

export function useIntegrationsStatus() {
  return useQuery({
    queryKey: ["integrations-status"],
    queryFn: () => apiGet<IntegrationsStatus>("/sentinel/integrations/status"),
    refetchInterval: 60 * 1000,
  });
}
