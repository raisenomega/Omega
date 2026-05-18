import { useMemo } from "react";
import { useDashboardData } from "./useDashboardData";

// Generate simulated growth data for the last 30 days
function generateGrowthData(totalFollowers: number) {
  const days = 30;
  const data = [];
  const base = Math.max(totalFollowers * 0.85, 10);
  for (let i = days; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const growth = base + ((totalFollowers - base) * (days - i)) / days + Math.random() * (totalFollowers * 0.02);
    data.push({
      date: date.toLocaleDateString("es-ES", { day: "2-digit", month: "short" }),
      followers: Math.round(growth),
    });
  }
  return data;
}

// Generate simulated engagement data per platform
function generateEngagementData(platformCounts: { platform: string; followers: number }[]) {
  return platformCounts
    .filter((p) => p.followers > 0)
    .map((p) => ({
      platform: p.platform.charAt(0).toUpperCase() + p.platform.slice(1),
      likes: Math.round(p.followers * (0.02 + Math.random() * 0.05)),
      comments: Math.round(p.followers * (0.005 + Math.random() * 0.01)),
      shares: Math.round(p.followers * (0.002 + Math.random() * 0.008)),
    }));
}

// Generate heatmap data (hour x day)
function generateHeatmapData() {
  const days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];
  const data: { day: string; hour: number; value: number }[] = [];
  for (const day of days) {
    for (let hour = 6; hour <= 23; hour++) {
      // Peak hours: 9-11, 13-14, 19-21
      const isPeak =
        (hour >= 9 && hour <= 11) || (hour >= 13 && hour <= 14) || (hour >= 19 && hour <= 21);
      const isWeekend = day === "Sáb" || day === "Dom";
      const base = isPeak ? 60 : 20;
      const modifier = isWeekend ? 0.7 : 1;
      data.push({
        day,
        hour,
        value: Math.round((base + Math.random() * 40) * modifier),
      });
    }
  }
  return data;
}

// Simulated top posts
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
  const { totalFollowers, platformCounts, loading } = useDashboardData();

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
