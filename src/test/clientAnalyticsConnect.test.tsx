// @vitest-environment jsdom
// B3b · sección Analítica del tab Cuentas · estado HONESTO (P1): el verde lo da el status REAL
// (/oauth/google/status), NO abrir el popup. (Meta retirado · solo Google.) Cero Zernio visible.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const gMutate = vi.fn();
const gStatus: { data: { connected: boolean }; refetch: () => void } = { data: { connected: false }, refetch: vi.fn() };

vi.mock("@/hooks/useGoogleOAuth", () => ({
  useGoogleStatus: () => gStatus,
  useGoogleConnect: () => ({ mutate: gMutate, isPending: false }),
}));
// El picker tiene su propio test (googlePropertyPicker.test) · acá se aísla (usa useQueryClient).
vi.mock("@/components/clients/GooglePropertyPicker", () => ({ GooglePropertyPicker: () => null }));
import { ClientAnalyticsConnect } from "@/components/clients/ClientAnalyticsConnect";

describe("ClientAnalyticsConnect · estado honesto (el verde lo da el status, no el popup · P1)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    gStatus.data = { connected: false };
  });
  afterEach(() => cleanup());

  it("no conectado → botón Conectar Google", () => {
    render(<ClientAnalyticsConnect clientId="c1" />);
    expect(screen.getByText("Conectar Google")).toBeTruthy();
  });

  it("Google conectado → 'Conectado' (sin botón Conectar Google)", () => {
    gStatus.data = { connected: true };
    render(<ClientAnalyticsConnect clientId="c1" />);
    expect(screen.getByText("Conectado")).toBeTruthy();
    expect(screen.queryByText("Conectar Google")).toBeNull();
  });

  it("click 'Conectar Google' → dispara connect.mutate", () => {
    render(<ClientAnalyticsConnect clientId="c1" />);
    fireEvent.click(screen.getByText("Conectar Google"));
    expect(gMutate).toHaveBeenCalled();
  });
});
