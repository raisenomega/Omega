// DEBT-097 · Modo Supervisado · cola de drafts pendientes de aprobación POR negocio.
// Lee del backend GET /content/supervisado/pending (ya filtra status=draft +
// metadata.supervisado=true + ownership). Aprobar reusa PATCH /content/{id}/save
// (draft->approved dispara el aprendizaje ARIA ya cableado). Rechazar: PATCH reject.

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPatch } from "@/lib/api-client";
import { useToast } from "./use-toast";

export interface SupervisedDraft {
  id: string;
  client_id: string;
  agent_code: string | null;
  content_type: string | null;
  generated_text: string | null;
  confidence: number | null;
  created_at: string;
}

interface PendingResult {
  items: SupervisedDraft[];
}

export function useSupervisedQueue(clientId: string) {
  const qc = useQueryClient();
  const { toast } = useToast();
  const queryKey = ["supervised_queue", clientId];

  const query = useQuery<PendingResult>({
    queryKey,
    queryFn: () => apiGet<PendingResult>(`/content/supervisado/pending?client_id=${clientId}`),
    enabled: !!clientId,
    retry: 1,
  });

  const invalidate = () => qc.invalidateQueries({ queryKey });

  const approve = useMutation({
    mutationFn: (id: string) => apiPatch(`/content/${id}/save`, { is_saved: true }),
    onSuccess: () => { invalidate(); toast({ title: "Aprobado · se publicará" }); },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  const reject = useMutation({
    mutationFn: (id: string) => apiPatch(`/content/supervisado/${id}/reject`, {}),
    onSuccess: () => { invalidate(); toast({ title: "Rechazado · ARIA aprende" }); },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  return {
    items: query.data?.items ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
    approve,
    reject,
  };
}
