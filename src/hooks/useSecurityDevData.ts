// Datos operacionales de Security Dev vía backend (apiGet · gate require_super_owner).
// staleTime 30s: refrescan frecuente. Tipos alineados al esquema real (00022/00029):
// incidents usa detected_at · watchlist usa list_type (NO created_at/risk_level).
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

export interface DevHealth {
  e2b_api_key: boolean;
  railway_api_token: boolean;
  railway_project_id: boolean;
  github_token: boolean;
  all_ready: boolean;
}

export interface SentinelScore {
  id: string;
  score: number;
  security_score: number | null;
  architecture_score: number | null;
  performance_score: number | null;
  quality_score: number | null;
  deployment_score: number | null;
  documentation_score: number | null;
  verdict: string;
  issues_critical: number;
  issues_high: number;
  issues_medium: number;
  issues_low: number;
  auto_fixes_applied: number;
  calculated_at: string;
}

export interface SentinelData {
  latest: SentinelScore | null;
  history: SentinelScore[];
  count: number;
  error?: string;
}

// Per-agente (tabla sentinel_scans · /sentinel/history) · distinto del agregado sentinel_risk_scores.
export interface SentinelIssue { severity: string; type: string; message: string; }
export interface SentinelScan {
  id: string;
  agent_code: string;
  scan_type: string;
  status: string;
  security_score: number | null;
  issues: SentinelIssue[];
  deploy_decision: string | null;
  scan_duration_ms: number | null;
  triggered_by: string | null;
  created_at: string;
}
export interface SentinelHistoryData { total: number; scans: SentinelScan[]; }

export interface GuardianLog { id: string; event_type: string; ip_address: string | null; user_agent: string | null; risk_score: number; created_at: string; }
export interface GuardianIncident { id: string; incident_type: string; severity: string; status: string; detected_at: string; }
export interface GuardianWatch { id: string; ip_address: string; list_type: string; reason: string | null; created_at: string; }
export interface GuardianData { logs: GuardianLog[]; incidents: GuardianIncident[]; watchlist: GuardianWatch[]; error?: string; }

export interface HermesIntegration { integration: string; status: string; last_use: string | null; checked_at: string; created_at: string; }
export interface HermesData { integrations: HermesIntegration[]; count: number; error?: string; }

const STALE = 30 * 1000;

export const useHermesData = () =>
  useQuery({ queryKey: ["hermes-data"], queryFn: () => apiGet<HermesData>("/security-dev/hermes"), staleTime: STALE });

export const useDevHealth = () =>
  useQuery({ queryKey: ["dev-health"], queryFn: () => apiGet<DevHealth>("/security-dev/health"), staleTime: STALE });

export const useSentinelData = () =>
  useQuery({ queryKey: ["sentinel-data"], queryFn: () => apiGet<SentinelData>("/security-dev/sentinel"), staleTime: STALE });

export const useSentinelHistory = () =>
  useQuery({ queryKey: ["sentinel-history"], queryFn: () => apiGet<SentinelHistoryData>("/sentinel/history/"), staleTime: STALE });

export const useGuardianData = () =>
  useQuery({ queryKey: ["guardian-data"], queryFn: () => apiGet<GuardianData>("/security-dev/guardian"), staleTime: STALE });
