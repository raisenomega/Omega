import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

// Centro de Inteligencia Fase 2 · chip Meta. GET /intelligence/chips/meta devuelve
// métricas REALES del cliente (followers/engagement/reach) leídas con su token OAuth, o
// connected=false + message si no conectó. Cero mocks: metrics es null salvo datos reales.
export interface ChipMetrics {
  followers?: number;
  engagement?: number;
  reach?: number;
}

export interface ChipResponse {
  connected: boolean;
  metrics: ChipMetrics | null;
  message: string | null;
}

const KEY = ["intelligence", "chip", "meta"];

export function useMetaChip() {
  return useQuery<ChipResponse, Error>({
    queryKey: KEY,
    queryFn: () => apiGet<ChipResponse>(`/intelligence/chips/meta`),
    staleTime: 60_000,
  });
}
