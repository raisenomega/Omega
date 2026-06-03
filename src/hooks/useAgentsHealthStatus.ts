import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { apiGet, apiPost } from "@/lib/api-client";

export interface AgentHealth {
  agent_code: string;
  calls_24h: number;
  success_rate: number | null;
  avg_latency_ms: number | null;
  was_correct_null_pct_30d: number | null;
  accuracy_30d: number | null;
  model_recent: string | null;
}

export interface AgentsHealthScan {
  scanned_at: string | null;
  per_agent: AgentHealth[];
  model_drift_alerts: { agent: string; expected: string; actual: string }[];
  total_daily_cost_usd: number | null;
  cost_calculation_source: string | null;
  score: number;
  coverage_note: string | null;
}

export interface AgentsHealthStatus {
  last_scan: AgentsHealthScan | null;
  summary: {
    total_agents_monitored: number;
    agents_with_issues: number;
    total_calls_24h: number;
    avg_success_rate: number | null;
  };
}

export function useAgentsHealthStatus() {
  return useQuery({
    queryKey: ["agents-health"],
    queryFn: () => apiGet<AgentsHealthStatus>("/sentinel/agents-health/status"),
    refetchInterval: 60 * 1000,
  });
}

export function useTriggerAgentsHealth() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: () => apiPost<{ agents: number }>("/sentinel/agents-health/trigger", {}),
    onSuccess: (r) => {
      toast({ title: "Scan de agentes completado", description: `${r.agents} agentes evaluados.` });
      qc.invalidateQueries({ queryKey: ["agents-health"] });
    },
    onError: (e: unknown) =>
      toast({ variant: "destructive", title: "Scan falló", description: e instanceof Error ? e.message : "Error" }),
  });
}
