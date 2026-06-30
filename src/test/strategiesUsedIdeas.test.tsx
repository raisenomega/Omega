// @vitest-environment jsdom
// Fase B.2 · el chip "Usadas" muestra IDEAS SUELTAS (IdeaUsageCard desde useUsedIdeas), no
// estrategias. Activas/Archivadas siguen con StrategyCard (cero regresion). Cada idea: red + texto
// + "De: {titulo}" (fallback honesto si null · NO undefined) + Re-usar navega a Content Lab. Solo front.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const { listSpy, ideas } = vi.hoisted(() => ({ listSpy: vi.fn(), ideas: { current: [] as unknown[] } }));
const navigateSpy = vi.fn();

vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
vi.mock("@/contexts/ARIAContext", () => ({ useARIA: () => ({ openARIAWith: vi.fn() }) }));
vi.mock("@/hooks/useBehavioralTracking", () => ({ useTrackOnMount: () => {} }));
vi.mock("@/contexts/ActiveBusinessContext", () => ({ useActiveBusiness: () => ({ activeBusinessId: "biz1", isReady: true }) }));
vi.mock("@/hooks/useRecordStrategyUse", () => ({ useRecordStrategyUse: () => ({ mutate: vi.fn() }) }));
vi.mock("@/hooks/useUsedIdeas", () => ({ useUsedIdeas: () => ({ data: ideas.current, isLoading: false, isError: false }) }));
vi.mock("@/hooks/useStrategies", () => ({
  useStrategiesList: (estado: string) => {
    listSpy(estado);
    const items = estado === "active" ? [{ id: "a1", client_id: "biz1", titulo: "T-active", tipo: "semanal", estado: "active", created_at: "2026-06-01T00:00:00Z", contenido: { resumen: "R", pilares: [], posts_sugeridos: [] } }] : [];
    return { data: { items }, isLoading: false, isError: false, refetch: vi.fn() };
  },
  useGenerateStrategy: () => ({ mutate: vi.fn(), isPending: false }),
  useSetStrategyStatus: () => ({ mutate: vi.fn(), isPending: false }),
}));

import Strategies from "@/pages/Strategies";

const mkIdea = (extra = {}) => ({ id: "u1", strategy_id: "s1", client_id: "biz1", idea_idx: 0, platform: "instagram", brief: "texto de la idea", used_at: "2026-06-10T00:00:00Z", strategies: { titulo: "Mi estrategia" }, ...extra });

beforeEach(() => { vi.clearAllMocks(); ideas.current = []; });
afterEach(cleanup);

const chip = (name: RegExp) => screen.getByRole("button", { name });

describe("Estrategias Fase B.2 · Usadas = ideas sueltas", () => {
  it("test_usadas_muestra_ideas · chip Usadas → IdeaUsageCard (no StrategyCard)", () => {
    ideas.current = [mkIdea()];
    render(<Strategies />);
    fireEvent.click(chip(/usadas/i));
    expect(screen.getByText("texto de la idea")).toBeTruthy();
    expect(screen.queryByText("T-active")).toBeNull();          // no renderiza estrategias en Usadas
  });

  it("test_idea_card_contenido · red + texto + 'De: titulo'", () => {
    ideas.current = [mkIdea()];
    render(<Strategies />);
    fireEvent.click(chip(/usadas/i));
    expect(screen.getByText("Instagram")).toBeTruthy();
    expect(screen.getByText("texto de la idea")).toBeTruthy();
    expect(screen.getByText(/De:\s*Mi estrategia/i)).toBeTruthy();
  });

  it("test_idea_card_titulo_null · titulo null → fallback honesto (no undefined)", () => {
    ideas.current = [mkIdea({ strategies: null })];
    render(<Strategies />);
    fireEvent.click(chip(/usadas/i));
    expect(screen.queryByText(/undefined/i)).toBeNull();
    expect(screen.getByText(/estrategia eliminada/i)).toBeTruthy();
  });

  it("test_activas_intactas · chip Activas → StrategyCard sin botones (C.1)", () => {
    render(<Strategies />);
    expect(screen.getByText("T-active")).toBeTruthy();
    expect(screen.queryByRole("button", { name: /^usar$/i })).toBeNull();   // C.1 · tarjeta activa sin acciones
  });

  it("test_usadas_empty · sin ideas usadas → empty state honesto", () => {
    ideas.current = [];
    render(<Strategies />);
    fireEvent.click(chip(/usadas/i));
    expect(screen.getByText(/no has usado/i)).toBeTruthy();
  });

  it("test_reusar_navega · 'Re-usar' → navega a Content Lab con su brief", () => {
    ideas.current = [mkIdea()];
    render(<Strategies />);
    fireEvent.click(chip(/usadas/i));
    fireEvent.click(screen.getByRole("button", { name: /re-?usar/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: "texto de la idea", platform: "instagram" } });
  });
});
