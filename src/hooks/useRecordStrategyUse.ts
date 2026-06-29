import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiPost } from "@/lib/api-client";

// ARCO MEDICION CAPA 1 · POST /strategies/{id}/use · registra el uso (last_used) de una estrategia.
// mark_used=true → la estrategia pasa a "Usadas". Tras el uso invalida ["strategies_list"] para que
// la vista se refresque (la estrategia aparezca en Usadas). best-effort: los callers no awaitean → la
// navegacion a Content Lab nunca se bloquea por un fallo de /use (el error queda en el estado del mutation).
interface UseInput {
  id: string;
  platform: string;
  brief: string;
  mark_used: boolean;
}

export function useRecordStrategyUse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, platform, brief, mark_used }: UseInput) =>
      apiPost(`/strategies/${id}/use`, { platform, brief, mark_used }),
    onSettled: () => qc.invalidateQueries({ queryKey: ["strategies_list"] }),
  });
}
