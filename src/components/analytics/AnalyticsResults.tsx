import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AnalyticsKPIs } from "@/components/analytics/AnalyticsKPIs";
import { GrowthChart } from "@/components/analytics/GrowthChart";
import { EngagementChart } from "@/components/analytics/EngagementChart";
import { EngagementOverTimeChart } from "@/components/analytics/EngagementOverTimeChart";
import { PostsOverTimeChart } from "@/components/analytics/PostsOverTimeChart";
import { BestTimesHeatmap } from "@/components/analytics/BestTimesHeatmap";
import { activeAnalyticsView, type EngagementSeriesPoint, type PostsSeriesPoint, type NetworkBreakdown } from "@/lib/analytics-series";
import { platformLabel } from "@/lib/zernioConnect";

interface EngagementRow { platform: string; likes: number; comments: number; shares: number; saves: number; views: number; reach: number }

interface AnalyticsResultsProps {
  growthData: { date: string; followers: number }[];
  engagementData: EngagementRow[];
  engagementSeries: EngagementSeriesPoint[];
  postsSeries: PostsSeriesPoint[];
  networks: NetworkBreakdown[];
  heatmapData: { day: string; hour: number; value: number }[];
  totalFollowers: number | null;
  totalReach: number | null;
  profileEngagement: number | null;
}

// Resultados del panel + chip de redes. "Todas" = vista agregada · red = data de networks[sel]
// (switch puro activeAnalyticsView). Las 3 trampas P1 honestas por card: growth no-IG="no
// disponible" · best-time per-perfil="del perfil completo" · tabla por-plataforma solo en "Todas".
export function AnalyticsResults(p: AnalyticsResultsProps) {
  const [selected, setSelected] = useState<string | null>(null);
  const view = activeAnalyticsView(selected, p.networks, {
    followers: p.totalFollowers, reach: p.totalReach, er: p.profileEngagement,
    engagementSeries: p.engagementSeries, postsSeries: p.postsSeries,
  });
  const label = view.network ? platformLabel(view.network) : null;
  const chips: (string | null)[] = [null, ...p.networks.map((n) => n.platform)];

  return (
    <>
      <div className="flex flex-wrap gap-1.5">
        {chips.map((c) => {
          const active = selected === c;
          return (
            <button key={c ?? "all"} onClick={() => setSelected(c)}
              className={`rounded-full border px-3 py-1 text-xs transition-colors ${active
                ? "border-primary bg-primary text-primary-foreground"
                : "border-border/50 text-muted-foreground hover:bg-muted/40"}`}>
              {c ? platformLabel(c) : "Todas"}
            </button>
          );
        })}
      </div>

      <AnalyticsKPIs followers={view.followers} totalReach={view.reach}
        profileEngagement={view.er} networkLabel={label} />

      <div className="grid gap-3 lg:grid-cols-2">
        {view.growthAvailable ? <GrowthChart data={p.growthData} /> : (
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardHeader className="pb-2"><CardTitle className="text-sm">Crecimiento de seguidores</CardTitle></CardHeader>
            <CardContent className="flex items-center justify-center h-56 text-xs text-muted-foreground text-center">
              No disponible para {label} · Zernio solo provee historial de seguidores de Instagram
            </CardContent>
          </Card>
        )}
        <EngagementOverTimeChart data={view.engagementSeries} networkLabel={label} />
      </div>

      <div className="grid gap-3 lg:grid-cols-2">
        <PostsOverTimeChart data={view.postsSeries} networkLabel={label} />
        <BestTimesHeatmap data={p.heatmapData} perfilCompleto={!!view.network} />
      </div>

      {!view.network && <EngagementChart data={p.engagementData} />}
    </>
  );
}
