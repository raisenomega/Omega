// @vitest-environment jsdom
// H1 · el modal expandido del carrusel muestra las N placas + flechas prev/next (adelante Y atrás).
// 🟡 cubre que las flechas se renderizan. El 🟢 (navegar cambia la placa) es la prueba en vivo del owner
// (embla no mide layout en jsdom, así que el scroll real no se puede testear acá).
import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { ResultExpandedModal } from "@/components/content/ResultExpandedModal";
import type { ResultV2 } from "@/components/content/result-types";

class ObserverStub { observe() {} unobserve() {} disconnect() {} takeRecords() { return []; } }
vi.stubGlobal("ResizeObserver", ObserverStub);
vi.stubGlobal("IntersectionObserver", ObserverStub);
vi.stubGlobal("matchMedia", (q: string) => ({
  matches: false, media: q, onchange: null, addEventListener: () => {},
  removeEventListener: () => {}, addListener: () => {}, removeListener: () => {}, dispatchEvent: () => false,
}));

const noop = () => {};
const CAROUSEL: ResultV2 = {
  id: "c1", content_type: "carousel", generated_text: "5 tips",
  media_urls: ["https://s/0.png", "https://s/1.png", "https://s/2.png"],
};
afterEach(cleanup);

describe("ResultExpandedModal · carrusel navegable (H1)", () => {
  it("muestra las N placas y las flechas prev/next (adelante y atrás)", () => {
    render(<ResultExpandedModal result={CAROUSEL} onClose={noop} onAgendar={noop} onSave={noop} onDownload={noop} onCopy={noop} />);
    const imgs = screen.getAllByRole("img");
    expect(imgs).toHaveLength(3);
    expect(screen.getByText("Previous slide")).toBeTruthy();   // flecha atrás (sr-only · sí se renderiza)
    expect(screen.getByText("Next slide")).toBeTruthy();       // flecha adelante
  });

  it("la placa entra por ALTO del viewport (object-contain · sin scroll · no recorta)", () => {
    render(<ResultExpandedModal result={CAROUSEL} onClose={noop} onAgendar={noop} onSave={noop} onDownload={noop} onCopy={noop} />);
    const cls = screen.getAllByRole("img")[0].className;
    expect(cls).toContain("object-contain");   // ajusta al alto · NO recorta (object-cover) ni desborda
    expect(cls).toContain("max-h-[70vh]");
  });
});
