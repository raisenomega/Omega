// @vitest-environment jsdom
// jsdom provee `localStorage` · `@/lib/guardian/actions` importa transitivamente
// api-client → integrations/supabase/client.ts (toca localStorage en load) · en
// env `node` reventaba con "ReferenceError: localStorage is not defined" (P0-3).
import { describe, it, expect } from "vitest";
import { expiresFromPreset } from "@/lib/guardian/actions";

describe("guardian expiresFromPreset", () => {
  it("permanente → null", () => expect(expiresFromPreset("permanente")).toBeNull());
  it("preset desconocido → null", () => expect(expiresFromPreset("xyz")).toBeNull());

  it("24h → ISO ~24h en el futuro", () => {
    const r = expiresFromPreset("24h");
    expect(r).not.toBeNull();
    const diffH = (new Date(r as string).getTime() - Date.now()) / 3_600_000;
    expect(diffH).toBeGreaterThan(23.9);
    expect(diffH).toBeLessThan(24.1);
  });

  it("1h y 7d → deltas correctos", () => {
    const h1 = (new Date(expiresFromPreset("1h") as string).getTime() - Date.now()) / 3_600_000;
    const d7 = (new Date(expiresFromPreset("7d") as string).getTime() - Date.now()) / 3_600_000;
    expect(h1).toBeGreaterThan(0.9);
    expect(h1).toBeLessThan(1.1);
    expect(d7).toBeGreaterThan(167);
    expect(d7).toBeLessThan(169);
  });
});
