// @vitest-environment jsdom
// Estrategias C1 · header: los 2 botones (Generar estrategia + Pack de Estrategias) SIEMPRE en
// la linea del titulo (no se caen) + texto descriptivo corto, frase fija. Solo UX/layout +
// el texto. El boton Pack y su dialogo coming-soon intactos (cero regresion de logica).
import { describe, it, expect, vi, beforeAll, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

vi.mock("@/hooks/useBehavioralTracking", () => ({ useTrackOnMount: () => {} }));
vi.mock("@/contexts/ActiveBusinessContext", () => ({
  useActiveBusiness: () => ({ activeBusinessId: "biz1", isReady: true }),
}));
vi.mock("@/hooks/useStrategies", () => ({
  useStrategiesList: () => ({
    data: { items: [], cadence: "semanal" },
    isLoading: false,
    isError: false,
    refetch: vi.fn(),
  }),
  useGenerateStrategy: () => ({ mutate: vi.fn(), isPending: false }),
}));

import Strategies from "@/pages/Strategies";

const FRASE = "ARIA prepara estrategias con tu contexto y las tendencias del momento y recibes automáticamente según tu plan.";

beforeAll(() => {
  Element.prototype.hasPointerCapture = vi.fn();
  Element.prototype.releasePointerCapture = vi.fn();
  Element.prototype.scrollIntoView = vi.fn();
});
beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("Estrategias · header (C1)", () => {
  it("test_header_botones · render de los 2 botones del header", () => {
    render(<Strategies />);
    expect(screen.getByRole("button", { name: /generar estrategia/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /pack de estrategias/i })).toBeTruthy();
  });

  it("test_texto_corto · el subtitulo es la frase corta nueva (fija)", () => {
    render(<Strategies />);
    expect(screen.getByText(FRASE)).toBeTruthy();
  });

  it("test_pack_dialog_intacto · el boton Pack abre su dialogo coming-soon", () => {
    render(<Strategies />);
    expect(screen.queryByText(/coming soon/i)).toBeNull();              // cerrado al inicio
    fireEvent.click(screen.getByRole("button", { name: /pack de estrategias/i }));
    expect(screen.getByText(/coming soon/i)).toBeTruthy();              // abre su dialogo
  });
});
