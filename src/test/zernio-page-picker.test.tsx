// @vitest-environment jsdom
// B-2 FB · page-picker · honestidad visual: el verde NUNCA sale del select ({ok:true}) — solo de
// connected-accounts vía onConnected→refetch. + errores honestos (409 expirado ≠ vacía ≠ fallo de fetch).
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

vi.mock("@/lib/api-client", () => ({ apiGet: vi.fn(), apiPost: vi.fn() }));
vi.mock("@/hooks/use-toast", () => ({ useToast: () => ({ toast: vi.fn() }) }));
import { apiGet, apiPost } from "@/lib/api-client";
import { ZernioPagePicker } from "@/components/clients/ZernioPagePicker";

const mGet = apiGet as ReturnType<typeof vi.fn>;
const mPost = apiPost as ReturnType<typeof vi.fn>;

function wrap(ui: ReactNode) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, ui);
}

const base = () => ({ clientId: "c1", platform: "facebook", onClose: vi.fn(), onConnected: vi.fn() });

describe("ZernioPagePicker · honestidad visual", () => {
  beforeEach(() => vi.clearAllMocks());

  it("elegir página → select-page + onConnected (refetch) + onClose · NO pinta verde", async () => {
    mGet.mockResolvedValue({ pages: [{ id: "pg1", name: "La Casita" }] });
    mPost.mockResolvedValue({ ok: true });
    const p = base();
    render(wrap(<ZernioPagePicker {...p} />));
    fireEvent.click(await screen.findByText("La Casita"));
    await waitFor(() =>
      expect(mPost).toHaveBeenCalledWith("/clients/c1/social-accounts/facebook/select-page", { page_id: "pg1" }));
    await waitFor(() => expect(p.onConnected).toHaveBeenCalled());   // dispara refetch (verdad de Zernio)
    expect(p.onClose).toHaveBeenCalled();
  });

  it("409 no_pending → mensaje de sesión expirada (reconectar)", async () => {
    mGet.mockRejectedValue(new Error("no_pending_facebook_oauth"));
    render(wrap(<ZernioPagePicker {...base()} />));
    expect(await screen.findByText(/expiró/i)).toBeTruthy();
  });

  it("lista vacía legítima (0 páginas) ≠ fallo de fetch", async () => {
    mGet.mockResolvedValue({ pages: [] });
    render(wrap(<ZernioPagePicker {...base()} />));
    expect(await screen.findByText(/no administra ninguna página/i)).toBeTruthy();
  });

  it("fallo de fetch (no 409) → mensaje de error distinto", async () => {
    mGet.mockRejectedValue(new Error("HTTP 500"));
    render(wrap(<ZernioPagePicker {...base()} />));
    expect(await screen.findByText(/no se pudieron cargar/i)).toBeTruthy();
  });
});
