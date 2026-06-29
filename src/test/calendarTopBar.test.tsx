// @vitest-environment jsdom
// Commit 2 del rediseño Calendario · la barra superior en-línea con el título (molde PlanStatusBar):
// título + chips Mes/Semana/Día (FilterChips genérico · primary) + REX compacto + toggle. Solo
// presentación + mover el toggle · CERO backend · CERO cambio en la lógica de REX/toggle/datos.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, cleanup, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

const navigate = vi.fn();
const setModeMutate = vi.fn();
vi.mock("react-router-dom", () => ({ useNavigate: () => navigate }));
vi.mock("@/contexts/ActiveBusinessContext", () => ({
  useActiveBusiness: () => ({ activeBusinessId: "biz-1", isReady: true, setActiveBusiness: vi.fn() }),
}));
vi.mock("@/hooks/useBehavioralTracking", () => ({ useTrackOnMount: () => {} }));
vi.mock("@/hooks/useAutonomousMode", () => ({
  useAutonomousMode: () => ({ data: { rex_addon_active: true, autonomous_mode_on: false }, isLoading: false }),
  useSetAutonomousMode: () => ({ mutate: setModeMutate, isPending: false }),
}));
vi.mock("@/hooks/useCalendarData", async (orig) => {
  const actual = (await orig()) as Record<string, unknown>;
  return { ...actual, useCalendarList: () => ({ data: { items: [] }, isLoading: false, isError: false, refetch: vi.fn() }) };
});

import Calendar from "@/pages/Calendar";
import { FilterChips } from "@/components/ui/FilterChips";

const ITEMS = [{ id: "month", label: "Mes" }, { id: "week", label: "Semana" }, { id: "day", label: "Día" }];
function wrap({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}
beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("FilterChips · chip genérico oficial (primary)", () => {
  it("test_filterchips_render · activo=primary SÓLIDO · inactivo=muted", () => {
    const { getByText } = render(<FilterChips items={ITEMS} active="month" onSelect={() => {}} />);
    expect(getByText("Mes").className).toMatch(/border-primary/);
    expect(getByText("Mes").className).toMatch(/bg-primary/);                  // fondo primary sólido
    expect(getByText("Mes").className).toMatch(/text-primary-foreground/);     // texto sobre el sólido
    expect(getByText("Mes").className).not.toMatch(/bg-primary\/10/);          // ya NO es el translúcido
    expect(getByText("Semana").className).toMatch(/text-muted-foreground/);
  });
  it("test_filterchips_onselect · click → onSelect(id)", () => {
    const onSel = vi.fn();
    const { getByText } = render(<FilterChips items={ITEMS} active="month" onSelect={onSel} />);
    fireEvent.click(getByText("Semana"));
    expect(onSel).toHaveBeenCalledWith("week");
  });
});

describe("Calendar · la barra superior (Commit 2)", () => {
  it("test_calendar_barra · título + chips + REX + toggle en una fila", () => {
    const { getByText, container } = render(<Calendar />, { wrapper: wrap });
    expect(getByText("Calendario")).toBeTruthy();
    expect(getByText("Mes")).toBeTruthy();
    expect(getByText("Semana")).toBeTruthy();
    expect(getByText("Día")).toBeTruthy();
    expect(container.textContent).toMatch(/REX publica/);                       // REX compacto presente
    expect(container.querySelector('[aria-label="Modo Autónomo"]')).toBeTruthy(); // toggle movido a la barra
  });
  it("test_view_default_month · arranca en Mes · pinta el grid del mes (intacto)", () => {
    const { getByText, container } = render(<Calendar />, { wrapper: wrap });
    expect(getByText("Mes").className).toMatch(/border-primary/);               // Mes activo por default
    expect(container.querySelector(".grid-cols-7")).toBeTruthy();              // grid del mes renderizado
  });
  it("test_cambiar_vista · click Semana → view='week' (Mes se desactiva · cae en grid por ahora)", () => {
    const { getByText, container } = render(<Calendar />, { wrapper: wrap });
    fireEvent.click(getByText("Semana"));
    expect(getByText("Semana").className).toMatch(/border-primary/);           // Semana ahora activo
    expect(getByText("Mes").className).not.toMatch(/bg-primary\/10/);          // Mes inactivo
    expect(container.querySelector(".grid-cols-7")).toBeTruthy();             // sigue cayendo en el grid del mes
  });
  it("test_toggle_sigue_funcionando · el toggle movido sigue llamando setMode", () => {
    const { container } = render(<Calendar />, { wrapper: wrap });
    fireEvent.click(container.querySelector('[aria-label="Modo Autónomo"]') as HTMLElement);
    expect(setModeMutate).toHaveBeenCalled();
  });
});
