import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiPost } from "@/lib/api-client";

// Fase B.3 · registra el uso de UNA idea (POST /use-idea · idx + platform + brief). El backend
// inserta en strategy_idea_usages (idempotente) y flipea la estrategia a "used" si se usaron TODAS.
// Invalida strategies_list (contador/flip en Activas) + used_ideas (la idea aparece en Usadas).
interface IdeaUseInput { id: string; idea_idx: number; platform: string; brief: string; }

export function useRecordIdeaUse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, idea_idx, platform, brief }: IdeaUseInput) =>
      apiPost(`/strategies/${id}/use-idea`, { idea_idx, platform, brief }),
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["strategies_list"] });
      qc.invalidateQueries({ queryKey: ["used_ideas"] });
    },
  });
}
