// @vitest-environment jsdom
// Commit 3 del rediseño Calendario · full-width + navegación Mes→Día + vista Día. Solo presentación
// + navegación de estado local · CERO backend · CERO funcionalidad nueva.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, cleanup, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

const navigate = vi.fn();
const setModeMutate = vi.fn();
vi.mock("react-router-dom", () => ({ useNavigate: () => navigate }));
vi.mock("@/lib/api-client", () => ({ apiGet: vi.fn(), apiPatch: vi.fn(), apiPost: vi.fn() }));
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
import { DayView } from "@/components/calendar/DayView";
import type { CalendarPost } from "@/hooks/useCalendarData";

const base = { client_id: "biz-1", platform: "instagram", platform_post_id: null, error_message: null };
const POSTS: CalendarPost[] = [
  { ...base, id: "p1", content_preview: "Post uno", scheduled_for: "2026-06-10T14:00:00Z", status: "pending" },
  { ...base, id: "p2", content_preview: "Post dos", scheduled_for: "2026-06-10T17:00:00Z", status: "published" },
];
function wrap({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}
beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("Calendar · full-width + navegación Mes→Día (Commit 3)", () => {
  it("test_mes_fullwidth · grid sin el panel lateral 'Selecciona un día'", () => {
    const { queryByText, container } = render(<Calendar />, { wrapper: wrap });
    expect(container.querySelector(".grid-cols-7")).toBeTruthy();              // grid del mes presente
    expect(queryByText("Selecciona un día del calendario")).toBeNull();        // panel lateral fuera del layout
    expect(container.querySelector(".md\\:grid-cols-3")).toBeNull();           // ya no hay 2-col
  });
  it("test_click_dia_abre_dia · click en un día → vista Día (view='day')", () => {
    const { container, getByText } = render(<Calendar />, { wrapper: wrap });
    fireEvent.click(container.querySelector("button.aspect-square") as HTMLElement);
    expect(getByText(/volver al mes/i)).toBeTruthy();                          // DayView montada
    expect(container.querySelector("button.aspect-square")).toBeNull();        // el grid del mes ya no está
  });
  it("test_rex_centrado · barra intacta · toggle sigue llamando setMode", () => {
    const { getByText, container } = render(<Calendar />, { wrapper: wrap });
    expect(getByText("Calendario")).toBeTruthy();
    expect(container.textContent).toMatch(/REX publica/);
    fireEvent.click(container.querySelector('[aria-label="Modo Autónomo"]') as HTMLElement);
    expect(setModeMutate).toHaveBeenCalled();
  });
  it("test_chips_siguen · click Semana cambia view (cae en mes en C3)", () => {
    const { getByText, container } = render(<Calendar />, { wrapper: wrap });
    fireEvent.click(getByText("Semana"));
    expect(getByText("Semana").className).toMatch(/border-primary/);
    expect(container.querySelector(".grid-cols-7")).toBeTruthy();              // Semana aún pinta el grid del mes
  });
});

describe("DayView · tarjetas desplegadas (Commit 3)", () => {
  it("test_dayview_tarjetas · PostCard spacious por cada post", () => {
    const { getByText, container } = render(<DayView day="2026-06-10" posts={POSTS} onBack={() => {}} />, { wrapper: wrap });
    expect(getByText("Post uno")).toBeTruthy();
    expect(getByText("Post dos")).toBeTruthy();
    expect(container.querySelector(".p-3")).toBeTruthy();                      // variant spacious (p-3)
  });
  it("test_dayview_volver · botón volver → onBack", () => {
    const onBack = vi.fn();
    const { getByText } = render(<DayView day="2026-06-10" posts={POSTS} onBack={onBack} />, { wrapper: wrap });
    fireEvent.click(getByText(/volver al mes/i));
    expect(onBack).toHaveBeenCalled();
  });
  it("test_dayview_empty · día sin posts → empty honesto (sin crash)", () => {
    const { getByText } = render(<DayView day="2026-06-10" posts={[]} onBack={() => {}} />, { wrapper: wrap });
    expect(getByText(/Sin posts ese día/i)).toBeTruthy();
  });
});
