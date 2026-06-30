// @vitest-environment jsdom
// Estrategias Fase 1 · Commit A · tarjeta usada LIMPIA (solo el cuadro de lo usado · sin pilares)
// + boton "Archivar" en Usadas (reusa PATCH /status · el hook ya existe). SOLO frontend · cero
// backend. El fallback honesto (usada SIN last_used) mantiene resumen+pilares (CAPA 1 · no rompe).
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const navigateSpy = vi.fn();
vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
const setStatusSpy = vi.fn();
vi.mock("@/hooks/useStrategies", async (orig) => ({
  ...(await orig<typeof import("@/hooks/useStrategies")>()),
  useSetStrategyStatus: () => ({ mutate: setStatusSpy, isPending: false }),
}));
const recordUseSpy = vi.fn();
vi.mock("@/hooks/useRecordStrategyUse", () => ({ useRecordStrategyUse: () => ({ mutate: recordUseSpy }) }));
vi.mock("@/contexts/ARIAContext", () => ({ useARIA: () => ({ openARIAWith: vi.fn() }) }));

import { StrategyCard } from "@/components/strategies/StrategyCard";
import type { Strategy } from "@/hooks/useStrategies";

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

const base: Strategy = {
  id: "s1", client_id: "biz1", titulo: "Mi estrategia", tipo: "semanal", estado: "used",
  created_at: "2026-06-01T00:00:00Z", used_at: "2026-06-10T12:00:00Z",
  contenido: { resumen: "Resumen completo X", pilares: ["Pilar A", "Pilar B", "Pilar C"], posts_sugeridos: [] },
};
const usedWithDetail: Strategy = { ...base, last_used: { platform: "facebook", brief: "Lo que use en Facebook", at: "2026-06-10T12:00:00Z" } };
const usedOld: Strategy = { ...base, last_used: null };

describe("Estrategias Fase 1 · Commit A · tarjeta usada limpia + Archivar", () => {
  it("test_usada_solo_lo_usado · usada CON last_used → muestra last_used.brief, NO los pilares", () => {
    render(<StrategyCard strategy={usedWithDetail} variant="used" />);
    expect(screen.getByText("Lo que use en Facebook")).toBeTruthy();   // el cuadro de lo usado
    expect(screen.getByText(/Usaste \(Facebook\)/i)).toBeTruthy();      // label por red
    expect(screen.queryByText("Pilar A")).toBeNull();                  // SIN pilares
    expect(screen.queryByText("Pilar B")).toBeNull();
    expect(screen.queryByText("Resumen completo X")).toBeNull();        // SIN resumen completo
  });

  it("test_usada_vieja_fallback · usada SIN last_used → resumen + pilares (fallback · no rompe)", () => {
    render(<StrategyCard strategy={usedOld} variant="used" />);
    expect(screen.getByText("Resumen completo X")).toBeTruthy();        // fallback honesto CAPA 1
    expect(screen.getByText("Pilar A")).toBeTruthy();
    expect(screen.getByText("Pilar B")).toBeTruthy();
  });

  it("test_usada_boton_archivar · la rama used muestra 'Re-usar' + 'Archivar'", () => {
    render(<StrategyCard strategy={usedWithDetail} variant="used" />);
    expect(screen.getByRole("button", { name: /re-?usar/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /archivar/i })).toBeTruthy();
  });

  it("test_archivar_llama_status · click 'Archivar' → setStatus {id, estado:'archived'}", () => {
    render(<StrategyCard strategy={usedWithDetail} variant="used" />);
    fireEvent.click(screen.getByRole("button", { name: /archivar/i }));
    expect(setStatusSpy).toHaveBeenCalledWith({ id: "s1", estado: "archived" });
  });

  it("test_reusar_sigue · 'Re-usar' sigue navegando + registrando uso (cero regresion)", () => {
    render(<StrategyCard strategy={usedWithDetail} variant="used" />);
    fireEvent.click(screen.getByRole("button", { name: /re-?usar/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "Lo que use en Facebook", platform: "facebook" } });
    expect(recordUseSpy).toHaveBeenCalledWith({ id: "s1", platform: "facebook", brief: "Lo que use en Facebook", mark_used: true });
  });
});
