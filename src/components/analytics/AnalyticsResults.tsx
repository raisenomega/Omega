import { AnalyticsKPIs } from "@/components/analytics/AnalyticsKPIs";
import { GrowthChart } from "@/components/analytics/GrowthChart";
import { EngagementChart } from "@/components/analytics/EngagementChart";
import { EngagementOverTimeChart } from "@/components/analytics/EngagementOverTimeChart";
import { PostsOverTimeChart } from "@/components/analytics/PostsOverTimeChart";
import { BestTimesHeatmap } from "@/components/analytics/BestTimesHeatmap";
import type { EngagementSeriesPoint, PostsSeriesPoint } from "@/lib/analytics-series";

interface EngagementRow { platform: string; likes: number; comments: number; shares: number; saves: number; views: number; reach: number }

interface AnalyticsResultsProps {
  growthData: { date: string; followers: number }[];
  engagementData: EngagementRow[];
  engagementSeries: EngagementSeriesPoint[];
  postsSeries: PostsSeriesPoint[];
  heatmapData: { day: string; hour: number; value: number }[];
  totalFollowers: number | null;
  totalReach: number | null;
  profileEngagement: number | null;
  bestHour: string | null;
}

// Región de resultados del panel (extraída de Analytics.tsx por C4 · la página queda de gating/estados).
// Todo ACUMULADO · empty honesto por componente (— / [] / empty state · nunca 0 inventado).
export function AnalyticsResults(p: AnalyticsResultsProps) {
  return (
    <>
      <AnalyticsKPIs
        followers={p.totalFollowers}
        totalReach={p.totalReach}
        profileEngagement={p.profileEngagement}
        bestHour={p.bestHour}
      />
      <div className="grid gap-3 lg:grid-cols-2">
        <GrowthChart data={p.growthData} />
        <EngagementChart data={p.engagementData} />
      </div>
      <div className="grid gap-3 lg:grid-cols-2">
        <EngagementOverTimeChart data={p.engagementSeries} />
        <PostsOverTimeChart data={p.postsSeries} />
      </div>
      <BestTimesHeatmap data={p.heatmapData} />
    </>
  );
}
