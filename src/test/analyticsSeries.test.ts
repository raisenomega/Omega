import { describe, it, expect } from "vitest";
import { engagementTotalSeries, fmtPct, hasGrowthTrend, activeAnalyticsView, type EngagementSeriesPoint, type NetworkBreakdown, type AggregateView } from "@/lib/analytics-series";

const pt = (date: string, likes: number, comments: number, shares: number, saves: number, views: number): EngagementSeriesPoint =>
  ({ date, impressions: 0, reach: 0, likes, comments, shares, saves, clicks: 0, views });

describe("analytics-series · transforms puros del panel", () => {
  it("engagementTotalSeries suma interacciones (NO views) por día", () => {
    const out = engagementTotalSeries([
      pt("2026-04-11", 0, 0, 0, 0, 86),   // solo views → engagement 0 (views no cuenta)
      pt("2026-06-20", 7, 0, 1, 1, 251),  // 7+0+1+1 = 9 (MB real · views 251 excluido)
    ]);
    expect(out).toEqual([
      { date: "2026-04-11", engagement: 0 },
      { date: "2026-06-20", engagement: 9 },
    ]);
  });

  it("engagementTotalSeries vacío → [] (empty state honesto, no cero falso)", () => {
    expect(engagementTotalSeries([])).toEqual([]);
  });

  it("fmtPct: null → '—' (nunca 0 inventado) · valor → 'N%' · 0 real se respeta", () => {
    expect(fmtPct(null)).toBe("—");
    expect(fmtPct(5.8)).toBe("5.8%");   // MB histórico
    expect(fmtPct(18.2)).toBe("18.2%"); // OR histórico
    expect(fmtPct(0)).toBe("0%");       // 0 real (no es lo mismo que sin dato)
  });

  it("hasGrowthTrend: <2 puntos → false (no fingir tendencia con 1 dato · P1)", () => {
    expect(hasGrowthTrend([])).toBe(false);
    expect(hasGrowthTrend([{ date: "2026-06-20", followers: 2 }])).toBe(false);             // 1 dato → insuficiente
    expect(hasGrowthTrend([{ date: "2026-06-20", followers: 2 }, { date: "2026-06-21", followers: 2 }])).toBe(true);  // 2 reales (MB)
  });
});

const AGG: AggregateView = { followers: 5, reach: 166, er: 6.6, engagementSeries: [], postsSeries: [] };
const NETS: NetworkBreakdown[] = [
  { platform: "instagram", followers: 2, reach: 155, likes: 7, comments: 0, shares: 1, saves: 1, views: 251, profile_engagement: 5.8, engagement_series: [], posts_series: [] },
  { platform: "facebook", followers: 3, reach: 0, likes: 0, comments: 0, shares: 0, saves: 0, views: 86, profile_engagement: null, engagement_series: [], posts_series: [] },
];

describe("activeAnalyticsView · switch de fuente del chip", () => {
  it("sin red (null) → vista agregada · growth disponible · sin label", () => {
    const v = activeAnalyticsView(null, NETS, AGG);
    expect(v.followers).toBe(5); expect(v.reach).toBe(166); expect(v.network).toBeNull();
    expect(v.growthAvailable).toBe(true);
  });

  it("Instagram → SUS números · growth disponible (IG)", () => {
    const v = activeAnalyticsView("instagram", NETS, AGG);
    expect(v.followers).toBe(2); expect(v.reach).toBe(155); expect(v.er).toBe(5.8);
    expect(v.network).toBe("instagram"); expect(v.growthAvailable).toBe(true);
  });

  it("Facebook → SUS números (ER null='—') · growth NO disponible (no IG)", () => {
    const v = activeAnalyticsView("facebook", NETS, AGG);
    expect(v.followers).toBe(3); expect(v.reach).toBe(0); expect(v.er).toBeNull();
    expect(v.network).toBe("facebook"); expect(v.growthAvailable).toBe(false);   // NO datos del perfil disfrazados
  });

  it("red inexistente → cae a agregada (fallback seguro · no rompe)", () => {
    const v = activeAnalyticsView("tiktok", [], AGG);
    expect(v.network).toBeNull(); expect(v.followers).toBe(5);
  });
});
