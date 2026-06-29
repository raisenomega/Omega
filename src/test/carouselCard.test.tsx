// @vitest-environment jsdom
// F.1 · la tarjeta de carrusel: N placas swipeables + caption del título + botón Agendar (no Copiar).
// CarouselPreview usa carousel.tsx (embla) → embla necesita ResizeObserver, que jsdom no trae → stub.
import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";

import { ResultCardV2 } from "@/components/content/ResultCardV2";
import type { ResultV2 } from "@/components/content/result-types";

class ObserverStub { observe() {} unobserve() {} disconnect() {} takeRecords() { return []; } }
vi.stubGlobal("ResizeObserver", ObserverStub);
vi.stubGlobal("IntersectionObserver", ObserverStub);
// embla (optionsMediaQueries) usa matchMedia · jsdom no lo trae y no hay setupFiles en config → stub.
vi.stubGlobal("matchMedia", (query: string) => ({
  matches: false, media: query, onchange: null,
  addEventListener: () => {}, removeEventListener: () => {},
  addListener: () => {}, removeListener: () => {}, dispatchEvent: () => false,
}));

const noop = () => {};
const CAROUSEL: ResultV2 = {
  id: "c1", content_type: "carousel", generated_text: "5 tips de ahorro",
  media_urls: ["https://s/0.png", "https://s/1.png", "https://s/2.png"],
};

function renderCard(result: ResultV2) {
  render(
    <ResultCardV2 result={result} onExpand={noop} onAgendar={noop} onSave={noop}
      onDownload={noop} onCopy={noop} onRemove={noop} />,
  );
}

afterEach(cleanup);

describe("ResultCardV2 · carrusel (F.1)", () => {
  it("renderiza las N placas como imágenes (swipeables)", () => {
    renderCard(CAROUSEL);
    const imgs = screen.getAllByRole("img");
    expect(imgs).toHaveLength(3);
    expect(imgs[0].getAttribute("src")).toBe("https://s/0.png");
  });

  it("muestra Agendar (no Copiar) para carrusel", () => {
    renderCard(CAROUSEL);
    expect(screen.getByText("Agendar")).toBeTruthy();   // carrusel en AGENDA_TYPES → se agenda
    expect(screen.queryByText("Copiar")).toBeNull();
  });

  it("muestra el caption (título) y la cuenta de placas", () => {
    renderCard(CAROUSEL);
    expect(screen.getByText("5 tips de ahorro")).toBeTruthy();
    expect(screen.getByText("3 placas")).toBeTruthy();
  });

  it("test_carousel_card_muestra_chips · virality + brand_dna → '🔥 XX/100', 'Estimado', '% voz de marca'", () => {
    renderCard({ ...CAROUSEL, virality_score: 64, virality_estimated: true, brand_dna_score: 0.73 });
    expect(screen.getByText(/64\/100/)).toBeTruthy();          // chip viral (reusa ResultCardV2, cero cambio)
    expect(screen.getByText("Estimado")).toBeTruthy();
    expect(screen.getByText(/73% voz de marca/)).toBeTruthy(); // brand_dna_score → % voz de marca
  });

  it("test_carousel_sin_score_no_rompe · sin virality/brand_dna → no pinta la fila de chips (como hoy)", () => {
    renderCard(CAROUSEL);  // sin los campos → undefined → 0
    expect(screen.queryByText(/\/100/)).toBeNull();
    expect(screen.queryByText("Estimado")).toBeNull();
    expect(screen.queryByText(/voz de marca/)).toBeNull();
  });
});
