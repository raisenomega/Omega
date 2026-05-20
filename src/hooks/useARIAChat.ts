import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useMyPlanStatus } from "./useMyPlanStatus";
import { useClientPlanStatus } from "./useClientPlanStatus";
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

async function authHeaders(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession();
  return {
    "Content-Type": "application/json",
    ...(session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {}),
  };
}

export function useARIAChat() {
  const queryClient = useQueryClient();
  const myPlan = useMyPlanStatus();
  const planStatus = useClientPlanStatus(myPlan.clientId ?? "");
  const apiBase = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
  const ariaLevel = PLAN_TO_LEVEL[planStatus.planCode] ?? 1;

  const historyQuery = useQuery({
    queryKey: ["aria_history"],
    queryFn: async (): Promise<ARIAMessage[]> => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) return [];
      const res = await fetch(`${apiBase}/aria/history`, { headers: await authHeaders() });
      if (!res.ok) throw new Error(`history HTTP ${res.status}`);
      const data = await res.json();
      return data.messages ?? [];
    },
    enabled: !myPlan.loading,
  });

  const sendMutation = useMutation({
    mutationFn: async (content: string): Promise<ARIAMessage> => {
      const res = await fetch(`${apiBase}/aria/message`, {
        method: "POST",
        headers: await authHeaders(),
        body: JSON.stringify({ content }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      return await res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["aria_history"] });
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
