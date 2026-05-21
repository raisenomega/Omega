import { useMemo } from "react";
import { useDashboardData } from "./useDashboardData";

// DEBT-034: mock generators · ascending growth + hardcoded engagement por
// plataforma con valores realistas (Meta API pendiente · Fase 3).

function generateGrowthData() {
  const days = 30;
  const data: { date: string; followers: number }[] = [];
  const startBase = 1200;
  const endBase = 1850;
  for (let i = days; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const progress = (days - i) / days;
    const noise = (Math.random() - 0.4) * 30;  // variación natural con sesgo positivo
    const followers = Math.round(startBase + (endBase - startBase) * progress + noise);
    data.push({
      date: date.toLocaleDateString("es-ES", { day: "2-digit", month: "short" }),
      followers,
    });
  }
  return data;
}

function generateEngagementData() {
  return [
    { platform: "Instagram", likes: 450, comments: 89, shares: 120 },
    { platform: "Facebook", likes: 230, comments: 45, shares: 67 },
    { platform: "TikTok", likes: 890, comments: 234, shares: 445 },
    { platform: "LinkedIn", likes: 120, comments: 56, shares: 34 },
  ];
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
  const { loading } = useDashboardData();
  const totalFollowers = 1850;  // matches endBase de growthData · DEBT-034

  const growthData = useMemo(() => generateGrowthData(), []);
  const engagementData = useMemo(() => generateEngagementData(), []);
  const heatmapData = useMemo(() => generateHeatmapData(), []);
  const topPosts = useMemo(() => generateTopPosts(), []);

  const totalInteractions = engagementData.reduce((s, e) => s + e.likes + e.comments + e.shares, 0);
  const avgEngagement = +((totalInteractions / engagementData.length / totalFollowers) * 100).toFixed(2);

  return { loading, growthData, engagementData, heatmapData, topPosts, avgEngagement, totalFollowers };
}
