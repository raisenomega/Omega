import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useToast } from "@/hooks/use-toast";

export type GeoStatus = "appeared" | "partial" | "not_appeared" | "unknown";

export interface GeoCheck {
  status: GeoStatus;
  summary: string | null;
  tips: string[];
  queries: string[];
  analyzed: boolean;
  cached: boolean;
  generated_at: string | null;
  message: string | null;
}

const key = (clientId: string) => ["intelligence", "geo-check", clientId];

export function useGeoCheck(clientId: string) {
  const qc = useQueryClient();
  const { toast } = useToast();

  const query = useQuery<GeoCheck, Error>({
    queryKey: key(clientId),
    queryFn: () => apiGet<GeoCheck>(`/intelligence/${clientId}/geo-check`),
    enabled: !!clientId,
    staleTime: 60_000,
  });

  const mutation = useMutation<GeoCheck, Error, void>({
    mutationFn: () =>
      apiGet<GeoCheck>(`/intelligence/${clientId}/geo-check?refresh=true`),
    onSuccess: (data) => {
      qc.setQueryData(key(clientId), data);
    },
    onError: (e) =>  // P1: el re-chequeo fallido no queda mudo
      toast({ title: "No se pudo verificar la visibilidad en IA", description: e.message, variant: "destructive" }),
  });

  return { query, recheck: mutation.mutate, isRechecking: mutation.isPending };
}
