import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useToast } from "@/hooks/use-toast";

export interface AeoCheck {
  analyzed: boolean;
  questions: string[];
  answered: string[];
  gaps: string[];
  tips: string[];
  cached: boolean;
  generated_at: string | null;
  message: string | null;
}

const key = (clientId: string) => ["intelligence", "aeo-check", clientId];

export function useAeoCheck(clientId: string) {
  const qc = useQueryClient();
  const { toast } = useToast();

  const query = useQuery<AeoCheck, Error>({
    queryKey: key(clientId),
    queryFn: () => apiGet<AeoCheck>(`/intelligence/${clientId}/aeo-check`),
    enabled: !!clientId,
    staleTime: 60_000,
  });

  const mutation = useMutation<AeoCheck, Error, void>({
    mutationFn: () =>
      apiGet<AeoCheck>(`/intelligence/${clientId}/aeo-check?refresh=true`),
    onSuccess: (data) => {
      qc.setQueryData(key(clientId), data);
    },
    onError: (e) =>  // P1: el re-análisis fallido no queda mudo
      toast({ title: "No se pudieron analizar las preguntas", description: e.message, variant: "destructive" }),
  });

  return { query, recheck: mutation.mutate, isRechecking: mutation.isPending };
}
