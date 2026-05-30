import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPost, apiPatch } from "@/lib/api-client";
import { useToast } from "./use-toast";

export interface Strategy {
  id: string;
  titulo: string;
  tipo: string;
  contenido: {
    resumen?: string;
    pilares?: string[];
    posts_sugeridos?: { plataforma: string; idea: string }[];
  };
  estado: string;
  created_at: string;
}

interface ListResult { items: Strategy[]; cadence?: string | null }

export function useStrategiesList(estado: "active" | "archived") {
  return useQuery<ListResult>({
    queryKey: ["strategies_list", estado],
    queryFn: () => apiGet<ListResult>(`/strategies/?estado=${estado}`),
    retry: 1,
  });
}

export function useGenerateStrategy() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: () => apiPost<Strategy>(`/strategies/generate`, {}),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["strategies_list"] });
      toast({ title: "Estrategia generada" });
    },
    onError: (e: Error) => toast({ title: "No se pudo generar", description: e.message, variant: "destructive" }),
  });
}

export function useSetStrategyStatus() {
  const qc = useQueryClient();
  const { toast } = useToast();
  return useMutation({
    mutationFn: ({ id, estado }: { id: string; estado: "archived" | "used" }) =>
      apiPatch(`/strategies/${id}/status`, { estado }),
    onSuccess: (_r, vars) => {
      qc.invalidateQueries({ queryKey: ["strategies_list"] });
      if (vars.estado === "archived") toast({ title: "Estrategia archivada" });
    },
    onError: (e: Error) => toast({ title: "Error", description: e.message, variant: "destructive" }),
  });
}
