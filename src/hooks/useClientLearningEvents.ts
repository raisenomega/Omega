// DEBT-102 · Widget per-cliente · lee agent_memory (RLS) SOLO evaluados
// (was_correct IS NOT NULL · pendientes aparte · P1). Agregación pura en
// learning-events-data.ts · molde useClientAgentExecutions (DEBT-053).

import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { buildLearningEvents } from "@/hooks/learning-events-data";
import type { LearningEvent } from "@/hooks/learning-events-data";

export type { LearningEvent } from "@/hooks/learning-events-data";

export function useClientLearningEvents(clientId: string): {
  events: LearningEvent[];
  correctCount: number;
  incorrectCount: number;
  pendingCount: number;
  accuracy: number | null;
  isLoading: boolean;
  isError: boolean;
} {
  const evaluatedQuery = useQuery({
    queryKey: ["learning_events", "client", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("agent_memory")
        .select("id, agent_code, decision, outcome, was_correct, confidence, evaluated_at")
        .eq("client_id", clientId)
        .not("was_correct", "is", null)
        .order("evaluated_at", { ascending: false })
        .limit(100);
      if (error) throw error;
      return (data ?? []) as unknown[];
    },
    enabled: !!clientId,
  });

  const pendingQuery = useQuery({
    queryKey: ["learning_events", "pending", clientId],
    queryFn: async () => {
      const { count, error } = await supabase
        .from("agent_memory")
        .select("id", { count: "exact", head: true })
        .eq("client_id", clientId)
        .is("was_correct", null);
      if (error) throw error;
      return count ?? 0;
    },
    enabled: !!clientId,
  });

  const agentsQuery = useQuery({
    queryKey: ["agents", "names"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("agents").select("code, name").eq("is_active", true);
      if (error) throw error;
      return (data ?? []) as { code: string; name: string }[];
    },
    staleTime: 5 * 60 * 1000,
  });
  const { events, correctCount, incorrectCount, accuracy } = buildLearningEvents(
    evaluatedQuery.data ?? [],
    agentsQuery.data ?? []
  );

  return {
    events,
    correctCount,
    incorrectCount,
    pendingCount: pendingQuery.data ?? 0,
    accuracy,
    isLoading: evaluatedQuery.isLoading || agentsQuery.isLoading,
    isError: evaluatedQuery.isError || agentsQuery.isError,
  };
}
