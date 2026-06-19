// @vitest-environment jsdom
// B-2 headless · el relay /zernio/return reenvía {status,platform} por BroadcastChannel SAME-ORIGIN
// (funciona con noopener · window.opener.postMessage era no-op) → fallback storage. NO afirma conexión:
// el verde lo decide connected-accounts en el opener. (Cierra el bug latente del noopener · ex-DEBT-AUTOVERDE.)
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ZernioReturn from "@/pages/ZernioReturn";

let posted: { name: string; msg: unknown }[] = [];

class MockBC {
  name: string;
  constructor(n: string) { this.name = n; }
  postMessage(m: unknown) { posted.push({ name: this.name, msg: m }); }
  close() {}
}

function renderAt(search: string) {
  return render(
    <MemoryRouter initialEntries={[`/zernio/return${search}`]}>
      <ZernioReturn />
    </MemoryRouter>,
  );
}

describe("ZernioReturn · relay por BroadcastChannel (same-origin · sobrevive noopener)", () => {
  let close: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    posted = [];
    close = vi.fn();
    vi.stubGlobal("BroadcastChannel", MockBC);
    vi.stubGlobal("close", close);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("publica {status,platform} en el canal zernio-oauth y cierra", () => {
    renderAt("?zernio=needs_page&platform=facebook");
    expect(posted).toContainEqual({
      name: "zernio-oauth", msg: { source: "zernio", status: "needs_page", platform: "facebook" },
    });
    expect(close).toHaveBeenCalled();
  });

  it("reenvía connected tal cual (para refetch · NO pinta verde)", () => {
    renderAt("?zernio=connected&platform=instagram");
    expect(posted).toContainEqual({
      name: "zernio-oauth", msg: { source: "zernio", status: "connected", platform: "instagram" },
    });
  });

  it("fallback a storage si no hay BroadcastChannel (NUNCA window.opener)", () => {
    vi.stubGlobal("BroadcastChannel", undefined);
    const setItem = vi.spyOn(Storage.prototype, "setItem");
    renderAt("?zernio=needs_page&platform=facebook");
    expect(setItem).toHaveBeenCalledWith("zernio-oauth", expect.stringContaining("needs_page"));
  });
});
