// @vitest-environment jsdom
// Commit 1 del rediseño Calendario · extracción INVISIBLE de PostCard (hoy inline en PostsList:44-68).
// PostsList debe verse byte-por-byte igual: solo delega en <PostCard/>. Cero cambio visual, cero backend.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, cleanup, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

vi.mock("@/lib/api-client", () => ({ apiGet: vi.fn(), apiPatch: vi.fn(), apiPost: vi.fn() }));
vi.mock("@/contexts/ActiveBusinessContext", () => ({
  useActiveBusiness: () => ({ activeBusinessId: "biz-1", setActiveBusiness: vi.fn(), isReady: true }),
}));
import { apiPatch } from "@/lib/api-client";
import { PostCard } from "@/components/calendar/PostCard";
import { PostsList } from "@/components/calendar/PostsList";
import type { CalendarPost } from "@/hooks/useCalendarData";

const mPatch = apiPatch as ReturnType<typeof vi.fn>;
const base = { client_id: "biz-1", platform: "instagram", platform_post_id: null, error_message: null };
const PENDING: CalendarPost = { ...base, id: "p1", content_preview: "Mi post de prueba", scheduled_for: "2026-06-01T14:30:00Z", status: "pending" };
const PUBLISHED: CalendarPost = { ...base, id: "p2", content_preview: "Ya salió", scheduled_for: "2026-06-01T09:00:00Z", status: "published" };

function wrap({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("PostCard · extracción invisible (Commit 1)", () => {
  it("test_postcard_render · hora + platform + badge + preview", () => {
    const { getByText, container } = render(<PostCard post={PENDING} />, { wrapper: wrap });
    expect(container.textContent).toMatch(/\d{1,2}:\d{2}/);     // hora formateada
    expect(getByText("Instagram")).toBeTruthy();                 // label de plataforma
    expect(getByText("Programado")).toBeTruthy();                // badge de estado (pending)
    expect(getByText("Mi post de prueba")).toBeTruthy();         // preview del contenido
  });

  it("test_postcard_acciones · marcar publicado (Día/spacious) llama el mismo hook", async () => {
    mPatch.mockResolvedValue({});
    const { getByText } = render(<PostCard post={PENDING} variant="spacious" />, { wrapper: wrap });
    expect(getByText("Publicar Auto")).toBeTruthy();             // AutoPublishButton reusado
    fireEvent.click(getByText("Marcar como publicado"));
    await waitFor(() => expect(mPatch).toHaveBeenCalledWith("/calendar/p1/status", { status: "published_manual" }));
  });
  it("test_postcard_marcar_solo_spacious · 'Marcar como publicado' solo en Día (spacious)", () => {
    const compact = render(<PostCard post={PENDING} variant="compact" />, { wrapper: wrap });
    expect(compact.queryByText("Marcar como publicado")).toBeNull();   // Semana (compact): oculto
    expect(compact.getByText("Publicar Auto")).toBeTruthy();           // Publicar Auto sí queda
    cleanup();
    const spacious = render(<PostCard post={PENDING} variant="spacious" />, { wrapper: wrap });
    expect(spacious.getByText("Marcar como publicado")).toBeTruthy();  // Día (spacious): visible
  });

  it("test_postcard_published_sin_acciones · un post publicado NO muestra botones", () => {
    const { queryByText, getByText } = render(<PostCard post={PUBLISHED} />, { wrapper: wrap });
    expect(getByText("Publicado")).toBeTruthy();
    expect(queryByText("Marcar como publicado")).toBeNull();    // solo pending tiene acciones
    expect(queryByText("Publicar Auto")).toBeNull();
  });
});

describe("PostsList · delega en PostCard sin cambio visual (Commit 1)", () => {
  it("test_postslist_sin_cambio · renderiza la tarjeta vía PostCard (mismo output)", () => {
    const { getByText, container } = render(<PostsList day="2026-06-01" posts={[PENDING]} />, { wrapper: wrap });
    expect(getByText("Instagram")).toBeTruthy();
    expect(getByText("Programado")).toBeTruthy();
    expect(getByText("Mi post de prueba")).toBeTruthy();
    expect(container.querySelector(".max-h-\\[480px\\]")).toBeTruthy();   // el contenedor con scroll se conserva
  });

  it("test_postslist_estados_vacios · sin día / sin posts (intacto)", () => {
    const { getByText, rerender } = render(<PostsList day={null} posts={[]} />, { wrapper: wrap });
    expect(getByText("Selecciona un día del calendario")).toBeTruthy();
    rerender(<PostsList day="2026-06-01" posts={[]} />);
    expect(getByText("Sin posts programados")).toBeTruthy();
  });
});
