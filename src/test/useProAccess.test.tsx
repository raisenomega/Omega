// @vitest-environment jsdom
// A2.2 · useProAccess gatea por el negocio ACTIVO (activeBusinessId), NO por el 1er cliente
// (useMyPlanStatus limit 1). Antes el badge del sidebar / gates de página leían el plan del
// negocio equivocado. Test: el clientId que llega a useClientPlanStatus = activeBusinessId.
import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

const seen: string[] = [];
vi.mock("@/contexts/ActiveBusinessContext", () => ({
  useActiveBusiness: () => ({ activeBusinessId: "active-biz", setActiveBusiness: vi.fn(), isReady: true }),
}));
vi.mock("@/hooks/useMyPlanStatus", () => ({
  useMyPlanStatus: () => ({ loading: false, isClient: true, isOwner: false, isSuperadmin: false, clientId: "first-biz" }),
}));
vi.mock("@/hooks/useClientPlanStatus", () => ({
  useClientPlanStatus: (clientId: string) => {
    seen.push(clientId);
    return { loading: false, planCode: "enterprise" };
  },
}));
vi.mock("@/integrations/supabase/client", () => ({
  supabase: { from: () => ({ select: () => ({ eq: () => ({ maybeSingle: async () => ({ data: null, error: null }) }) }) }) },
}));

import { useProAccess } from "@/hooks/useProAccess";

function wrap({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}

describe("useProAccess · gatea por negocio activo (A2.2)", () => {
  it("pasa activeBusinessId (no el 1er cliente) a useClientPlanStatus", () => {
    seen.length = 0;
    const { result } = renderHook(() => useProAccess(), { wrapper: wrap });
    expect(seen).toContain("active-biz");      // negocio activo
    expect(seen).not.toContain("first-biz");   // NUNCA el 1ero (bug viejo)
    expect(result.current.clientId).toBe("active-biz");
  });

  it("hasPro/hasBasic derivan del plan del negocio activo (enterprise → ambos true)", () => {
    const { result } = renderHook(() => useProAccess(), { wrapper: wrap });
    expect(result.current.hasPro).toBe(true);
    expect(result.current.hasBasic).toBe(true);
  });
});
