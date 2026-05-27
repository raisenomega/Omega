import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

// Centro de Inteligencia Fase 2 · chip Google. GET /intelligence/chips/google devuelve
// métricas REALES del cliente (sessions/clicks/impressions) leídas con su token OAuth, o
// connected=false + message si no conectó. Cero mocks: metrics es null salvo datos reales.
export interface GoogleChipMetrics {
  sessions?: number;
  clicks?: number;
  impressions?: number;
}

export interface GoogleChipResponse {
  connected: boolean;
  metrics: GoogleChipMetrics | null;
  message: string | null;
}

const KEY = ["intelligence", "chip", "google"];

export function useGoogleChip() {
  return useQuery<GoogleChipResponse, Error>({
    queryKey: KEY,
    queryFn: () => apiGet<GoogleChipResponse>(`/intelligence/chips/google`),
    staleTime: 60_000,
  });
}
