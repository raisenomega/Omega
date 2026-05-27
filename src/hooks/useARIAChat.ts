import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useMyPlanStatus } from "./useMyPlanStatus";
import { useClientPlanStatus } from "./useClientPlanStatus";
import { useToast } from "@/hooks/use-toast";
import { ariaGet, ariaPost } from "@/lib/aria-fetch";
import type { PlanCode } from "@/lib/plan-limits";

// Mapping plan → ARIA level BASE (Q2=A · spec §6 ARIA_NOVA_INTELLIGENCE)
// adopcion→1 · basic→2 · pro→3 · enterprise→3 · nivel 4 = add-on ARIA Premium
// (DEBT-063: se lee del aria_level real del backend, no se deriva del plan).
const PLAN_TO_LEVEL: Record<PlanCode, number> = {
  adopcion: 1, basic: 2, pro: 3, enterprise: 3,
};

// DEBT-046: resellers default to ARIA level 3 (pro equivalent).
// Their clientId is null so useClientPlanStatus returns "adopcion" → level 1,
// which would incorrectly floor the resolved level below what they paid for.
const RESELLER_BASE_ARIA_LEVEL = 3;

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
  // DEBT-046: for reseller owners (isOwner=true, clientId=null) use the reseller base level
  // rather than falling through to "adopcion" (level 1) from the empty clientId path.
  const planLevel = myPlan.isOwner
    ? RESELLER_BASE_ARIA_LEVEL
    : (PLAN_TO_LEVEL[planStatus.planCode] ?? 1);

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

  // DEBT-063: el nivel REAL puede superar al del plan si el cliente pagó ARIA Premium
  // (add-on · aria_level=4 en DB · el backend lo reporta en cada ARIAMessage.aria_level).
  // Máximo plan↔backend → no mostrar "Actualizar" a quien ya pagó (evita doble cobro percibido).
  const messages = historyQuery.data ?? [];
  const backendLevel = messages.reduce((mx, m) => Math.max(mx, m.aria_level ?? 0), 0);
  const ariaLevel = Math.max(planLevel, backendLevel);

  return {
    messages,
    isLoadingHistory: historyQuery.isLoading,
    isSending: sendMutation.isPending,
    sendMessage: (content: string) => sendMutation.mutate(content),
    ariaLevel,
    error: sendMutation.error,
  };
}
