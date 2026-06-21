import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";

// DEBT-034 (Fase 1 · live-read): analytics REALES vía Zernio, scopeados por negocio activo.
// El backend (/intelligence/analytics) es honesto (regla cero-mocks): sin profile/cuentas →
// connected=false + arrays vacíos · NUNCA números inventados. dataDelay comunica el lag ~24-48h.

interface GrowthPoint { date: string; followers: number }
interface EngagementRow { platform: string; likes: number; comments: number; shares: number }
interface HeatmapCell { day: string; hour: number; value: number }
interface TopPost {
  id: string;
  title: string;
  platform: string;
  likes: number;
  comments: number;
  shares: number;
  engagement: number;
}

interface AnalyticsResponse {
  connected: boolean;
  growth: GrowthPoint[];
  engagement: EngagementRow[];
  heatmap: HeatmapCell[];
  total_followers: number | null;
  avg_engagement: number | null;
  posts: number;
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
    topPosts: [] as TopPost[], // Zernio no expone top-posts aún · seguimiento
    avgEngagement: (data?.avg_engagement ?? null) as number | null,
    totalFollowers: (data?.total_followers ?? null) as number | null,
    dataDelay: data?.data_delay ?? null,
  };
}
