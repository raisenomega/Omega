import { describe, it, expect } from "vitest";
import { platformLabel, isConnected, allConnected, type ConnectedItem } from "@/lib/zernioConnect";

describe("zernioConnect · white-label + estado real de conexión", () => {
  it("platformLabel nombra la RED, nunca 'Zernio'", () => {
    expect(platformLabel("facebook")).toBe("Facebook");
    expect(platformLabel("tiktok")).toBe("TikTok");
    expect(platformLabel("instagram")).toBe("Instagram");
    expect(platformLabel("desconocida")).toBe("desconocida");
    // ninguna etiqueta contiene "Zernio"
    expect(Object.values({ a: platformLabel("facebook"), b: platformLabel("tiktok") }).join().toLowerCase())
      .not.toContain("zernio");
  });

  const items: ConnectedItem[] = [
    { platform: "instagram", handle: "@zafaconesr", zernio_account_id: "ig1" },
    { platform: "facebook", handle: "Zafacones", zernio_account_id: "fb1" },
  ];

  it("isConnected refleja si la red está en el profile", () => {
    expect(isConnected("instagram", items)).toBe(true);
    expect(isConnected("tiktok", items)).toBe(false);   // no conectada → parpadea
  });

  it("allConnected true solo si TODAS las redes del negocio están conectadas", () => {
    expect(allConnected(["instagram", "facebook"], items)).toBe(true);
    expect(allConnected(["instagram", "facebook", "tiktok"], items)).toBe(false);
    expect(allConnected([], items)).toBe(false);
  });
});
