// @vitest-environment jsdom
// B3b · sección Analítica del tab Cuentas · estados HONESTOS (P1): el verde lo da el status REAL
// (/oauth/{provider}/status), NO abrir el popup. Google y Meta son independientes. Cero Zernio visible.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const gMutate = vi.fn();
const mMutate = vi.fn();
const gStatus: { data: { connected: boolean }; refetch: () => void } = { data: { connected: false }, refetch: vi.fn() };
const mStatus: { data: { connected: boolean }; refetch: () => void } = { data: { connected: false }, refetch: vi.fn() };

vi.mock("@/hooks/useGoogleOAuth", () => ({
  useGoogleStatus: () => gStatus,
  useGoogleConnect: () => ({ mutate: gMutate, isPending: false }),
}));
vi.mock("@/hooks/useMetaOAuth", () => ({
  useMetaStatus: () => mStatus,
  useMetaOAuth: () => ({ connect: { mutate: mMutate, isPending: false } }),
}));
import { ClientAnalyticsConnect } from "@/components/clients/ClientAnalyticsConnect";

describe("ClientAnalyticsConnect · estados honestos (el verde lo da el status, no el popup · P1)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    gStatus.data = { connected: false };
    mStatus.data = { connected: false };
  });
  afterEach(() => cleanup());   // sin esto el DOM se acumula entre tests → "multiple elements"

  it("no conectado → 2 botones Conectar Google + Conectar Meta", () => {
    render(<ClientAnalyticsConnect clientId="c1" />);
    expect(screen.getByText("Conectar Google")).toBeTruthy();
    expect(screen.getByText("Conectar Meta")).toBeTruthy();
  });

  it("Google conectado → 'Conectado' para Google · Meta sigue 'Conectar Meta' (independientes)", () => {
    gStatus.data = { connected: true };
    render(<ClientAnalyticsConnect clientId="c1" />);
    expect(screen.getByText("Conectado")).toBeTruthy();
    expect(screen.queryByText("Conectar Google")).toBeNull();
    expect(screen.getByText("Conectar Meta")).toBeTruthy();
  });

  it("click 'Conectar Google' → dispara connect.mutate", () => {
    render(<ClientAnalyticsConnect clientId="c1" />);
    fireEvent.click(screen.getByText("Conectar Google"));
    expect(gMutate).toHaveBeenCalled();
  });
});
