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
  media_urls: string[] | null;
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
    mutationFn: (id: string) => apiPatch<{ scheduled: { scheduled_for: string; falta_cuenta: boolean } | null }>(
      `/content/${id}/save`, { is_saved: true }),
    onSuccess: (r) => {
      invalidate();
      // P2: toast honesto · refleja lo que REALMENTE pasó (no "se publicará")
      if (r?.scheduled) {
        const fecha = String(r.scheduled.scheduled_for).slice(0, 16).replace("T", " ");
        const aviso = r.scheduled.falta_cuenta ? " · falta conectar una cuenta para publicarlo" : "";
        toast({ title: `Aprobado · agendado para ${fecha}${aviso}` });
      } else {
        toast({ title: "Aprobado · agendalo en el Calendario cuando quieras" });
      }
    },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  const reject = useMutation({
    mutationFn: (id: string) => apiPatch(`/content/supervisado/${id}/reject`, {}),
    onSuccess: () => { invalidate(); toast({ title: "Rechazado · ARIA aprende" }); },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  // P1: la foto va a media_urls · generated_text (caption+hashtags) NO se toca.
  const attachPhoto = useMutation({
    mutationFn: ({ id, url }: { id: string; url: string }) =>
      apiPatch(`/content/${id}/media`, { media_urls: [url] }),
    onSuccess: () => { invalidate(); toast({ title: "Foto agregada al borrador" }); },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });

  return {
    items: query.data?.items ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
    approve,
    reject,
    attachPhoto,
  };
}
