// @vitest-environment jsdom
// Estrategias C2 · modal mas ancho (max-w-3xl) + leyendas explicativas honestas por seccion
// (resumen / pilares / ideas). Solo presentacion: datos, boton Usar y logica del modal intactos.
// Los cuadros por red con flecha llegan en el C3 (este commit solo ensancha + leyendas).
import { describe, it, expect, vi, beforeAll, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";

// El modal ahora incluye StrategyIdeaBoxes (C3) que usa useNavigate → mock para no exigir Router.
vi.mock("react-router-dom", () => ({ useNavigate: () => vi.fn() }));
// CAPA 1 · StrategyIdeaBoxes usa useRecordStrategyUse (react-query) → mock para no exigir provider.
vi.mock("@/hooks/useRecordStrategyUse", () => ({ useRecordStrategyUse: () => ({ mutate: vi.fn() }) }));

import { StrategyDetailModal } from "@/components/strategies/StrategyDetailModal";
import type { Strategy } from "@/hooks/useStrategies";

const STRAT: Strategy = {
  id: "s1",
  client_id: "biz1",
  titulo: "Mi estrategia de junio",
  tipo: "semanal",
  estado: "active",
  created_at: "2026-06-01T00:00:00Z",
  contenido: {
    resumen: "Resumen del enfoque",
    pilares: ["Pilar A", "Pilar B"],
    posts_sugeridos: [{ plataforma: "Instagram", idea: "Idea para IG" }],
  },
};

beforeAll(() => {
  Element.prototype.hasPointerCapture = vi.fn();
  Element.prototype.releasePointerCapture = vi.fn();
  Element.prototype.scrollIntoView = vi.fn();
});
afterEach(cleanup);

describe("Estrategias · modal ancho + leyendas (C2)", () => {
  it("test_modal_ancho · DialogContent usa max-w-3xl (mas ancho que lg)", () => {
    render(<StrategyDetailModal strategy={STRAT} onClose={() => {}} />);
    const dialog = screen.getByRole("dialog");
    expect(dialog.className).toMatch(/max-w-3xl/);
    expect(dialog.className).not.toMatch(/max-w-lg/);
  });

  it("test_modal_leyendas · cada seccion tiene su leyenda de ayuda", () => {
    render(<StrategyDetailModal strategy={STRAT} onClose={() => {}} />);
    expect(screen.getByText(/enfoque general de esta estrategia/i)).toBeTruthy();   // resumen
    expect(screen.getByText(/ejes de contenido/i)).toBeTruthy();                    // pilares
    expect(screen.getByText(/aún no son posts reales/i)).toBeTruthy();              // ideas
  });

  it("test_modal_sin_regresion · sigue mostrando titulo + resumen + pilares + ideas", () => {
    render(<StrategyDetailModal strategy={STRAT} onClose={() => {}} />);
    expect(screen.getByText("Mi estrategia de junio")).toBeTruthy();
    expect(screen.getByText("Resumen del enfoque")).toBeTruthy();
    expect(screen.getByText("Pilar A")).toBeTruthy();
    expect(screen.getByText("Pilar B")).toBeTruthy();
    expect(screen.getByText(/Idea para IG/)).toBeTruthy();
  });
});
