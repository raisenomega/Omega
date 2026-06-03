import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { apiGet, apiPost } from "@/lib/api-client";

export interface RLSIssue {
  table: string;
  issue_type: string;
  severity: string;
  detail: string;
}

export interface RLSAudit {
  id: string;
  scanned_at: string | null;
  total_tables: number;
  total_issues: number;
  severity_critical: number;
  severity_high: number;
  severity_medium: number;
  issues: RLSIssue[];
  created_at: string;
}

export function useRLSAuditLatest() {
  return useQuery({
    queryKey: ["rls-audit"],
    queryFn: () => apiGet<{ latest: RLSAudit | null }>("/sentinel/rls-audit/latest"),
    refetchInterval: 5 * 60 * 1000,
  });
}

export function useTriggerRLSAudit() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: () => apiPost<{ total_issues: number }>("/sentinel/rls-audit/trigger", {}),
    onSuccess: (r) => {
      toast({ title: "Auditoría RLS completada", description: `${r.total_issues} issues detectados.` });
      qc.invalidateQueries({ queryKey: ["rls-audit"] });
    },
    onError: (e: unknown) =>
      toast({ variant: "destructive", title: "Auditoría falló", description: e instanceof Error ? e.message : "Error" }),
  });
}
