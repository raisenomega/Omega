// @vitest-environment jsdom
// F.2 · wizard 2 pasos: Paso 1 (guion editable · visual_note OCULTO) → Paso 2 (render con el guion EDITADO).
// 🟡 Cubre la LÓGICA del wizard (mockea apiPost). El 🟢 es la prueba en vivo del owner (placas reales).
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement, type ReactNode } from "react";

class ObserverStub { observe() {} unobserve() {} disconnect() {} takeRecords() { return []; } }
vi.stubGlobal("ResizeObserver", ObserverStub);
vi.stubGlobal("matchMedia", (q: string) => ({
  matches: false, media: q, onchange: null, addEventListener: () => {},
  removeEventListener: () => {}, addListener: () => {}, removeListener: () => {}, dispatchEvent: () => false,
}));

vi.mock("@/lib/api-client", () => ({ apiPost: vi.fn() }));
import { apiPost } from "@/lib/api-client";
import { CarouselWizardModal } from "@/components/content/CarouselWizardModal";
import type { ResultV2 } from "@/components/content/result-types";

const SCRIPT = {
  carousel_title: "5 tips de ahorro",
  slides: [
    { order: 0, slide_type: "portada", text: "Tip uno", visual_note: "dark bg neon SECRET_ART_NOTE" },
    { order: 1, slide_type: "punto", text: "Tip dos", visual_note: "white bg" },
    { order: 2, slide_type: "cierre", text: "Tip tres", visual_note: "cta bg" },
  ],
};
const RENDER_RESP = { id: "draft1", content_type: "carousel", carousel_title: "5 tips de ahorro", media_urls: ["u0", "u1", "u2"] };

function wrapper({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
  return createElement(QueryClientProvider, { client: qc }, children);
}

beforeEach(() => {
  vi.mocked(apiPost).mockReset();
  vi.mocked(apiPost).mockImplementation((path: string) =>
    Promise.resolve(path.includes("carousel-script") ? SCRIPT : RENDER_RESP));
});
afterEach(cleanup);

describe("CarouselWizardModal · 2 pasos (F.2)", () => {
  it("Paso 1: muestra el text editable y NUNCA el visual_note (white-label)", async () => {
    render(<CarouselWizardModal open idea="ahorro" clientId="c1" onClose={() => {}} onGenerated={() => {}} />, { wrapper });
    expect(await screen.findByDisplayValue("Tip uno")).toBeTruthy();
    expect(screen.getByDisplayValue("Tip dos")).toBeTruthy();
    expect(screen.queryByText(/SECRET_ART_NOTE/)).toBeNull();        // visual_note nunca en la UI
    expect(screen.queryByDisplayValue(/dark bg neon/)).toBeNull();
  });

  it("Paso 2: manda el guion EDITADO (no el original) y devuelve un result carrusel a la grilla", async () => {
    let got: ResultV2 | null = null;
    render(<CarouselWizardModal open idea="ahorro" clientId="c1" onClose={() => {}} onGenerated={(r) => { got = r; }} />, { wrapper });
    const ta = await screen.findByDisplayValue("Tip uno");
    fireEvent.change(ta, { target: { value: "Tip uno EDITADO" } });
    fireEvent.click(screen.getByText("Generar placas"));
    await waitFor(() => expect(got).not.toBeNull());
    const renderCall = vi.mocked(apiPost).mock.calls.find(c => String(c[0]).includes("carousel-render"));
    expect(renderCall).toBeTruthy();
    const body = renderCall![1] as { slides: { text: string; visual_note: string }[] };
    expect(body.slides[0].text).toBe("Tip uno EDITADO");                 // edita el guion
    expect(body.slides[0].visual_note).toBe("dark bg neon SECRET_ART_NOTE"); // preserva la nota interna
    expect(got!.content_type).toBe("carousel");
    expect(got!.media_urls).toEqual(["u0", "u1", "u2"]);
  });

  it("test_checkbox_dispara_apply_logo · marcar 'Usar mi logo' → render con apply_logo=true (opt-in)", async () => {
    render(<CarouselWizardModal open idea="ahorro" clientId="c1" onClose={() => {}} onGenerated={() => {}} />, { wrapper });
    await screen.findByDisplayValue("Tip uno");
    fireEvent.click(screen.getByRole("checkbox"));            // opt-in "Usar mi logo"
    fireEvent.click(screen.getByText("Generar placas"));
    await waitFor(() => {
      const call = vi.mocked(apiPost).mock.calls.find(c => String(c[0]).includes("carousel-render"));
      expect(call).toBeTruthy();
      expect((call![1] as { apply_logo?: boolean }).apply_logo).toBe(true);
    });
  });

  it("sin marcar el checkbox → apply_logo=false (default · sin logo, como hoy)", async () => {
    render(<CarouselWizardModal open idea="ahorro" clientId="c1" onClose={() => {}} onGenerated={() => {}} />, { wrapper });
    await screen.findByDisplayValue("Tip uno");
    fireEvent.click(screen.getByText("Generar placas"));
    await waitFor(() => {
      const call = vi.mocked(apiPost).mock.calls.find(c => String(c[0]).includes("carousel-render"));
      expect(call).toBeTruthy();
      expect((call![1] as { apply_logo?: boolean }).apply_logo).toBe(false);
    });
  });
});
