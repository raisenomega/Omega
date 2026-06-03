import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { apiPost } from "@/lib/api-client";
import { useSecurityDev } from "@/contexts/SecurityDevContext";

export interface IssueActionPayload {
  agent_code: string;
  severity: string;
  type: string;
  message: string;
  scan_id?: string | null;
  reason?: string;
}

interface FixResult { action_id: string; issue_hash: string; dispatch_prompt: string; }

// Ignorar (registra) y Fix (registra + precarga prompt en Dev Chat + navega al tab).
export function useSentinelIssueAction() {
  const qc = useQueryClient();
  const { toast } = useToast();
  const { setActiveTab, setPendingFixPrompt } = useSecurityDev();

  const ignoreMutation = useMutation({
    mutationFn: (p: IssueActionPayload) => apiPost("/sentinel/issues/ignore", p),
    onSuccess: () => {
      toast({ title: "Issue ignorado", description: "Seguirá visible con badge en futuros scans." });
      qc.invalidateQueries({ queryKey: ["sentinel-history"] });
    },
    onError: (e: unknown) =>
      toast({ variant: "destructive", title: "No se pudo ignorar", description: e instanceof Error ? e.message : "Error" }),
  });

  const fixMutation = useMutation({
    mutationFn: (p: IssueActionPayload): Promise<FixResult> => apiPost<FixResult>("/sentinel/issues/dispatch-fix", p),
    onSuccess: (r) => {
      setPendingFixPrompt(r.dispatch_prompt);
      setActiveTab("chat");
      toast({ title: "Fix despachado a Dev Chat" });
      qc.invalidateQueries({ queryKey: ["sentinel-history"] });
    },
    onError: (e: unknown) =>
      toast({ variant: "destructive", title: "No se pudo despachar el fix", description: e instanceof Error ? e.message : "Error" }),
  });

  return { ignoreMutation, fixMutation };
}
