import { describe, it, expect } from "vitest";
import { engagementTotalSeries, fmtPct, hasGrowthTrend, type EngagementSeriesPoint } from "@/lib/analytics-series";

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
