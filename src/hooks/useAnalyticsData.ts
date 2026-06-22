import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import type { EngagementSeriesPoint, PostsSeriesPoint } from "@/lib/analytics-series";

// DEBT-034 ("paridad de verdad" · live-read): analytics REALES vía Zernio, resueltos por profileId.
// Backend honesto (regla GLOBAL cero-sintéticos): sin profileId → connected=false + vacíos · NUNCA números
// inventados. Seguidores/reach = snapshot real · ER = histórico (Σinter/Σreach · — si reach=0) · best_hour
// derivado. Series (engagement/posts) ACUMULADO: la API no tiene ventana (NO "del período").

interface GrowthPoint { date: string; followers: number }
interface EngagementRow { platform: string; likes: number; comments: number; shares: number; saves: number; views: number; reach: number }
interface HeatmapCell { day: string; hour: number; value: number }

interface AnalyticsResponse {
  connected: boolean;
  growth: GrowthPoint[];
  engagement: EngagementRow[];
  engagement_series: EngagementSeriesPoint[];
  posts_series: PostsSeriesPoint[];
  heatmap: HeatmapCell[];
  total_followers: number | null;
  total_reach: number | null;
  profile_engagement: number | null;
  best_hour: string | null;
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
    engagementSeries: (data?.engagement_series ?? []) as EngagementSeriesPoint[],
    postsSeries: (data?.posts_series ?? []) as PostsSeriesPoint[],
    heatmapData: (data?.heatmap ?? []) as HeatmapCell[],
    totalFollowers: (data?.total_followers ?? null) as number | null,
    totalReach: (data?.total_reach ?? null) as number | null,
    profileEngagement: (data?.profile_engagement ?? null) as number | null,
    bestHour: data?.best_hour ?? null,
  };
}
