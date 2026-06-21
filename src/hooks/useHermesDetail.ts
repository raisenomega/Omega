// HERMES Fase B · drill-down de una integración (derivado de mcp_health_log · sin tabla nueva).
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

export interface HermesIncident { started_at: string; recovered_at: string | null; last_failure_at: string; detail: string | null; }
export interface HermesTimelineRow { status: string; detail: string | null; last_use: string | null; checked_at: string; created_at: string; }
export interface HermesDetail { integration: string; timeline: HermesTimelineRow[]; incidents: HermesIncident[]; error?: string; }

export const useHermesDetail = (integration: string | null) =>
  useQuery({
    queryKey: ["hermes-detail", integration],
    queryFn: () => apiGet<HermesDetail>(`/security-dev/hermes/detail/${integration}`),
    enabled: !!integration,
    staleTime: 30 * 1000,
  });
