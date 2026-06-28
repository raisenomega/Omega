// @vitest-environment jsdom
// COMMIT 3 · higiene de canasta: la X del modal (cerrar) limpia el bloque entero (items + fecha).
// Bug del owner: cerrar con X dejaba block.items vivo → la próxima pieza se sumaba al fantasma ("2 piezas").
// El reset vive en el handler handleCloseModal del hook (testeable) · la X por-item y minimizar NO cambian.
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import type { ResultV2 } from "@/components/content/result-types";

// El hook compone muchos sub-hooks de red/router · los mockeamos: solo probamos el estado local del bloque.
vi.mock("react-router-dom", () => ({ useLocation: () => ({ state: null }) }));
vi.mock("@/hooks/use-toast", () => ({ useToast: () => ({ toast: vi.fn() }) }));
vi.mock("@/hooks/useGenerateText", () => ({ useGenerateText: () => ({ mutateAsync: vi.fn(), isPending: false }) }));
vi.mock("@/hooks/useGenerateImage", () => ({ useGenerateImage: () => ({ mutateAsync: vi.fn(), isPending: false }) }));
vi.mock("@/hooks/useVideoJobPolling", () => ({ useVideoJobPolling: () => ({ mutateAsync: vi.fn(), isPending: false, cancel: vi.fn() }) }));
vi.mock("@/hooks/useContentActions", () => ({ useSaveContent: () => ({ mutate: vi.fn() }) }));
vi.mock("@/hooks/useMyAccounts", () => ({ useConnectedNetworks: () => ({ data: [] }) }));
vi.mock("@/hooks/useResearch", () => ({ useResearch: () => ({ mutate: vi.fn(), isPending: false }) }));
vi.mock("@/lib/content-lab-persistence", () => ({ loadPersistedResults: () => [], persistResults: vi.fn() }));
vi.mock("@/hooks/useScheduleBlock", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/hooks/useScheduleBlock")>();
  return { ...actual, useScheduleBlock: () => ({ mutateAsync: vi.fn(), isPending: false }) };
});

import { useContentLabState } from "@/hooks/useContentLabState";

const CAPTION: ResultV2 = { id: "cap-1", content_type: "text", generated_text: "caption viejo" };
const CARRUSEL: ResultV2 = { id: "car-1", content_type: "carousel", generated_text: "5 ventajas", media_urls: ["u1", "u2"] };
const PLACA_NUEVA: ResultV2 = { id: "car-2", content_type: "carousel", generated_text: "otra", media_urls: ["x1"] };

describe("Content Lab · la X del modal limpia el bloque (Commit 3)", () => {
  beforeEach(() => vi.clearAllMocks());

  it("test_X_modal_limpia_bloque · X → block.items vacío + scheduledAt limpio", () => {
    const { result } = renderHook(() => useContentLabState("biz1"));
    act(() => result.current.handleAgendar(CAPTION));
    act(() => result.current.handleAgendar(CARRUSEL));
    act(() => result.current.setScheduledAt("2026-12-01T10:00"));
    expect(result.current.block.items).toHaveLength(2);

    act(() => result.current.handleCloseModal());   // la X
    expect(result.current.block.items).toEqual([]);  // se fue TODO
    expect(result.current.scheduledAt).toBe("");
    expect(result.current.modalState).toBe("closed");
  });

  it("test_agendar_tras_X_empieza_limpio · X → agendar una placa → SOLO la placa (sin caption fantasma)", () => {
    const { result } = renderHook(() => useContentLabState("biz1"));
    act(() => result.current.handleAgendar(CAPTION));
    act(() => result.current.handleCloseModal());           // X (descarta el caption)
    act(() => result.current.handleAgendar(PLACA_NUEVA));   // nueva pieza
    expect(result.current.block.items).toEqual([PLACA_NUEVA]);  // cierra el bug: NO hay "2 piezas"
  });

  it("test_X_por_item_sigue_funcionando · quita solo su item (cero regresión)", () => {
    const { result } = renderHook(() => useContentLabState("biz1"));
    act(() => result.current.handleAgendar(CAPTION));
    act(() => result.current.handleAgendar(CARRUSEL));
    act(() => result.current.handleRemoveItem(0));   // quita el caption (índice 0)
    expect(result.current.block.items).toEqual([CARRUSEL]);  // queda el carrusel, limpio
  });

  it("test_minimizar_no_se_rompe · minimizar conserva el bloque (no lo limpia)", () => {
    const { result } = renderHook(() => useContentLabState("biz1"));
    act(() => result.current.handleAgendar(CAPTION));
    act(() => result.current.setModalState("minimized"));
    expect(result.current.modalState).toBe("minimized");
    expect(result.current.block.items).toHaveLength(1);  // minimizar NO descarta
  });
});
