// DEBT-052 FASE 5 · AI Tab · estado de créditos prepagados del cliente.
// Lee client_agent_credits (saldo/budget/periodo/packs) + client_credit_ledger
// (consumo por agente) con RLS client-scoped. Enriquece agent_code → nombre vía agents.
// Excluye códigos internos (__admin_*, __auto_recharge__) del consumo por agente.
// Patrón: useQuery + supabase.from · idéntico a useClientAgentExecutions. Cero mocks.

import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export interface AgentConsumption {
  agentCode: string;
  agentName: string;
  totalUsd: number;
  count: number;
}

export interface ClientCredits {
  enrolled: boolean;
  budgetUsd: number;
  consumidoUsd: number;
  saldoUsd: number;
  pctUsed: number;
  periodoEnd: string | null;
  tier: string | null;
  autoRecharge: boolean;
  consumption: AgentConsumption[];
  isLoading: boolean;
  isError: boolean;
}

interface CreditsRow {
  budget_usd_mensual: number;
  consumido_usd: number;
  periodo_end: string | null;
  packs: unknown;
}

function num(v: unknown): number {
  return typeof v === "number" ? v : 0;
}

function activePack(packs: unknown): { tier: string | null; autoRecharge: boolean } {
  if (!Array.isArray(packs)) return { tier: null, autoRecharge: false };
  for (const p of packs) {
    if (p && typeof p === "object") {
      const o = p as Record<string, unknown>;
      if (o.deactivated_at == null && typeof o.tier === "string") {
        return { tier: o.tier, autoRecharge: o.auto_recharge === true };
      }
    }
  }
  return { tier: null, autoRecharge: false };
}

interface LedgerRow {
  agent_code: string;
  cost_usd: number;
}

function parseLedger(row: unknown): LedgerRow | null {
  if (typeof row !== "object" || row === null) return null;
  const r = row as Record<string, unknown>;
  if (typeof r.agent_code !== "string") return null;
  return { agent_code: r.agent_code, cost_usd: num(r.cost_usd) };
}

export function useClientCredits(clientId: string): ClientCredits {
  const creditsQuery = useQuery({
    queryKey: ["client_agent_credits", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("client_agent_credits")
        .select("budget_usd_mensual, consumido_usd, periodo_end, packs")
        .eq("client_id", clientId)
        .maybeSingle();
      if (error) throw error;
      return (data as CreditsRow | null) ?? null;
    },
    enabled: !!clientId,
  });

  const ledgerQuery = useQuery({
    queryKey: ["client_credit_ledger", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("client_credit_ledger")
        .select("agent_code, cost_usd, created_at")
        .eq("client_id", clientId)
        .order("created_at", { ascending: false })
        .limit(500);
      if (error) throw error;
      return (data ?? []) as unknown[];
    },
    enabled: !!clientId,
  });

  const agentsQuery = useQuery({
    queryKey: ["agents", "names"],
    queryFn: async () => {
      const { data, error } = await supabase.from("agents").select("code, name").eq("is_active", true);
      if (error) throw error;
      return (data ?? []) as { code: string; name: string }[];
    },
    staleTime: 5 * 60 * 1000,
  });

  const row = creditsQuery.data ?? null;
  const budgetUsd = num(row?.budget_usd_mensual);
  const consumidoUsd = num(row?.consumido_usd);
  const saldoUsd = Math.max(0, budgetUsd - consumidoUsd);
  const pctUsed = budgetUsd > 0 ? Math.min(100, Math.round((consumidoUsd / budgetUsd) * 100)) : 0;
  const { tier, autoRecharge } = activePack(row?.packs);

  const nameMap = new Map<string, string>((agentsQuery.data ?? []).map((a) => [a.code, a.name]));
  const consMap = new Map<string, AgentConsumption>();
  for (const raw of ledgerQuery.data ?? []) {
    const l = parseLedger(raw);
    if (!l || l.agent_code.startsWith("__")) continue; // excluye __admin_*/__auto_recharge__
    let c = consMap.get(l.agent_code);
    if (!c) {
      c = { agentCode: l.agent_code, agentName: nameMap.get(l.agent_code) ?? l.agent_code, totalUsd: 0, count: 0 };
      consMap.set(l.agent_code, c);
    }
    c.totalUsd += l.cost_usd;
    c.count += 1;
  }
  const consumption = Array.from(consMap.values()).sort((a, b) => b.totalUsd - a.totalUsd);

  return {
    enrolled: row !== null,
    budgetUsd,
    consumidoUsd,
    saldoUsd,
    pctUsed,
    periodoEnd: row?.periodo_end ?? null,
    tier,
    autoRecharge,
    consumption,
    isLoading: creditsQuery.isLoading || ledgerQuery.isLoading || agentsQuery.isLoading,
    isError: creditsQuery.isError || ledgerQuery.isError,
  };
}
