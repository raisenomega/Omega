import { useState } from "react";
import { Loader2, TrendingUp, Heart, Clock } from "lucide-react";
import { useAnalyticsData } from "@/hooks/useAnalyticsData";
import { useDashboardData } from "@/hooks/useDashboardData";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { GrowthChart } from "@/components/analytics/GrowthChart";
import { EngagementChart } from "@/components/analytics/EngagementChart";
import { ScheduleHeatmap } from "@/components/analytics/ScheduleHeatmap";
import { TopPostsTable } from "@/components/analytics/TopPostsTable";
import { AnalyticsFilters } from "@/components/analytics/AnalyticsFilters";

export default function Analytics() {
  const [selectedClient, setSelectedClient] = useState("all");
  const [dateRange, setDateRange] = useState<{ from: Date | undefined; to: Date | undefined }>({
    from: undefined,
    to: undefined,
  });

  const { loading, growthData, engagementData, heatmapData, topPosts, avgEngagement, totalFollowers } =
    useAnalyticsData();
  const { clients } = useDashboardData();

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-display font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">Métricas y reportes de rendimiento</p>
      </div>

      <AnalyticsFilters
        clients={clients.map((c) => ({ id: c.id, name: c.name }))}
        selectedClient={selectedClient}
        onClientChange={setSelectedClient}
        dateRange={dateRange}
        onDateRangeChange={setDateRange}
      />

      {/* KPI row */}
      <div className="grid gap-4 sm:grid-cols-3">
        <StatsCard
          title="Seguidores Totales"
          value={totalFollowers.toLocaleString()}
          icon={TrendingUp}
          subtitle="Todas las plataformas"
        />
        <StatsCard
          title="Engagement Promedio"
          value={`${avgEngagement}%`}
          icon={Heart}
          subtitle="Likes + comentarios + shares"
        />
        <StatsCard
          title="Mejor Horario"
          value="19:00 – 21:00"
          icon={Clock}
          subtitle="Mayor interacción"
        />
      </div>

      {/* Charts row */}
      <div className="grid gap-4 lg:grid-cols-2">
        <GrowthChart data={growthData} />
        <EngagementChart data={engagementData} />
      </div>

      {/* Heatmap */}
      <ScheduleHeatmap data={heatmapData} />

      {/* Top Posts */}
      <TopPostsTable posts={topPosts} />
    </div>
  );
}
