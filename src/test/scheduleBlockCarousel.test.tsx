// @vitest-environment jsdom
// F.3 · agendar el carrusel = mandar el ARRAY de N placas (no 1).
// Bug vivo que probó el owner: "la caja va sin las placas". Las placas mueren en
// useScheduleBlock (MEDIA_TYPES no incluye carousel → body sin media_urls) y el modal
// bloquea (hasMin exige media separada). Estos tests prueban ambos huecos (RED hoy).
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, render, waitFor, cleanup } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

vi.mock("@/lib/api-client", () => ({ apiPost: vi.fn(), apiGet: vi.fn() }));
import { apiPost } from "@/lib/api-client";
import { useScheduleBlock } from "@/hooks/useScheduleBlock";
import { ScheduleModalV2 } from "@/components/content/ScheduleModalV2";
import type { ResultV2, BlockState } from "@/components/content/result-types";

const mPost = apiPost as ReturnType<typeof vi.fn>;
const CAROUSEL: ResultV2 = {
  id: "car-1", content_type: "carousel", generated_text: "5 razones",
  media_urls: ["https://s/0.png", "https://s/1.png", "https://s/2.png"],
};

function wrap({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}

describe("useScheduleBlock · el carrusel manda el array de N placas (F.3)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("el body del POST incluye media_urls con las N placas (no 1 ni vacío)", async () => {
    mPost.mockResolvedValue([{ id: "p1", status: "scheduled" }]);
    const block: BlockState = { items: [CAROUSEL] };
    const { result } = renderHook(() => useScheduleBlock(), { wrapper: wrap });
    await result.current.mutateAsync({
      block, clientId: "c1", platform: "instagram", platforms: ["instagram"],
      scheduledAt: "2026-12-01T10:00",
    });
    await waitFor(() => expect(mPost).toHaveBeenCalled());
    const body = mPost.mock.calls[0][1] as Record<string, unknown>;
    expect(body.media_urls).toEqual(["https://s/0.png", "https://s/1.png", "https://s/2.png"]);
    expect(body.content_ids).toEqual(["car-1"]);  // el carrusel ES el content_id (su draft)
  });
});

afterEach(cleanup);
const noop = () => {};
function modalProps(block: BlockState) {
  return {
    state: "open" as const, block, scheduledAt: "", setScheduledAt: noop,
    onMinimize: noop, onRestore: noop, onClose: noop, onConfirm: noop, onRemoveItem: noop,
    connectedNetworks: ["instagram"], selectedPlatforms: ["instagram"], onTogglePlatform: noop,
  };
}

describe("ScheduleModalV2 · un bloque de solo-carrusel es agendable (F.3)", () => {
  it("hasMin = true con solo un carrusel → la fecha NO está deshabilitada", () => {
    const { container } = render(<ScheduleModalV2 {...modalProps({ items: [CAROUSEL] })} />);
    const dt = container.querySelector('input[type="datetime-local"]') as HTMLInputElement;
    expect(dt).toBeTruthy();
    expect(dt.disabled).toBe(false);   // hoy: disabled=true (mediaCount=0) → RED
  });

  it("el carrusel muestra preview (primera placa + badge N placas)", () => {
    const { container, getByText } = render(<ScheduleModalV2 {...modalProps({ items: [CAROUSEL] })} />);
    const img = container.querySelector('img[src="https://s/0.png"]');
    expect(img).toBeTruthy();              // primera placa visible (no el título como texto)
    expect(getByText(/3 placas/)).toBeTruthy();
  });
});
