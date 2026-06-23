// @vitest-environment jsdom
// B3a · el relay /oauth/return reenvia {provider,status} por BroadcastChannel SAME-ORIGIN -> fallback
// storage. NO afirma conexion: el verde lo decide /oauth/{provider}/status en el opener (P1). Espejo
// de zernio-return.test (probado en prod). Ruta generica /oauth/return · cero "zernio".
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import OAuthAnalyticsReturn from "@/pages/OAuthAnalyticsReturn";

let posted: { name: string; msg: unknown }[] = [];

class MockBC {
  name: string;
  constructor(n: string) { this.name = n; }
  postMessage(m: unknown) { posted.push({ name: this.name, msg: m }); }
  close() {}
}

function renderAt(search: string) {
  return render(
    <MemoryRouter initialEntries={[`/oauth/return${search}`]}>
      <OAuthAnalyticsReturn />
    </MemoryRouter>,
  );
}

describe("OAuthAnalyticsReturn · relay por BroadcastChannel (espejo de Zernio · cero zernio)", () => {
  let close: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    posted = [];
    close = vi.fn();
    vi.stubGlobal("BroadcastChannel", MockBC);
    vi.stubGlobal("close", close);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("publica {provider,status} en el canal oauth-analytics y cierra", () => {
    renderAt("?provider=google&status=connected");
    expect(posted).toContainEqual({
      name: "oauth-analytics", msg: { source: "oauth-analytics", provider: "google", status: "connected" },
    });
    expect(close).toHaveBeenCalled();
  });

  it("reenvia meta/error tal cual (para refetch · NO pinta verde)", () => {
    renderAt("?provider=meta&status=error");
    expect(posted).toContainEqual({
      name: "oauth-analytics", msg: { source: "oauth-analytics", provider: "meta", status: "error" },
    });
  });

  it("fallback a storage si no hay BroadcastChannel", () => {
    vi.stubGlobal("BroadcastChannel", undefined);
    const setItem = vi.spyOn(Storage.prototype, "setItem");
    renderAt("?provider=google&status=connected");
    expect(setItem).toHaveBeenCalledWith("oauth-analytics", expect.stringContaining("google"));
  });
});
