import { useDashboardData } from "./useDashboardData";

// P1 strict (DDD): cero datos sintéticos en dashboards.
// DEBT-034: cuando llegue sync Meta API real (Fase 3), poblar growthData/
// engagementData/heatmapData con datos reales. Hoy: arrays vacíos · cada
// componente Analytics renderiza empty state.

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

export function useAnalyticsData() {
  const { loading } = useDashboardData();
  return {
    loading,
    growthData: [] as GrowthPoint[],
    engagementData: [] as EngagementRow[],
    heatmapData: [] as HeatmapCell[],
    topPosts: [] as TopPost[],
    avgEngagement: null as number | null,
    totalFollowers: null as number | null,
  };
}
