import { useState } from "react";
import { Info, Loader2 } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAnalyticsData } from "@/hooks/useAnalyticsData";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { AnalyticsKPIs } from "@/components/analytics/AnalyticsKPIs";
import { GrowthChart } from "@/components/analytics/GrowthChart";
import { EngagementChart } from "@/components/analytics/EngagementChart";
import { BestTimesHeatmap } from "@/components/analytics/BestTimesHeatmap";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useProAccess } from "@/hooks/useProAccess";
import { ProFeatureGate, ProGateLoading } from "@/components/ProFeatureGate";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import { EmptyState } from "@/components/common/EmptyState";

type Period = "7d" | "30d" | "90d";

export default function Analytics() {
  const [selectedClient, setSelectedClient] = useState("all");
  const [period, setPeriod] = useState<Period>("30d");
  useTrackOnMount("feature_open", { feature: "analytics" });

  const access = useProAccess();
  const { loading, growthData, engagementData, heatmapData, avgEngagement, totalFollowers } = useAnalyticsData();
  const { activeBusinessId, isReady } = useActiveBusiness();

  if (access.loading) return <ProGateLoading />;
  if (!access.hasPro)
    return <ProFeatureGate feature="Analytics" description="Métricas y reportes de rendimiento de tus cuentas." clientId={access.clientId} />;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!isReady) return null;
  if (!activeBusinessId) return <EmptyState feature="Analytics" />;

  const hasEngagement = engagementData.length > 0;
  const postsCount = hasEngagement ? engagementData.reduce((s, e) => s + e.likes + e.comments + e.shares, 0) : null;
  const hasAnyData = growthData.length > 0 || hasEngagement || heatmapData.length > 0 || totalFollowers !== null || avgEngagement !== null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-display font-bold tracking-tight">Analytics</h1>
          <p className="text-sm text-muted-foreground">Métricas y reportes de rendimiento</p>
        </div>
        <div className="flex gap-2">
          <Select value={selectedClient} onValueChange={setSelectedClient}>
            <SelectTrigger className="h-8 w-44 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent><SelectItem value="all">Todos los clientes</SelectItem></SelectContent>
          </Select>
          <Select value={period} onValueChange={(v) => setPeriod(v as Period)}>
            <SelectTrigger className="h-8 w-36 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Últimos 7d</SelectItem>
              <SelectItem value="30d">Últimos 30d</SelectItem>
              <SelectItem value="90d">Últimos 90d</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {!hasAnyData && (
        <div className="flex items-center gap-2 bg-muted/40 rounded px-3 py-2 text-xs text-muted-foreground">
          <Info className="h-3.5 w-3.5 shrink-0" />
          <span className="flex-1">Aún no hay métricas reales · las analíticas se activan al conectar tus cuentas y publicar contenido</span>
          <Button asChild size="sm" variant="outline" className="h-7 text-xs shrink-0">
            <Link to={`/clients/${activeBusinessId}`}>Conectar en Cuentas Sociales →</Link>
          </Button>
        </div>
      )}

      <AnalyticsKPIs followers={totalFollowers} engagement={avgEngagement} bestHour={heatmapData.length > 0 ? "19:00 – 21:00" : null} posts={postsCount} />

      <div className="grid gap-3 lg:grid-cols-2">
        <GrowthChart data={growthData} />
        <EngagementChart data={engagementData} />
      </div>

      <BestTimesHeatmap data={heatmapData} />
    </div>
  );
}
