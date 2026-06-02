// @vitest-environment jsdom
// toggle → variation_labels → label (DEBT-FRONTEND-TEST-GAP · Opción A).
import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

vi.mock("@/lib/api-client", () => ({ apiPost: vi.fn() }));
import { apiPost } from "@/lib/api-client";
import { useGenerateText } from "@/hooks/useGenerateText";
import type { FormState } from "@/components/content/ContentLabFormV2";

const FORM: FormState = {
  platform: "instagram", type: "caption", tone: "casual", topic: "x",
  braveQuery: "", clientId: "", aspect: "1:1", accountId: "",
};
const ITEM = (id: string, label: string) => ({
  id, label, temperature: 0.5, generated_text: `txt${label}`,
  virality_score: 1, virality_estimated: true, brand_dna_score: 0.5,
});
const respFor = (labels: string[]) => ({
  id: "r", content_type: "text", generated_text: "", virality_score: 0,
  virality_estimated: true, variations: labels.map(l => ITEM(l, l)),
});
function wrapper({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}
const labels = (out: { variation_label?: string }[]) => out.map(r => r.variation_label).sort();

beforeEach(() => {
  vi.mocked(apiPost).mockReset();
  // el backend (real) devuelve solo lo pedido → el mock lo espeja
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  vi.mocked(apiPost).mockImplementation((_p, body: any) => Promise.resolve(respFor(body.variation_labels)));
});

describe("ContentLab · Opción A (variation_labels)", () => {
  it("Test 1 · solo Atrevida → variation_labels:['C'] → 1 card 'Atrevida'", async () => {
    const { result } = renderHook(() => useGenerateText(), { wrapper });
    const out = await result.current.mutateAsync({ form: FORM, selectedLabels: ["Atrevida"] });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const body = vi.mocked(apiPost).mock.calls[0][1] as any;
    expect(body.variation_labels).toEqual(["C"]);
    expect(body).not.toHaveProperty("variations");          // limpieza
    expect(out).toHaveLength(1);
    expect(out[0].variation_label).toBe("Atrevida");
  });
  it("Test 2 · Conservadora + Atrevida → ['A','C'] → 2 cards correctas", async () => {
    const { result } = renderHook(() => useGenerateText(), { wrapper });
    const out = await result.current.mutateAsync({ form: FORM, selectedLabels: ["Conservadora", "Atrevida"] });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    expect((vi.mocked(apiPost).mock.calls[0][1] as any).variation_labels).toEqual(["A", "C"]);
    expect(labels(out)).toEqual(["Atrevida", "Conservadora"]);
  });
  it("Test 3 · las 3 → ['A','B','C'] → 3 cards", async () => {
    const { result } = renderHook(() => useGenerateText(), { wrapper });
    const out = await result.current.mutateAsync({ form: FORM, selectedLabels: ["Conservadora", "Balanceada", "Atrevida"] });
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    expect((vi.mocked(apiPost).mock.calls[0][1] as any).variation_labels).toEqual(["A", "B", "C"]);
    expect(labels(out)).toEqual(["Atrevida", "Balanceada", "Conservadora"]);
  });
});
