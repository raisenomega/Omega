// @vitest-environment jsdom
// Commit 3 (Vía A) · picker de propiedad GA4 · HONESTO (P1): solo si Google está conectado · lista
// propiedades REALES · sin propiedades → mensaje claro (cero mock) · elegir → persiste el property_id.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

const mutate = vi.fn();
let propsData: { properties: { property_id: string; display_name: string }[] };
let loading = false;

vi.mock("@/hooks/useGoogleProperties", () => ({
  useGoogleProperties: () => ({ data: propsData, isLoading: loading }),
  useSetGoogleProperty: () => ({ mutate, isPending: false }),
}));
vi.mock("@/hooks/use-toast", () => ({ useToast: () => ({ toast: vi.fn() }) }));
import { GooglePropertyPicker } from "@/components/clients/GooglePropertyPicker";

function wrap(ui: ReactNode) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, ui);
}

describe("GooglePropertyPicker · honesto (cero mock · solo si conectado)", () => {
  beforeEach(() => { vi.clearAllMocks(); propsData = { properties: [] }; loading = false; });
  afterEach(() => cleanup());

  it("no conectado → no renderiza nada", () => {
    const { container } = render(wrap(<GooglePropertyPicker clientId="c1" connected={false} />));
    expect(container.textContent).toBe("");
  });

  it("conectado sin propiedades → mensaje honesto (sin select)", () => {
    render(wrap(<GooglePropertyPicker clientId="c1" connected={true} />));
    expect(screen.getByText(/No encontramos propiedades/i)).toBeTruthy();
    expect(screen.queryByRole("combobox")).toBeNull();
  });

  it("conectado con propiedades → opción + elegir dispara mutate(property_id)", () => {
    propsData = { properties: [{ property_id: "539450994", display_name: "Omega Raisen" }] };
    render(wrap(<GooglePropertyPicker clientId="c1" connected={true} />));
    expect(screen.getByText("Omega Raisen")).toBeTruthy();
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "539450994" } });
    expect(mutate).toHaveBeenCalledWith("539450994", expect.anything());
  });
});
