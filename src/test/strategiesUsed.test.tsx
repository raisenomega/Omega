// @vitest-environment jsdom
// Estrategias · vista "usadas" con chips de estado (Activas/Usadas/Archivadas · FilterChips).
// Resuelve el dolor: las estrategias que desaparecen al "Usar" se recuperan. Cero backend (el
// endpoint ya sirve estado=used · confirmado en la sonda). Una usada: badge "Usada" + used_at +
// solo "Usar" (re-usar, idempotente). Reemplaza el acordeon "Historial".
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";

const { listSpy, setStatusSpy } = vi.hoisted(() => ({ listSpy: vi.fn(), setStatusSpy: vi.fn() }));
const navigateSpy = vi.fn();

vi.mock("react-router-dom", () => ({ useNavigate: () => navigateSpy }));
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

  it("test_chip_usadas_query · click Usadas → useStrategiesList con estado='used'", () => {
    render(<Strategies />);
    fireEvent.click(chip(/usadas/i));
    expect(listSpy).toHaveBeenCalledWith("used");
  });

  it("test_card_usada_badge · una usada muestra badge 'Usada' + su used_at", () => {
    render(<Strategies />);
    fireEvent.click(chip(/usadas/i));
    expect(screen.getByText("Usada")).toBeTruthy();
    expect(screen.getByText(/10 jun/i)).toBeTruthy();           // used_at formateado (≠ created_at 01 jun)
  });

  it("test_card_usada_solo_usar · una usada muestra SOLO 'Usar' (no Ajuste/Archivar)", () => {
    render(<Strategies />);
    fireEvent.click(chip(/usadas/i));
    expect(screen.getByRole("button", { name: /^usar$/i })).toBeTruthy();
    expect(screen.queryByRole("button", { name: /ajuste/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /archivar/i })).toBeNull();
  });

  it("test_reusar · 'Usar' en una usada → re-navega a Content Lab (re-uso)", () => {
    render(<Strategies />);
    fireEvent.click(chip(/usadas/i));
    fireEvent.click(screen.getByRole("button", { name: /^usar$/i }));
    expect(navigateSpy).toHaveBeenCalledWith("/content-lab", { state: { brief: expect.stringContaining("T-used") } });
  });

  it("test_activas_intactas · 'Activas' (default) muestra activas con todas las acciones", () => {
    render(<Strategies />);
    expect(screen.getByText("T-active")).toBeTruthy();
    expect(screen.getByRole("button", { name: /^usar$/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /ajuste/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /archivar/i })).toBeTruthy();
  });

  it("test_archivadas_en_chip · 'Archivadas' las muestra (ya no en acordeon Historial)", () => {
    render(<Strategies />);
    expect(screen.queryByText(/Historial/i)).toBeNull();        // acordeon eliminado
    fireEvent.click(chip(/archivadas/i));
    expect(screen.getByText("T-archived")).toBeTruthy();
  });
});
