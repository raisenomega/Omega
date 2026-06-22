import { describe, it, expect } from "vitest";
import {
  CONNECTABLE_PLATFORMS,
  COMING_SOON_PLATFORMS,
  TAB_PLATFORMS_LEGEND,
} from "@/lib/social-platforms-tab";

describe("social-platforms-tab · fuente única del tab Cuentas (NO modal §7)", () => {
  it("conectables = las 6 del onboarding §7 + Reddit (7 exactas, en orden)", () => {
    expect(CONNECTABLE_PLATFORMS.map((p) => p.value)).toEqual([
      "instagram", "facebook", "tiktok", "twitter", "linkedin", "youtube", "reddit",
    ]);
  });

  it("Reddit es conectable (decisión owner · Zernio da authUrl · connect genérico)", () => {
    expect(CONNECTABLE_PLATFORMS.some((p) => p.value === "reddit")).toBe(true);
  });

  it("coming-soon = threads/bluesky/pinterest/snapchat, sin solaparse con conectables", () => {
    expect(COMING_SOON_PLATFORMS.map((p) => p.value)).toEqual([
      "threads", "bluesky", "pinterest", "snapchat",
    ]);
    const connectable = new Set(CONNECTABLE_PLATFORMS.map((p) => p.value));
    for (const p of COMING_SOON_PLATFORMS) {
      expect(connectable.has(p.value)).toBe(false);   // una red está en UNA sola lista
    }
  });

  it("white-label · ninguna etiqueta menciona 'Zernio'", () => {
    const labels = [...CONNECTABLE_PLATFORMS, ...COMING_SOON_PLATFORMS]
      .map((p) => p.label).join(" ").toLowerCase();
    expect(labels).not.toContain("zernio");
  });

  it("leyenda nombra el universo conectable + la regla una-cuenta-por-red", () => {
    expect(TAB_PLATFORMS_LEGEND).toContain("Reddit");
    expect(TAB_PLATFORMS_LEGEND).toContain("Una cuenta por red por negocio");
    expect(TAB_PLATFORMS_LEGEND.toLowerCase()).not.toContain("zernio");
  });
});
