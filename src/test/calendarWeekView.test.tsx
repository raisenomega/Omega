// @vitest-environment jsdom
// Commit 4 del rediseño Calendario · vista SEMANA (7 columnas · reusa PostsList por columna).
// Flechas semana-a-semana · al cruzar mes setMonth al mes nuevo (mismo hook · cero backend).
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
import { WeekView } from "@/components/calendar/WeekView";
import { groupByDay, type CalendarPost } from "@/hooks/useCalendarData";

const base = { client_id: "biz-1", platform: "instagram", platform_post_id: null, error_message: null };
const todayIso = new Date().toISOString().slice(0, 10);
const POST_J10: CalendarPost = { ...base, id: "p1", content_preview: "Post del 10", scheduled_for: "2026-06-10T14:00:00Z", status: "published" };
const POST_HOY: CalendarPost = { ...base, id: "p2", content_preview: "Post de hoy", scheduled_for: `${todayIso}T12:00:00Z`, status: "published" };
function wrap({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}
beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("WeekView · 7 columnas (Commit 4)", () => {
  it("test_weekview_7_columnas · 7 columnas L→D con header", () => {
    const { container } = render(<WeekView anchorDay="2026-06-10" month="2026-06" setMonth={() => {}} grouped={new Map()} />, { wrapper: wrap });
    const grid = container.querySelector(".grid-cols-7")!;
    expect(grid.children.length).toBe(7);
    expect(grid.children[0].textContent?.startsWith("L")).toBe(true);
  });
  it("test_weekview_posts_por_dia · cada columna muestra los posts de SU día (reusa PostsList)", () => {
    const { getByText } = render(<WeekView anchorDay="2026-06-10" month="2026-06" setMonth={() => {}} grouped={groupByDay([POST_J10])} />, { wrapper: wrap });
    expect(getByText("Post del 10")).toBeTruthy();
  });
  it("test_weekview_ancla_selectedday · la semana mostrada contiene el día ancla", () => {
    const { getByText } = render(<WeekView anchorDay="2026-06-10" month="2026-06" setMonth={() => {}} grouped={groupByDay([POST_J10])} />, { wrapper: wrap });
    expect(getByText("Post del 10")).toBeTruthy();   // Jun 10 cae dentro de su propia semana
  });
  it("test_weekview_ancla_hoy · sin selectedDay → la semana de hoy", () => {
    const { getByText } = render(<WeekView anchorDay={todayIso} month={todayIso.slice(0, 7)} setMonth={() => {}} grouped={groupByDay([POST_HOY])} />, { wrapper: wrap });
    expect(getByText("Post de hoy")).toBeTruthy();
  });
  it("test_weekview_flecha_avanza · › avanza 7 días (cambia el rango)", () => {
    const { container, getByLabelText } = render(<WeekView anchorDay="2026-06-10" month="2026-06" setMonth={() => {}} grouped={new Map()} />, { wrapper: wrap });
    const before = container.querySelector(".grid-cols-7")!.children[0].textContent;
    fireEvent.click(getByLabelText("Semana siguiente"));
    expect(container.querySelector(".grid-cols-7")!.children[0].textContent).not.toBe(before);
  });
  it("test_weekview_flecha_cruza_mes · › que cruza a julio → setMonth('2026-07')", () => {
    const setMonth = vi.fn();
    const { getByLabelText } = render(<WeekView anchorDay="2026-06-30" month="2026-06" setMonth={setMonth} grouped={new Map()} />, { wrapper: wrap });
    fireEvent.click(getByLabelText("Semana siguiente"));
    expect(setMonth).toHaveBeenCalledWith("2026-07");
  });
});

describe("Calendar · chip Semana pinta WeekView (Commit 4)", () => {
  it("test_chip_semana_pinta_weekview · ya NO cae en Mes", () => {
    const { getByText, container } = render(<Calendar />, { wrapper: wrap });
    fireEvent.click(getByText("Semana"));
    expect(container.querySelector('[aria-label="Semana siguiente"]')).toBeTruthy();   // WeekView montada
    expect(container.querySelector('[aria-label="Mes anterior"]')).toBeNull();         // MonthView fuera
  });
});
