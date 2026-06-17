// @vitest-environment jsdom
// El bug del owner fue en el RENDER: al abrir el popup la fila cantó "Ya conecté". Este test
// simula clic en Vincular SIN completar OAuth y exige que la fila NO afirme conexión ni muestre
// verde · solo ofrezca verificar/reintentar. Mockea api-client (evita import de supabase/client).
import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

vi.mock("@/lib/api-client", () => ({
  apiGet: vi.fn(async () => ({ auth_url: "https://www.facebook.com/oauth" })),
  apiPost: vi.fn(),
}));
vi.mock("@/hooks/use-toast", () => ({ useToast: () => ({ toast: vi.fn() }) }));
import { ZernioConnectButton } from "@/components/clients/ZernioConnectButton";

function wrap({ children }: { children: ReactNode }) {
  return createElement(QueryClientProvider, { client: new QueryClient() }, children);
}
afterEach(cleanup);   // sin setupFile wired · cleanup explícito · evita DOM filtrado entre tests
const mount = (connected: boolean) =>
  render(createElement(ZernioConnectButton,
    { clientId: "c1", platform: "instagram", connected, onSynced: vi.fn() }), { wrapper: wrap });


describe("ZernioConnectButton · honestidad de estado (P1)", () => {
  it("clic en Vincular SIN completar OAuth → NO afirma conexión ni muestra verde", async () => {
    window.open = vi.fn();
    mount(false);
    fireEvent.click(screen.getByText(/Vincular Instagram/i));
    await waitFor(() => expect(screen.getByText(/Verificar conexión/i)).toBeTruthy());
    expect(screen.queryByText(/Ya conecté/i)).toBeNull();          // no afirma un hecho
    expect(screen.getByText(/Vincular Instagram/i)).toBeTruthy();  // retry SIEMPRE disponible (no atrapado)
  });

  it("connected=true (verdad de Zernio) → verde, sin botón de vincular", () => {
    mount(true);
    expect(screen.getByText("Instagram")).toBeTruthy();
    expect(screen.queryByText(/Vincular/i)).toBeNull();
  });
});
