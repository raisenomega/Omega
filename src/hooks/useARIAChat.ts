import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useMyPlanStatus } from "./useMyPlanStatus";
import { useClientPlanStatus } from "./useClientPlanStatus";
import { useToast } from "@/hooks/use-toast";
import { ariaGet, ariaPost } from "@/lib/aria-fetch";
import type { PlanCode } from "@/lib/plan-limits";

// Mapping plan → ARIA level (Q2=A · spec §6 ARIA_NOVA_INTELLIGENCE)
// adopcion→1 · basic→2 · pro→3 · enterprise→3 (4 requiere add-ons activos · pending)
const PLAN_TO_LEVEL: Record<PlanCode, number> = {
  adopcion: 1, basic: 2, pro: 3, enterprise: 3,
};

export interface ARIAMessage {
  role: "user" | "assistant";
  content: string;
  aria_level?: number | null;
  created_at?: string;
}

interface HistoryResponse { messages: ARIAMessage[] }

// DEBT-CL-003 cerrada: cero authHeaders/apiBase duplicado · usa api-client
// como fuente única de truth para fetch wrappers + auth headers.
export function useARIAChat() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const myPlan = useMyPlanStatus();
  const planStatus = useClientPlanStatus(myPlan.clientId ?? "");
  const ariaLevel = PLAN_TO_LEVEL[planStatus.planCode] ?? 1;

  const historyQuery = useQuery({
    queryKey: ["aria_history"],
    queryFn: async (): Promise<ARIAMessage[]> => {
      const data = await ariaGet<HistoryResponse>(`/aria/history`);
      return data.messages ?? [];
    },
    enabled: !myPlan.loading,
  });

  const sendMutation = useMutation({
    mutationFn: (content: string): Promise<ARIAMessage> =>
      ariaPost<ARIAMessage>(`/aria/message`, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["aria_history"] });
    },
    onError: (e: unknown) => {  // fallo/abort visible → input no queda mudo (fix deadlock)
      toast({
        variant: "destructive",
        title: "ARIA no pudo responder",
        description: e instanceof Error ? e.message : "Error desconocido. Reintentá.",
      });
    },
  });

  return {
    messages: historyQuery.data ?? [],
    isLoadingHistory: historyQuery.isLoading,
    isSending: sendMutation.isPending,
    sendMessage: (content: string) => sendMutation.mutate(content),
    ariaLevel,
    error: sendMutation.error,
  };
}
