// @vitest-environment jsdom
// El carrusel = MEDIA (N placas = 1 imagen). caption + carrusel = 1 post (placas + caption descripción), igual
// que caption + imagen suelta. El texto dibujado en las placas NUNCA cuenta como texto. SIN guard/aviso.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, render, cleanup } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

class ObserverStub { observe() {} unobserve() {} disconnect() {} takeRecords() { return []; } }
vi.stubGlobal("ResizeObserver", ObserverStub);
vi.stubGlobal("matchMedia", (q: string) => ({
  matches: false, media: q, onchange: null, addEventListener: () => {},
  removeEventListener: () => {}, addListener: () => {}, removeListener: () => {}, dispatchEvent: () => false,
}));
vi.mock("@/lib/api-client", () => ({ apiPost: vi.fn(), apiGet: vi.fn() }));
import { apiPost } from "@/lib/api-client";
import { useScheduleBlock } from "@/hooks/useScheduleBlock";
import { ScheduleModalV2 } from "@/components/content/ScheduleModalV2";
import type { ResultV2, BlockState } from "@/components/content/result-types";

const mPost = apiPost as ReturnType<typeof vi.fn>;
const CAPTION: ResultV2 = { id: "cap-1", content_type: "text", generated_text: "Mi caption" };
const CAPTION2: ResultV2 = { id: "cap-2", content_type: "text", generated_text: "Otro caption" };
const PLACAS = ["https://s/0.png", "https://s/1.png", "https://s/2.png"];
const CAROUSEL: ResultV2 = { id: "car-1", content_type: "carousel", generated_text: "Título carrusel", media_urls: PLACAS };
const IMAGE: ResultV2 = { id: "img-1", content_type: "image", generated_text: "https://s/img.png" };

function wrap({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}
async function send(block: BlockState) {
  mPost.mockResolvedValue([{ id: "p1", status: "scheduled" }]);
  const { result } = renderHook(() => useScheduleBlock(), { wrapper: wrap });
  await result.current.mutateAsync({ block, clientId: "c1", platform: "instagram", platforms: ["instagram"], scheduledAt: "2026-12-01T10:00" });
  return mPost.mock.calls[0][1] as Record<string, unknown>;
}
beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe("useScheduleBlock · el carrusel = media (caption + carrusel = 1 post)", () => {
  it("test_caption_carrusel_1_post · [caption, carrusel] → content_ids=[caption] + media_urls=placas (1 post)", async () => {
    const body = await send({ items: [CAPTION, CAROUSEL] });
    expect(body.content_ids).toEqual(["cap-1"]);          // el carrusel NO es content_id (es media del caption)
    expect(body.media_urls).toEqual(PLACAS);              // las placas se cuelgan como media
    expect(body.media_url).toBe(PLACAS[0]);
  });
  it("test_carrusel_solo_intacto · [carrusel] → content_ids=[carrusel] + media_urls=placas (1 post · título)", async () => {
    const body = await send({ items: [CAROUSEL] });
    expect(body.content_ids).toEqual(["car-1"]);          // carrusel solo → se lleva a sí mismo (su título)
    expect(body.media_urls).toEqual(PLACAS);
  });
  it("test_caption_solo_intacto · [caption] → content_ids=[caption] sin media (post de texto)", async () => {
    const body = await send({ items: [CAPTION] });
    expect(body.content_ids).toEqual(["cap-1"]);
    expect(body.media_urls).toBeUndefined();
    expect(body.media_url).toBeNull();
  });
  it("test_caption_imagen_intacto · [caption, imagen] → content_ids=[caption] + media_url=imagen (intacto)", async () => {
    const body = await send({ items: [CAPTION, IMAGE] });
    expect(body.content_ids).toEqual(["cap-1"]);          // la imagen ya se excluía · intacto
    expect(body.media_url).toBe("https://s/img.png");
    expect(body.media_urls).toBeUndefined();
  });
  it("test_multi_caption_carrusel_como_imagen · [cap1, cap2, carrusel] = [cap1, cap2, imagen]", async () => {
    const conCarrusel = await send({ items: [CAPTION, CAPTION2, CAROUSEL] });
    expect(conCarrusel.content_ids).toEqual(["cap-1", "cap-2"]);   // ambos captions · carrusel = media (no pieza)
    expect(conCarrusel.media_urls).toEqual(PLACAS);
    vi.clearAllMocks();
    const conImagen = await send({ items: [CAPTION, CAPTION2, IMAGE] });
    expect(conImagen.content_ids).toEqual(["cap-1", "cap-2"]);     // mismo shape que la imagen (sin regla especial)
  });
});

function modalProps(block: BlockState) {
  const noop = () => {};
  return {
    state: "open" as const, block, scheduledAt: "", setScheduledAt: noop,
    onMinimize: noop, onRestore: noop, onClose: noop, onConfirm: noop, onRemoveItem: noop,
    connectedNetworks: ["instagram"], selectedPlatforms: ["instagram"], onTogglePlatform: noop,
  };
}

describe("ScheduleModalV2 · el carrusel cuenta como media, no texto", () => {
  it("test_conteo_carrusel_es_media · [caption, carrusel] → '1 publicación' (NO 2) · sin spread", () => {
    const { getByText, queryByText, container } = render(<ScheduleModalV2 {...modalProps({ items: [CAPTION, CAROUSEL] })} />);
    expect(getByText(/1 publicación/)).toBeTruthy();      // el carrusel NO infla el conteo
    expect(queryByText(/2 publicaciones/)).toBeNull();
    expect(queryByText(/Spread automático/)).toBeNull();  // 1 pieza de texto → sin spread
    expect((container.querySelector('input[type="datetime-local"]') as HTMLInputElement).disabled).toBe(false);
  });
  it("carrusel solo → Agendar habilitado (1 post · intacto)", () => {
    const { container } = render(<ScheduleModalV2 {...modalProps({ items: [CAROUSEL] })} />);
    expect((container.querySelector('input[type="datetime-local"]') as HTMLInputElement).disabled).toBe(false);
  });
});
