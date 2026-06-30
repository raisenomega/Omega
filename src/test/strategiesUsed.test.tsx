// @vitest-environment jsdom
// Estrategias · chips de estado (Activas/Usadas/Archivadas · FilterChips) + Activas/Archivadas con
// StrategyCard. ⚠️ La vista de Usadas (ahora IDEAS sueltas · Fase B.2) se prueba en
// strategiesUsedIdeas.test.tsx; aquí solo cubrimos los chips y que Activas/Archivadas no regresionen.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const { listSpy, setStatusSpy } = vi.hoisted(() => ({ listSpy: vi.fn(), setStatusSpy: vi.fn() }));
const navigateSpy = vi.fn();

vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
vi.mock("@/hooks/useRecordStrategyUse", () => ({ useRecordStrategyUse: () => ({ mutate: vi.fn() }) }));
vi.mock("@/hooks/useArchiveIdea", () => ({ useArchiveIdea: () => ({ mutate: vi.fn(), isPending: false }) }));
vi.mock("@/hooks/useUsedIdeas", () => ({ useUsedIdeas: () => ({ data: [], isLoading: false, isError: false, refetch: vi.fn() }) }));
vi.mock("@/contexts/ARIAContext", () => ({ useARIA: () => ({ openARIAWith: vi.fn() }) }));
vi.mock("@/hooks/useBehavioralTracking", () => ({ useTrackOnMount: () => {} }));
vi.mock("@/contexts/ActiveBusinessContext", () => ({
  useActiveBusiness: () => ({ activeBusinessId: "biz1", isReady: true }),
}));
vi.mock("@/hooks/useStrategies", () => {
  const mk = (id: string, estado: string, extra = {}) => ({
    id, client_id: "biz1", titulo: `T-${estado}`, tipo: "semanal", estado,
    created_at: "2026-06-01T00:00:00Z", contenido: { resumen: `R-${estado}`, pilares: [], posts_sugeridos: [] }, ...extra,
  });
  const DATA: Record<string, unknown[]> = {
    active: [mk("a1", "active")],
    used: [mk("u1", "used", { used_at: "2026-06-10T12:00:00Z" })],
    archived: [mk("ar1", "archived")],
  };
  return {
    useStrategiesList: (estado: string) => {
      listSpy(estado);
      return { data: { items: DATA[estado] ?? [], cadence: "semanal" }, isLoading: false, isError: false, refetch: vi.fn() };
    },
    useGenerateStrategy: () => ({ mutate: vi.fn(), isPending: false }),
    useSetStrategyStatus: () => ({ mutate: setStatusSpy, isPending: false }),
  };
});

import Strategies from "@/pages/Strategies";

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

const chip = (name: RegExp) => screen.getByRole("button", { name });

describe("Estrategias · chips de estado + vista usadas", () => {
  it("test_chips_estados · muestra los 3 chips Activas/Usadas/Archivadas", () => {
    render(<Strategies />);
    expect(chip(/activas/i)).toBeTruthy();
    expect(chip(/usadas/i)).toBeTruthy();
    expect(chip(/archivadas/i)).toBeTruthy();
  });

  it("test_activas_sin_botones · 'Activas' muestra la tarjeta SIN botones (C.1 · modelo idea-level)", () => {
    render(<Strategies />);
    expect(screen.getByText("T-active")).toBeTruthy();
    expect(screen.queryByRole("button", { name: /^usar$/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /ajuste/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /archivar/i })).toBeNull();
  });

  it("test_archivadas_ideas · 'Archivadas' ahora muestra IDEAS archivadas, no estrategias (C.2)", () => {
    render(<Strategies />);
    expect(screen.queryByText(/Historial/i)).toBeNull();        // acordeon eliminado
    fireEvent.click(chip(/archivadas/i));
    expect(screen.queryByText("T-archived")).toBeNull();        // ya no muestra estrategias archivadas
    expect(screen.getByText(/no hay ideas/i)).toBeTruthy();     // vista de ideas (mock vacio → empty)
  });
});
