// @vitest-environment jsdom
// B-2 headless · el relay /zernio/return SOLO reenvía status+platform al opener (postMessage) y cierra.
// No afirma conexión: el verde lo decide connected-accounts en el opener. (DEBT-FRONTEND-TEST-GAP cubierto.)
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ZernioReturn from "@/pages/ZernioReturn";

function renderAt(search: string) {
  return render(
    <MemoryRouter initialEntries={[`/zernio/return${search}`]}>
      <ZernioReturn />
    </MemoryRouter>,
  );
}

describe("ZernioReturn · relay del popup headless", () => {
  let postMessage: ReturnType<typeof vi.fn>;
  let close: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    postMessage = vi.fn();
    close = vi.fn();
    vi.stubGlobal("opener", { postMessage });
    vi.stubGlobal("close", close);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("postMessage al opener con status+platform y luego cierra", () => {
    renderAt("?zernio=connected&platform=instagram");
    expect(postMessage).toHaveBeenCalledWith(
      { source: "zernio", status: "connected", platform: "instagram" },
      window.location.origin,
    );
    expect(close).toHaveBeenCalled();
  });

  it("reenvía el status tal cual (needs_page · FB) · no inventa conexión", () => {
    renderAt("?zernio=needs_page&platform=facebook");
    expect(postMessage).toHaveBeenCalledWith(
      { source: "zernio", status: "needs_page", platform: "facebook" },
      window.location.origin,
    );
  });
});
