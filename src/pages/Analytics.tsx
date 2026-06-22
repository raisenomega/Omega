import { Info, Loader2 } from "lucide-react";
import { useAnalyticsData } from "@/hooks/useAnalyticsData";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { AnalyticsResults } from "@/components/analytics/AnalyticsResults";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useProAccess } from "@/hooks/useProAccess";
import { ProFeatureGate, ProGateLoading } from "@/components/ProFeatureGate";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import { EmptyState } from "@/components/common/EmptyState";

export default function Analytics() {
  useTrackOnMount("feature_open", { feature: "analytics" });

  const access = useProAccess();
  const {
    loading, growthData, engagementData, engagementSeries, postsSeries,
    heatmapData, totalFollowers, totalReach, profileEngagement, bestHour,
  } = useAnalyticsData();
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
  const hasAnyData = growthData.length > 0 || hasEngagement || heatmapData.length > 0
    || totalFollowers !== null || totalReach !== null || postsSeries.length > 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-display font-bold tracking-tight">Analytics</h1>
        <p className="text-sm text-muted-foreground">Métricas y reportes de rendimiento</p>
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

      <AnalyticsResults
        growthData={growthData}
        engagementData={engagementData}
        engagementSeries={engagementSeries}
        postsSeries={postsSeries}
        heatmapData={heatmapData}
        totalFollowers={totalFollowers}
        totalReach={totalReach}
        profileEngagement={profileEngagement}
        bestHour={bestHour}
      />
    </div>
  );
}
