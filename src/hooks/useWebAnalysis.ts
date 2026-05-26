import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useToast } from "@/hooks/use-toast";

export interface WebAnalysis {
  url: string | null;
  analyzed: boolean;
  title: string | null;
  meta_description: string | null;
  h1: string[];
  h2: string[];
  h3: string[];
  keywords: string[];
  score: number;
  recommendations: string[];
  cached: boolean;
  generated_at: string | null;
  message: string | null;
}

const key = (clientId: string) => ["intelligence", "web-analysis", clientId];

export function useWebAnalysis(clientId: string) {
  const qc = useQueryClient();
  const { toast } = useToast();

  const query = useQuery<WebAnalysis, Error>({
    queryKey: key(clientId),
    queryFn: () => apiGet<WebAnalysis>(`/intelligence/${clientId}/web-analysis`),
    enabled: !!clientId,
    staleTime: 60_000,
  });

  const mutation = useMutation<WebAnalysis, Error, void>({
    mutationFn: () =>
      apiGet<WebAnalysis>(`/intelligence/${clientId}/web-analysis?refresh=true`),
    onSuccess: (data) => {
      qc.setQueryData(key(clientId), data);
    },
    onError: (e) =>  // P1: el reanálisis fallido no queda mudo
      toast({ title: "No se pudo analizar el sitio", description: e.message, variant: "destructive" }),
  });

  return { query, reanalyze: mutation.mutate, isReanalyzing: mutation.isPending };
}
