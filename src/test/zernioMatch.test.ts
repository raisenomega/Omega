import { describe, it, expect } from "vitest";
import { normalizeHandle, handlesMatch, autoMatch } from "@/lib/zernioMatch";

describe("zernioMatch · auto-match + warning del picker Zernio", () => {
  it("normaliza @, mayúsculas y espacios", () => {
    expect(normalizeHandle("@Zafaconesr")).toBe("zafaconesr");
    expect(normalizeHandle("  @mila_software ")).toBe("mila_software");
    expect(normalizeHandle(null)).toBe("");
  });

  it("handlesMatch ignora @ y case · vacío nunca matchea", () => {
    expect(handlesMatch("@zafaconesr", "Zafaconesr")).toBe(true);
    expect(handlesMatch("@zafaconesr", "@raisenagency")).toBe(false);
    expect(handlesMatch("", "x")).toBe(false);
  });

  // Escenario EXACTO del incidente 8-jun: 2 negocios con Instagram en el mismo workspace.
  it("autoMatch pre-selecciona la cuenta correcta por negocio (2 IG · no cruza)", () => {
    const opts = [
      { zernio_account_id: "ig_zafa", platform: "instagram", handle: "@zafaconesr" },
      { zernio_account_id: "ig_raisen", platform: "instagram", handle: "@raisenagency" },
    ];
    expect(autoMatch(opts, "@zafaconesr")?.zernio_account_id).toBe("ig_zafa");
    expect(autoMatch(opts, "@raisenagency")?.zernio_account_id).toBe("ig_raisen");
  });

  it("autoMatch null si ninguna coincide → fuerza elección manual + warning", () => {
    const opts = [{ zernio_account_id: "x", platform: "instagram", handle: "@otro" }];
    expect(autoMatch(opts, "@zafaconesr")).toBeNull();
  });

  it("autoMatch null si hay coincidencia ambigua (>1) → no adivina", () => {
    const opts = [
      { zernio_account_id: "a", platform: "instagram", handle: "@dup" },
      { zernio_account_id: "b", platform: "instagram", handle: "@dup" },
    ];
    expect(autoMatch(opts, "@dup")).toBeNull();
  });
});
