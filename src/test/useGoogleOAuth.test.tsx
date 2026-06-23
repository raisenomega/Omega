// @vitest-environment jsdom
// Fase B2 · useGoogleOAuth toma el clientId de la RUTA y lo pasa como ?client_id= →
// cierra el 422 que el backend de Fase A introdujo (Query requerido). window.location
// stubeado: el connect redirige al consent; sin stub jsdom tiraria "navigation not
// implemented" (ruido). Test limpio = cualquier salida inesperada es senal.
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

vi.mock("@/lib/api-client", () => ({ apiGet: vi.fn() }));
vi.mock("@/hooks/use-toast", () => ({ useToast: () => ({ toast: vi.fn() }) }));
vi.mock("@/hooks/useDemoMode", () => ({ useDemoMode: () => ({ isDemoAccount: false }) }));
import { apiGet } from "@/lib/api-client";
import { useGoogleStatus, useGoogleConnect } from "@/hooks/useGoogleOAuth";

const mGet = apiGet as ReturnType<typeof vi.fn>;

function wrap({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}

describe("useGoogleOAuth · client_id de la ruta en la URL (cierra el 422)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(window, "location", { configurable: true, writable: true, value: { href: "" } });
  });

  it("status pasa ?client_id= al backend", async () => {
    mGet.mockResolvedValue({ connected: false, scopes: null, has_refresh: false });
    renderHook(() => useGoogleStatus("c1"), { wrapper: wrap });
    await waitFor(() => expect(mGet).toHaveBeenCalledWith("/oauth/google/status?client_id=c1"));
  });

  it("connect pide authorize con ?client_id=", async () => {
    mGet.mockResolvedValue({ authorize_url: "https://consent.example" });
    const { result } = renderHook(() => useGoogleConnect("c1"), { wrapper: wrap });
    result.current.mutate();
    await waitFor(() => expect(mGet).toHaveBeenCalledWith("/oauth/google/authorize?client_id=c1"));
  });
});
