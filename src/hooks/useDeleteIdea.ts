import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiDelete } from "@/lib/api-client";

// Fase C.3 · ⚠️ BORRADO PERMANENTE de una idea archivada (DELETE /used-ideas/{id} · irreversible).
// Invalida used_ideas → la idea desaparece de Archivadas. El confirm vive en DeleteIdeaButton.
export function useDeleteIdea() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id }: { id: string }) => apiDelete(`/strategies/used-ideas/${id}`),
    onSettled: () => qc.invalidateQueries({ queryKey: ["used_ideas"] }),
  });
}
