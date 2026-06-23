// @vitest-environment jsdom
// Fase B2 · useMetaOAuth toma el clientId de la RUTA y lo pasa como ?client_id= →
// cierra el 422 que el backend de Fase B1 introdujo (Query requerido). window.location
// stubeado (el connect redirige al dialog de Meta · sin stub jsdom tiraria "navigation
// not implemented"). useMetaOAuth devuelve { connect } → se dispara con connect.mutate().
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

vi.mock("@/lib/api-client", () => ({ apiGet: vi.fn() }));
vi.mock("@/hooks/use-toast", () => ({ useToast: () => ({ toast: vi.fn() }) }));
vi.mock("@/hooks/useDemoMode", () => ({ useDemoMode: () => ({ isDemoAccount: false }) }));
import { apiGet } from "@/lib/api-client";
import { useMetaStatus, useMetaOAuth } from "@/hooks/useMetaOAuth";

const mGet = apiGet as ReturnType<typeof vi.fn>;
const mOpen = vi.fn();

function wrap({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}

describe("useMetaOAuth · client_id de la ruta en la URL (cierra el 422)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.open = mOpen;   // stub limpio del popup (sin "window.open not implemented" de jsdom)
  });

  it("status pasa ?client_id= al backend", async () => {
    mGet.mockResolvedValue({ connected: false, scopes: null, external_account_id: null });
    renderHook(() => useMetaStatus("c1"), { wrapper: wrap });
    await waitFor(() => expect(mGet).toHaveBeenCalledWith("/oauth/meta/status?client_id=c1"));
  });

  it("connect pide authorize con ?client_id=", async () => {
    mGet.mockResolvedValue({ authorize_url: "https://dialog.example" });
    const { result } = renderHook(() => useMetaOAuth("c1"), { wrapper: wrap });
    result.current.connect.mutate();
    await waitFor(() => expect(mGet).toHaveBeenCalledWith("/oauth/meta/authorize?client_id=c1"));
    await waitFor(() => expect(mOpen).toHaveBeenCalledWith("https://dialog.example", "_blank", expect.stringContaining("width=600")));
  });
});
