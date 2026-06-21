import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";

// DEBT-034 ("paridad de verdad" · live-read): analytics REALES vía Zernio, scopeados por negocio activo.
// Backend honesto (regla GLOBAL cero-sintéticos): sin profile/cuentas → connected=false + vacíos · NUNCA
// números inventados. Seguidores = snapshot real · posts = conteo real · best_hour = derivado · SIN %.

interface GrowthPoint { date: string; followers: number }
interface EngagementRow { platform: string; likes: number; comments: number; shares: number; saves: number; views: number }
interface HeatmapCell { day: string; hour: number; value: number }

interface AnalyticsResponse {
  connected: boolean;
  growth: GrowthPoint[];
  engagement: EngagementRow[];
  heatmap: HeatmapCell[];
  total_followers: number | null;
  posts: number;
  best_hour: string | null;
  data_delay: string | null;
  message: string | null;
}

export function useAnalyticsData() {
  const { activeBusinessId } = useActiveBusiness();
  const { data, isLoading } = useQuery<AnalyticsResponse>({
    queryKey: ["analytics-social", activeBusinessId],
    queryFn: () => apiGet<AnalyticsResponse>(`/intelligence/analytics?client_id=${activeBusinessId}`),
    enabled: !!activeBusinessId,
    staleTime: 5 * 60_000, // dato de 24-48h · no recargar seguido
  });
  return {
    loading: isLoading,
    growthData: (data?.growth ?? []) as GrowthPoint[],
    engagementData: (data?.engagement ?? []) as EngagementRow[],
    heatmapData: (data?.heatmap ?? []) as HeatmapCell[],
    totalFollowers: (data?.total_followers ?? null) as number | null,
    posts: (data?.posts ?? null) as number | null, // total histórico de la cuenta (NO del período)
    bestHour: data?.best_hour ?? null,
    dataDelay: data?.data_delay ?? null,
  };
}
