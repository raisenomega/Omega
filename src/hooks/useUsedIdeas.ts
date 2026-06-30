import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

// Fase B · una fila por IDEA usada (strategy_idea_usages). strategies.titulo = de qué estrategia
// vino (embed B.1 · null si la estrategia fue borrada). El endpoint devuelve las ideas de TODOS los
// clientes accesibles → filtramos por el negocio activo (mismo patrón que Strategies.tsx con estrategias).
export interface UsedIdea {
  id: string;
  strategy_id: string;
  client_id: string;
  idea_idx: number;
  platform: string | null;
  brief: string | null;
  used_at: string;
  strategies: { titulo: string } | null;
}

interface UsedIdeasResult { items: UsedIdea[] }

export function useUsedIdeas(businessId: string | null) {
  return useQuery({
    queryKey: ["used_ideas", businessId],
    queryFn: () => apiGet<UsedIdeasResult>("/strategies/used-ideas"),
    enabled: !!businessId,
    select: (data): UsedIdea[] => (data.items ?? []).filter((i) => i.client_id === businessId),
    retry: 1,
  });
}
