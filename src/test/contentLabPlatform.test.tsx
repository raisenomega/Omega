// @vitest-environment jsdom
// Estrategias C3 · pre-seleccion de red en Content Lab. useContentLabState lee state.platform
// (ADITIVO): si viene una red valida del form -> el form arranca en esa red; si NO viene
// (entrada normal o desde "Usar") -> default de hoy (instagram). No rompe el flujo normal.
import { describe, it, expect, vi, afterEach } from "vitest";
import { renderHook, cleanup } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { createElement, type ReactNode } from "react";

// Sub-hooks inertes: aislamos la lectura de location.state (useLocation queda REAL via MemoryRouter).
vi.mock("@/hooks/use-toast", () => ({ useToast: () => ({ toast: vi.fn() }) }));
vi.mock("@/hooks/useGenerateText", () => ({ useGenerateText: () => ({ isPending: false, mutateAsync: vi.fn() }) }));
vi.mock("@/hooks/useGenerateImage", () => ({ useGenerateImage: () => ({ isPending: false, mutateAsync: vi.fn() }) }));
vi.mock("@/hooks/useVideoJobPolling", () => ({ useVideoJobPolling: () => ({ isPending: false, mutateAsync: vi.fn(), cancel: vi.fn() }) }));
vi.mock("@/hooks/useContentActions", () => ({ useSaveContent: () => ({ mutate: vi.fn() }) }));
vi.mock("@/hooks/useScheduleBlock", () => ({ useScheduleBlock: () => ({ isPending: false, mutateAsync: vi.fn() }), MAX_PIECES: 10 }));
vi.mock("@/hooks/useMyAccounts", () => ({ useConnectedNetworks: () => ({ data: [] }) }));
vi.mock("@/hooks/useResearch", () => ({ useResearch: () => ({ isPending: false, mutate: vi.fn() }) }));

import { useContentLabState } from "@/hooks/useContentLabState";

afterEach(cleanup);

function wrapWith(state: unknown) {
  return function Wrapper({ children }: { children: ReactNode }) {
    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    return createElement(
      MemoryRouter,
      { initialEntries: [{ pathname: "/content-lab", state }] },
      createElement(QueryClientProvider, { client: qc }, children),
    );
  };
}

describe("useContentLabState · pre-seleccion de red (C3)", () => {
  it("test_contentlab_lee_platform · state.platform=tiktok -> form arranca en tiktok", () => {
    const { result } = renderHook(() => useContentLabState("biz1"), { wrapper: wrapWith({ platform: "tiktok" }) });
    expect(result.current.form.platform).toBe("tiktok");
  });

  it("test_contentlab_sin_platform · sin platform -> default instagram (flujo normal intacto)", () => {
    const { result } = renderHook(() => useContentLabState("biz1"), { wrapper: wrapWith(null) });
    expect(result.current.form.platform).toBe("instagram");
  });

  it("test_contentlab_platform_invalido · red no soportada -> default (no fuerza valor invalido)", () => {
    const { result } = renderHook(() => useContentLabState("biz1"), { wrapper: wrapWith({ platform: "myspace" }) });
    expect(result.current.form.platform).toBe("instagram");
  });
});
