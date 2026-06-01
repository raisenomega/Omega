import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";

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

export function useMetaChip() {
  // Switcher V1: scope al negocio activo · queryKey incluye el id → cache invalida al cambiar.
  const { activeBusinessId } = useActiveBusiness();
  return useQuery<ChipResponse, Error>({
    queryKey: ["intelligence", "chip", "meta", activeBusinessId],
    queryFn: () => apiGet<ChipResponse>(
      `/intelligence/chips/meta${activeBusinessId ? `?client_id=${encodeURIComponent(activeBusinessId)}` : ""}`,
    ),
    staleTime: 60_000,
  });
}
