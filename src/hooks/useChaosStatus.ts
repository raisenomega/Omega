import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { apiGet, apiPost } from "@/lib/api-client";

export interface ChaosIssue { severity: string; check: string; detail: string; }
export interface ChaosScenario {
  id: string;
  scenario: string;
  result: "passed" | "partial" | "failed" | "skipped";
  recovery_time_ms: number | null;
  graceful_degradation: boolean | null;
  issues: ChaosIssue[];
  scanned_at: string;
}
export interface ChaosStatus {
  last_scanned_at: string | null;
  score: number | null;
  scenarios: ChaosScenario[];
  history: { scanned_at: string; score: number }[];
  coverage_note: string;
}

export function useChaosStatus() {
  return useQuery({
    queryKey: ["chaos-status"],
    queryFn: () => apiGet<ChaosStatus>("/sentinel/chaos/status"),
    refetchInterval: 60 * 1000,
  });
}

export function useTriggerChaos() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: (scenarios?: string[]) => apiPost<{ score: number; scenarios: number }>("/sentinel/chaos/trigger", { scenarios }),
    onSuccess: (r) => {
      toast({ title: "Chaos test completado", description: `Score ${r.score} · ${r.scenarios} escenarios.` });
      qc.invalidateQueries({ queryKey: ["chaos-status"] });
      qc.invalidateQueries({ queryKey: ["sentinel-issues"] });
    },
    onError: (e: unknown) =>
      toast({ variant: "destructive", title: "Chaos test falló", description: e instanceof Error ? e.message : "Error" }),
  });
}
