import { useMemo } from "react";
import { useDashboardData } from "./useDashboardData";

// DEBT-034: este hook contiene mock generators (growth/engagement/heatmap/topPosts).
// Los followers reales no existen en schema V3. Hasta que llegue el sync Meta API
// con followers reales, este hook mantiene generadores con base 0 para no romper UI
// y para que Charts/Tables tengan estructura. Fase 3 §3.x — rewrite contra
// analytics_events real o eliminar página entera.

function generateGrowthData(totalFollowers: number) {
  const safe = Number.isFinite(totalFollowers) ? totalFollowers : 0;
  const days = 30;
  const data = [];
  const base = Math.max(safe * 0.85, 10);
  for (let i = days; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const growth = base + ((safe - base) * (days - i)) / days + Math.random() * (safe * 0.02);
    data.push({
      date: date.toLocaleDateString("es-ES", { day: "2-digit", month: "short" }),
      followers: Math.round(growth),
    });
  }
  return data;
}

function generateEngagementData(platformCounts: { platform: string; count: number }[]) {
  return platformCounts
    .filter((p) => p.count > 0)
    .map((p) => ({
      platform: p.platform.charAt(0).toUpperCase() + p.platform.slice(1),
      likes: Math.round(p.count * (0.02 + Math.random() * 0.05) * 100),
      comments: Math.round(p.count * (0.005 + Math.random() * 0.01) * 100),
      shares: Math.round(p.count * (0.002 + Math.random() * 0.008) * 100),
    }));
}

function generateHeatmapData() {
  const days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];
  const data: { day: string; hour: number; value: number }[] = [];
  for (const day of days) {
    for (let hour = 6; hour <= 23; hour++) {
      const isPeak =
        (hour >= 9 && hour <= 11) || (hour >= 13 && hour <= 14) || (hour >= 19 && hour <= 21);
      const isWeekend = day === "Sáb" || day === "Dom";
      const base = isPeak ? 60 : 20;
      const modifier = isWeekend ? 0.7 : 1;
      data.push({ day, hour, value: Math.round((base + Math.random() * 40) * modifier) });
    }
  }
  return data;
}

function generateTopPosts() {
  const titles = [
    "Lanzamiento de nueva colección",
    "Detrás de cámaras",
    "Tips de productividad",
    "Colaboración especial",
    "Recap del mes",
  ];
  const platforms = ["instagram", "tiktok", "facebook", "twitter", "linkedin"];
  return titles.map((title, i) => ({
    id: String(i),
    title,
    platform: platforms[i % platforms.length],
    likes: Math.round(500 + Math.random() * 4500),
    comments: Math.round(20 + Math.random() * 300),
    shares: Math.round(10 + Math.random() * 200),
    engagement: +(2 + Math.random() * 8).toFixed(1),
  }));
}

export function useAnalyticsData() {
  // DEBT-034: useDashboardData ya no expone totalFollowers (Step 2 §2.x).
  // Base 0 hasta que sync de Meta API alimente followers reales.
  const { platformCounts, loading } = useDashboardData();
  const totalFollowers = 0;

  const growthData = useMemo(() => generateGrowthData(totalFollowers), [totalFollowers]);
  const engagementData = useMemo(() => generateEngagementData(platformCounts), [platformCounts]);
  const heatmapData = useMemo(() => generateHeatmapData(), []);
  const topPosts = useMemo(() => generateTopPosts(), []);

  const avgEngagement = engagementData.length
    ? +(
        engagementData.reduce((s, e) => s + e.likes + e.comments + e.shares, 0) /
        engagementData.length /
        Math.max(totalFollowers, 1) *
        100
      ).toFixed(2)
    : 0;

  return { loading, growthData, engagementData, heatmapData, topPosts, avgEngagement, totalFollowers };
}
