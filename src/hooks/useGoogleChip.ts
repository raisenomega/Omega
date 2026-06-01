import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";

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

export function useGoogleChip() {
  // Switcher V1: scope al negocio activo · queryKey incluye el id → cache invalida al cambiar.
  const { activeBusinessId } = useActiveBusiness();
  return useQuery<GoogleChipResponse, Error>({
    queryKey: ["intelligence", "chip", "google", activeBusinessId],
    queryFn: () => apiGet<GoogleChipResponse>(
      `/intelligence/chips/google${activeBusinessId ? `?client_id=${encodeURIComponent(activeBusinessId)}` : ""}`,
    ),
    staleTime: 60_000,
  });
}
