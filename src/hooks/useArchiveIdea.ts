import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiPatch } from "@/lib/api-client";

// Fase C.2 · archiva UNA idea usada (PATCH /used-ideas/{id}/archive · setea archived_at). Invalida
// used_ideas (ambos filtros: la idea sale de Usadas y entra a Archivadas sin recargar la pagina).
export function useArchiveIdea() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id }: { id: string }) => apiPatch(`/strategies/used-ideas/${id}/archive`, {}),
    onSettled: () => qc.invalidateQueries({ queryKey: ["used_ideas"] }),
  });
}
