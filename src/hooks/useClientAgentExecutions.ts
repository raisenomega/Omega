// DEBT-053 · Posts Tab · historial de ejecuciones de agentes por cliente.
// Lee agent_executions (migración 00032) con RLS client-scoped y enriquece
// agent_id → nombre amigable vía tabla agents.
// Patrón: useQuery + supabase.from · idéntico a useClientActiveAgents / useClientPlanStatus.

import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

// ── Forma canónica de una fila de agent_executions ─────────────────────────
export interface AgentExecution {
  id: string;
  agent_id: string;
  agentName: string;          // resuelto desde agents.name (o agent_id como fallback)
  status: string;
  triggered_by: string;
  started_at: string | null;
  completed_at: string | null;
  execution_time_ms: number | null;
  created_at: string;
}

// ── Agrupación por agente (para la vista de timeline) ─────────────────────
export interface AgentExecutionGroup {
  agent_id: string;
  agentName: string;
  totalCount: number;
  completedCount: number;
  failedCount: number;
  lastExecution: string;      // ISO string de la más reciente
  executions: AgentExecution[];
}

// ── Narrow seguro desde unknown ────────────────────────────────────────────
interface RawExecution {
  id: string;
  agent_id: string;
  status: string;
  triggered_by: string;
  started_at: string | null;
  completed_at: string | null;
  execution_time_ms: number | null;
  created_at: string;
}

function parseRaw(row: unknown): RawExecution | null {
  if (typeof row !== "object" || row === null) return null;
  const r = row as Record<string, unknown>;
  if (typeof r.id !== "string") return null;
  if (typeof r.agent_id !== "string") return null;
  if (typeof r.status !== "string") return null;
  if (typeof r.triggered_by !== "string") return null;
  if (typeof r.created_at !== "string") return null;
  return {
    id: r.id,
    agent_id: r.agent_id,
    status: r.status,
    triggered_by: r.triggered_by,
    started_at: typeof r.started_at === "string" ? r.started_at : null,
    completed_at: typeof r.completed_at === "string" ? r.completed_at : null,
    execution_time_ms: typeof r.execution_time_ms === "number" ? r.execution_time_ms : null,
    created_at: r.created_at,
  };
}

// ── Hook principal ─────────────────────────────────────────────────────────
export function useClientAgentExecutions(clientId: string): {
  groups: AgentExecutionGroup[];
  totalExecutions: number;
  isLoading: boolean;
  isError: boolean;
} {
  // 1. Fetch executions for this client (RLS enforces client ownership)
  const executionsQuery = useQuery({
    queryKey: ["agent_executions", "client", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("agent_executions")
        .select("id, agent_id, status, triggered_by, started_at, completed_at, execution_time_ms, created_at")
        .eq("client_id", clientId)
        .eq("is_active", true)
        .order("created_at", { ascending: false })
        .limit(200);
      if (error) throw error;
      return (data ?? []) as unknown[];
    },
    enabled: !!clientId,
  });

  // 2. Fetch agent names to resolve agent_id → friendly name
  const agentsQuery = useQuery({
    queryKey: ["agents", "names"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("agents")
        .select("code, name")
        .eq("is_active", true);
      if (error) throw error;
      return (data ?? []) as { code: string; name: string }[];
    },
    staleTime: 5 * 60 * 1000, // agent names rarely change · 5-min cache
  });

  const agentNameMap = new Map<string, string>(
    (agentsQuery.data ?? []).map((a) => [a.code, a.name])
  );

  const rawRows = (executionsQuery.data ?? []).flatMap((row) => {
    const parsed = parseRaw(row);
    return parsed ? [parsed] : [];
  });

  // Enrich with friendly agent name
  const executions: AgentExecution[] = rawRows.map((r) => ({
    ...r,
    agentName: agentNameMap.get(r.agent_id) ?? r.agent_id,
  }));

  // Group by agent_id
  const groupMap = new Map<string, AgentExecutionGroup>();
  for (const exec of executions) {
    let group = groupMap.get(exec.agent_id);
    if (!group) {
      group = {
        agent_id: exec.agent_id,
        agentName: exec.agentName,
        totalCount: 0,
        completedCount: 0,
        failedCount: 0,
        lastExecution: exec.created_at,
        executions: [],
      };
      groupMap.set(exec.agent_id, group);
    }
    group.totalCount += 1;
    if (exec.status === "completed") group.completedCount += 1;
    if (exec.status === "failed") group.failedCount += 1;
    // executions already ordered DESC → first is most recent per agent
    if (exec.created_at > group.lastExecution) group.lastExecution = exec.created_at;
    group.executions.push(exec);
  }

  // Sort groups by most recent execution first
  const groups = Array.from(groupMap.values()).sort(
    (a, b) => new Date(b.lastExecution).getTime() - new Date(a.lastExecution).getTime()
  );

  return {
    groups,
    totalExecutions: executions.length,
    isLoading: executionsQuery.isLoading || agentsQuery.isLoading,
    isError: executionsQuery.isError || agentsQuery.isError,
  };
}
