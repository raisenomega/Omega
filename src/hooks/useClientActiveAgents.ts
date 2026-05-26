import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { AGENTS, type Agent } from "@/components/addons/_agents_data";

// Entry de add-on de agente dentro de client_plans.addons (jsonb).
// Convención de código: `agent_{id}` (ej. agent_publicador) · fallback por persona.
interface AddonEntry {
  addon_code: string;
  deactivated_at: string | null;
}

// Narrowing seguro desde unknown (addons puede ser null/[] o forma inesperada · cero any).
function parseAddons(raw: unknown): AddonEntry[] {
  if (!Array.isArray(raw)) return [];
  return raw.flatMap((item) => {
    if (typeof item !== "object" || item === null) return [];
    const rec = item as Record<string, unknown>;
    if (typeof rec.addon_code !== "string") return [];
    const deactivated = typeof rec.deactivated_at === "string" ? rec.deactivated_at : null;
    return [{ addon_code: rec.addon_code, deactivated_at: deactivated }];
  });
}

// agent_publicador → AGENTS.find(id === "publicador"); fallback agent_rex → persona "rex".
function resolveAgent(addonCode: string): Agent | undefined {
  const key = addonCode.slice("agent_".length).toLowerCase();
  return (
    AGENTS.find((a) => a.id.toLowerCase() === key) ??
    AGENTS.find((a) => a.persona.toLowerCase() === key)
  );
}

export function useClientActiveAgents(clientId: string): { agents: Agent[]; isLoading: boolean } {
  const { data, isLoading } = useQuery({
    queryKey: ["client_active_agents", clientId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("client_plans")
        .select("addons")
        .eq("client_id", clientId)
        .maybeSingle();
      if (error) throw error;
      return data;
    },
    enabled: !!clientId,
  });

  const agents = parseAddons(data?.addons)
    .filter((e) => e.addon_code.startsWith("agent_") && !e.deactivated_at)
    .map((e) => resolveAgent(e.addon_code))
    .filter((a): a is Agent => a !== undefined);

  return { agents, isLoading };
}
