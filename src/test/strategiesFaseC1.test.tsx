// @vitest-environment jsdom
// Fase C.1 (solo frontend) · (1) contador "quedan" = total-used ("5 de 6"). (2) el modal OCULTA
// las ideas ya usadas (cruce idx con usedIdxs · buildBoxes preserva el idx original B.3) y descarta
// cuadros vacios. (3) tarjeta activa SIN botones (Usar/Ajuste/Archivar quitados · modelo idea-level)
// + borde amarillo · el clic abre el modal. Cero backend.
import { describe, it, expect, vi, beforeAll, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const navigateSpy = vi.fn();
vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
vi.mock("@/hooks/useRecordIdeaUse", () => ({ useRecordIdeaUse: () => ({ mutate: vi.fn() }) }));

import { StrategyIdeaBoxes } from "@/components/strategies/StrategyIdeaBoxes";
import { StrategyCard } from "@/components/strategies/StrategyCard";
import type { Strategy } from "@/hooks/useStrategies";

const POSTS = [
  { plataforma: "Instagram", idea: "ig-0" },   // idx 0
  { plataforma: "Instagram", idea: "ig-1" },   // idx 1
  { plataforma: "TikTok", idea: "tt-2" },       // idx 2
];
const STRAT6: Strategy = {
  id: "s1", client_id: "biz1", titulo: "Mi estrategia", tipo: "semanal", estado: "active", created_at: "2026-06-01T00:00:00Z",
  contenido: { resumen: "R", pilares: [], posts_sugeridos: [
    { plataforma: "ig", idea: "ig-0" }, { plataforma: "ig", idea: "ig-1" }, { plataforma: "ig", idea: "ig-2" },
    { plataforma: "tt", idea: "tt-3" }, { plataforma: "tt", idea: "tt-4" }, { plataforma: "fb", idea: "fb-5" }] },
};

beforeAll(() => {
  Element.prototype.hasPointerCapture = vi.fn();
  Element.prototype.scrollIntoView = vi.fn();
});
beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("Fase C.1 · contador quedan + modal oculta usadas + tarjeta sin botones", () => {
  it("test_contador_quedan · 6 ideas, 1 usada → '5 de 6' (las que quedan, no '1 de 6')", () => {
    render(<StrategyCard strategy={STRAT6} variant="active" usedCount={1} />);
    expect(screen.getByText(/5 de 6/i)).toBeTruthy();
    expect(screen.queryByText(/1 de 6/i)).toBeNull();
  });

  it("test_modal_oculta_usada · idx 0 usado → el modal NO muestra ig-0 (solo las disponibles)", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={POSTS} usedIdxs={[0]} />);
    expect(screen.queryByText("ig-0")).toBeNull();    // la usada desaparece
    expect(screen.getByText("ig-1")).toBeTruthy();     // las disponibles siguen
    expect(screen.getByText("tt-2")).toBeTruthy();
  });

  it("test_modal_cuadro_vacio · todas las ideas de IG usadas → el cuadro Instagram no aparece", () => {
    render(<StrategyIdeaBoxes strategyId="s1" posts={POSTS} usedIdxs={[0, 1]} />);
    expect(screen.queryByText("Instagram")).toBeNull();   // cuadro IG vacio → no se renderiza
    expect(screen.getByText("TikTok")).toBeTruthy();        // TikTok queda
    expect(screen.getByText("tt-2")).toBeTruthy();
  });

  it("test_tarjeta_sin_botones · variant active → NO renderiza Usar/Ajuste/Archivar", () => {
    render(<StrategyCard strategy={STRAT6} variant="active" />);
    expect(screen.queryByRole("button", { name: /usar/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /ajuste/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /archivar/i })).toBeNull();
  });

  it("test_tarjeta_clic_modal · clic en la tarjeta activa → abre el modal con las ideas", () => {
    render(<StrategyCard strategy={STRAT6} variant="active" />);
    fireEvent.click(screen.getByText("Mi estrategia"));   // el titulo vive en el div clickable
    expect(screen.getByText("ig-0")).toBeTruthy();         // idea del modal → modal abierto
  });

  it("test_tarjeta_borde · la tarjeta activa tiene el borde amarillo", () => {
    const { container } = render(<StrategyCard strategy={STRAT6} variant="active" />);
    expect((container.firstChild as HTMLElement).className).toMatch(/border-yellow-500/);
  });
});
